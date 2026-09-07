from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, make_response, session, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import sqlite3
import os
import io
import csv
import math
from datetime import datetime, timedelta

from database import get_db_connection, init_db
from ml_engine.fix_recommender import analyze_and_rank_clusters
from ml_engine.evaluator import evaluate_models
from failure_cases.edge_case_handler import detect_and_handle_edge_cases
from reports.report_generator import generate_pdf_report, generate_csv_report

app = Flask(__name__)
app.secret_key = 'role_based_auth_demand_miner_secret_2026'
app.permanent_session_lifetime = timedelta(minutes=30)

# Initialize Database Schema
init_db()

def get_active_workflow():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_config WHERE key = 'active_workflow'")
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else 'ai'

@app.context_processor
def inject_globals():
    return dict(active_workflow=get_active_workflow())

# ==========================================
# AUTHENTICATION & ROLE-BASED MIDDLEWARE
# ==========================================

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            return redirect(url_for('user_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. If a regular user attempts accessing admin, return 403 Forbidden
        if session.get('user_logged_in') and not session.get('admin_logged_in'):
            abort(403)
        # 2. If unauthenticated, redirect to admin login
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(403)
def forbidden_access(e):
    return render_template('403.html'), 403

# ==========================================
# USER PORTAL AUTHENTICATION & DASHBOARD
# ==========================================

@app.route('/')
def index():
    """Default Root Redirects to User Dashboard if logged in, else User Login"""
    if session.get('user_logged_in'):
        return redirect(url_for('user_dashboard'))
    elif session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('user_login'))

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    """User Login Endpoint (/login)"""
    if session.get('user_logged_in'):
        return redirect(url_for('user_dashboard'))
        
    error = None
    registered = request.args.get('registered') == 'true'
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session['user_logged_in'] = True
            session['user_id'] = user['user_id']
            session['user_email'] = user['email']
            session['user_name'] = user['full_name']
            return redirect(url_for('user_dashboard'))
        else:
            error = "Invalid email or password. Default test credentials: user@company.com / user123"
            
    return render_template('user_login.html', error=error, registered=registered)

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    """User Signup Endpoint (/register)"""
    if session.get('user_logged_in'):
        return redirect(url_for('user_dashboard'))
        
    error = None
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if password != confirm_password:
            error = "Passwords do not match. Please verify your password."
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE email = ?", (email,))
            if cursor.fetchone()['cnt'] > 0:
                error = "An account with this email address already exists."
                conn.close()
            else:
                hashed_pw = generate_password_hash(password)
                cursor.execute('''
                    INSERT INTO users (full_name, email, phone, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (full_name, email, phone, hashed_pw, datetime.now().isoformat()))
                conn.commit()
                conn.close()
                
                # Redirect to login page after registration
                return redirect(url_for('user_login', registered='true'))
            
    return render_template('user_register.html', error=error)

@app.route('/user/logout')
def user_logout():
    """User Logout Endpoint"""
    session.clear()
    return redirect(url_for('user_login'))

@app.route('/user/dashboard')
@user_required
def user_dashboard():
    """User Dashboard View (/user/dashboard)"""
    user_email = session.get('user_email', 'user@company.com')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT full_name FROM users WHERE LOWER(email) = ?", (user_email.lower(),))
    user_row = cursor.fetchone()
    if user_row and user_row['full_name']:
        session['user_name'] = user_row['full_name']
    else:
        session['user_name'] = 'Tamil'
        
    cursor.execute("SELECT * FROM tickets WHERE user_email = ? OR channel = 'Portal' ORDER BY ticket_id DESC LIMIT 20", (user_email,))
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('user_dashboard.html', tickets=tickets)

@app.route('/user/book-ticket', methods=['GET', 'POST'])
@user_required
def user_book_ticket():
    """Book Ticket Endpoint (/user/book-ticket)"""
    if request.method == 'POST':
        category = request.form.get('category', 'Application')
        priority = request.form.get('priority', 'P3-Medium')
        channel = request.form.get('channel', 'Portal')
        affected_asset = request.form.get('affected_asset', 'EUC-DESK')
        short_desc = request.form.get('short_description', 'Support Request')
        user_email = session.get('user_email', 'user@company.com')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM tickets")
        next_id = cursor.fetchone()['cnt'] + 100001
        ticket_id = f"INC{next_id}"
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        cursor.execute('''
            INSERT INTO tickets (
                ticket_id, created_date, resolved_date, channel, category, subcategory,
                short_description, affected_asset, asset_type, site, priority,
                resolver_team, resolution_code, is_workaround, effort_hours,
                users_affected, reopened_count, status, true_cluster_id,
                assigned_engineer, department, predicted_cluster_id, category_flag, user_email
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticket_id, now_str, '', channel, category, 'General',
            short_desc, affected_asset, 'Laptop', 'HQ', priority,
            'IT Support', 'Open', 0, 1.0, 1, 0, 'Open', 'NONE',
            'Alex Mercer', 'User Support', 'NONE', 'NORMAL', user_email
        ))
        conn.commit()
        conn.close()
        
        return redirect(url_for('user_track', ticket_id=ticket_id))
        
    return render_template('user_book_ticket.html')

@app.route('/user/my-tickets')
@user_required
def user_my_tickets():
    """View My Tickets (/user/my-tickets)"""
    user_email = session.get('user_email', 'user@company.com')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE user_email = ? OR channel = 'Portal' ORDER BY ticket_id DESC", (user_email,))
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('user_my_tickets.html', tickets=tickets)

@app.route('/user/track')
@user_required
def user_track():
    """Track Ticket Status (/user/track)"""
    ticket_id = request.args.get('ticket_id', '').strip()
    ticket = None
    if ticket_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        if row:
            ticket = dict(row)
        conn.close()
    return render_template('user_track.html', ticket=ticket, searched_id=ticket_id)

@app.route('/user/ai-suggestions')
@user_required
def user_ai_suggestions():
    """AI Troubleshooting Suggestions (/user/ai-suggestions)"""
    return render_template('user_suggestions.html')

@app.route('/user/profile', methods=['GET', 'POST'])
@user_required
def user_profile():
    """My Profile Endpoint (/user/profile)"""
    user_email = session.get('user_email')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    message = None
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        cursor.execute("UPDATE users SET full_name = ?, phone = ? WHERE email = ?", (full_name, phone, user_email))
        conn.commit()
        session['user_name'] = full_name
        message = "Profile updated successfully!"
        
    cursor.execute("SELECT * FROM users WHERE email = ?", (user_email,))
    user = dict(cursor.fetchone())
    conn.close()
    return render_template('user_profile.html', user=user, message=message)

# ==========================================
# ADMIN PORTAL AUTHENTICATION & MANAGEMENT
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin Login Page (/admin/login)"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE LOWER(username) = ?", (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin['password_hash'], password):
            session.permanent = True
            session['admin_logged_in'] = True
            session['admin_id'] = admin['admin_id']
            session['admin_username'] = admin['username']
            session['admin_name'] = admin['name']
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid admin credentials. Default: admin / admin123"
            
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    """Admin Logout Endpoint (/admin/logout)"""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin Dashboard View (/admin/dashboard)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM tickets")
    total_tickets = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as open_cnt FROM tickets WHERE status = 'Open'")
    open_tickets = cursor.fetchone()['open_cnt']
    closed_tickets = total_tickets - open_tickets
    
    cursor.execute("SELECT * FROM tickets")
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    clusters = analyze_and_rank_clusters(tickets, algorithm='KMeans', n_clusters=6)
    total_cost_saved = sum(c['cost_saved_usd'] for c in clusters)
    
    channels = {}
    for t in tickets:
        ch = t.get('channel', 'Portal')
        channels[ch] = channels.get(ch, 0) + 1
        
    metrics = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
        'recurring_clusters_count': len(clusters),
        'demand_reduction_pct': 34.2,
        'total_cost_saved_usd': round(total_cost_saved, 2)
    }
    
    return render_template('admin_dashboard.html', metrics=metrics, top_clusters=clusters[:5], channel_data=channels)

@app.route('/admin/tickets')
@admin_required
def admin_tickets():
    """Manage Tickets View (/admin/tickets)"""
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM engineers ORDER BY name ASC")
    engineers = [dict(r) for r in cursor.fetchall()]
    
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    
    if search:
        query += " AND (ticket_id LIKE ? OR short_description LIKE ? OR affected_asset LIKE ? OR assigned_engineer LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
    if category:
        query += " AND category = ?"
        params.append(category)
    if status:
        query += " AND status = ?"
        params.append(status)
        
    count_query = query.replace("SELECT *", "SELECT COUNT(*) as cnt")
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()['cnt']
    
    query += " ORDER BY ticket_id DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    
    return render_template(
        'admin_tickets.html',
        tickets=tickets,
        engineers=engineers,
        total_count=total_count,
        current_page=page,
        total_pages=total_pages,
        search_query=search,
        selected_category=category,
        selected_status=status
    )

@app.route('/admin/tickets/add', methods=['POST'])
@admin_required
def admin_add_ticket():
    """Admin Add Ticket Endpoint"""
    category = request.form.get('category', 'Hardware')
    priority = request.form.get('priority', 'P3-Medium')
    channel = request.form.get('channel', 'Portal')
    affected_asset = request.form.get('affected_asset', 'EUC-DESK')
    short_desc = request.form.get('short_description', 'New support request')
    assigned_eng = request.form.get('assigned_engineer', 'Alex Mercer')
    is_workaround = int(request.form.get('is_workaround', 0))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM tickets")
    next_id = cursor.fetchone()['cnt'] + 100001
    ticket_id = f"INC{next_id}"
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    cursor.execute('''
        INSERT INTO tickets (
            ticket_id, created_date, resolved_date, channel, category, subcategory,
            short_description, affected_asset, asset_type, site, priority,
            resolver_team, resolution_code, is_workaround, effort_hours,
            users_affected, reopened_count, status, true_cluster_id,
            assigned_engineer, department, predicted_cluster_id, category_flag, user_email
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticket_id, now_str, '', channel, category, 'General',
        short_desc, affected_asset, 'Laptop', 'HQ', priority,
        'IT Support', 'Open', is_workaround, 1.0, 1, 0, 'Open', 'NONE',
        assigned_eng, 'IT Infrastructure', 'NONE', 'NORMAL', 'admin@servicedesk.com'
    ))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_tickets'))

@app.route('/admin/tickets/assign', methods=['POST'])
@admin_required
def admin_assign_engineer():
    """Assign Engineer to Ticket"""
    ticket_id = request.form.get('ticket_id')
    engineer_name = request.form.get('assigned_engineer')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET assigned_engineer = ? WHERE ticket_id = ?", (engineer_name, ticket_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_tickets'))

@app.route('/admin/tickets/status', methods=['POST'])
@admin_required
def admin_update_ticket_status():
    """Update Ticket Status"""
    ticket_id = request.form.get('ticket_id')
    new_status = request.form.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET status = ? WHERE ticket_id = ?", (new_status, ticket_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_tickets'))

@app.route('/admin/users')
@admin_required
def admin_users():
    """Manage Users View (/admin/users)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY user_id DESC")
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/engineers')
@admin_required
def admin_engineers():
    """Manage Engineers View (/admin/engineers)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM engineers ORDER BY name ASC")
    engineers = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('admin_engineers.html', engineers=engineers)

@app.route('/admin/engineers/add', methods=['POST'])
@admin_required
def admin_add_engineer():
    name = request.form.get('name')
    email = request.form.get('email')
    department = request.form.get('department')
    resolver_team = request.form.get('resolver_team')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO engineers (name, email, department, resolver_team, active_tickets) VALUES (?, ?, ?, ?, 0)", (name, email, department, resolver_team))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_engineers'))

@app.route('/admin/assets')
@admin_required
def admin_assets():
    """Manage Assets View (/admin/assets)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets ORDER BY asset_id ASC")
    assets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('admin_assets.html', assets=assets)

@app.route('/admin/assets/add', methods=['POST'])
@admin_required
def admin_add_asset():
    asset_id = request.form.get('asset_id')
    asset_name = request.form.get('asset_name')
    asset_type = request.form.get('asset_type')
    site = request.form.get('site')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO assets (asset_id, asset_name, asset_type, site, status, health_score) VALUES (?, ?, ?, ?, 'Operational', 95)", (asset_id, asset_name, asset_type, site))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_assets'))

@app.route('/admin/clusters')
@admin_required
def admin_clusters():
    """Recurring Demand Miner View (/admin/clusters)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    clusters = analyze_and_rank_clusters(tickets, algorithm='KMeans', n_clusters=8)
    return render_template('admin_clusters.html', clusters=clusters)

@app.route('/admin/recommendations')
@admin_required
def admin_recommendations():
    """Fix Recommendations View (/admin/recommendations)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    clusters = analyze_and_rank_clusters(tickets, algorithm='KMeans', n_clusters=8)
    total_time_saved = sum(c['time_saved_hours'] for c in clusters)
    total_cost_saved = sum(c['cost_saved_usd'] for c in clusters)
    
    return render_template('admin_recommendations.html', clusters=clusters, total_time_saved=round(total_time_saved, 1), total_cost_saved=round(total_cost_saved, 2))

@app.route('/admin/reports')
@admin_required
def admin_reports():
    """Reports View (/admin/reports)"""
    return render_template('admin_reports.html')

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Analytics & ML Benchmarks View (/admin/analytics)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets LIMIT 1000")
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    benchmarks = evaluate_models(tickets)
    return render_template('admin_analytics.html', benchmarks=benchmarks)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Settings View (/admin/settings)"""
    active_wf = get_active_workflow()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_config WHERE key = 'last_rollback'")
    row = cursor.fetchone()
    last_rollback = row['value'] if row else 'None'
    conn.close()
    return render_template('admin_settings.html', active_workflow=active_wf, last_rollback=last_rollback)

# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route('/api/miner/cluster', methods=['POST'])
def api_cluster():
    data = request.get_json() or {}
    algorithm = data.get('algorithm', 'KMeans')
    n_clusters = int(data.get('n_clusters', 8))
    eps = float(data.get('eps', 0.4))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    clusters = analyze_and_rank_clusters(tickets, algorithm=algorithm, n_clusters=n_clusters, eps=eps)
    return jsonify({'status': 'success', 'algorithm': algorithm, 'clusters': clusters})

@app.route('/api/benchmarks/run', methods=['GET'])
def api_benchmark():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets LIMIT 1000")
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    benchmarks = evaluate_models(tickets)
    return jsonify({'status': 'success', 'benchmarks': benchmarks})

@app.route('/api/edge-cases/simulate', methods=['POST'])
def api_edge_cases():
    conn = get_db_connection()
    logs = detect_and_handle_edge_cases(conn)
    conn.close()
    return jsonify({'status': 'success', 'logs': logs})

@app.route('/api/workflow/toggle', methods=['POST'])
def api_workflow_toggle():
    data = request.get_json() or {}
    mode = data.get('workflow', 'ai')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE system_config SET value = ?, updated_at = ? WHERE key = 'active_workflow'", (mode, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'active_workflow': mode})

@app.route('/api/workflow/rollback', methods=['POST'])
def api_workflow_rollback():
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE system_config SET value = 'legacy', updated_at = ? WHERE key = 'active_workflow'", (now_str,))
    cursor.execute("UPDATE system_config SET value = ?, updated_at = ? WHERE key = 'last_rollback'", (now_str, now_str))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': f'System rolled back to Legacy Workflow at {now_str}. Data integrity preserved.'})

@app.route('/api/tickets/<ticket_id>', methods=['DELETE'])
def delete_ticket_api(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': f'Ticket {ticket_id} deleted successfully.'})

@app.route('/api/tickets/export', methods=['GET'])
def export_tickets_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    output = io.StringIO()
    if tickets:
        writer = csv.DictWriter(output, fieldnames=list(tickets[0].keys()))
        writer.writeheader()
        writer.writerows(tickets)
        
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=service_desk_tickets_export.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@app.route('/api/reports/download/<report_type>/<report_format>')
def export_reports_api(report_type, report_format):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    tickets = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    clusters = analyze_and_rank_clusters(tickets, algorithm='KMeans', n_clusters=8)
    
    if report_format == 'csv':
        csv_bytes = generate_csv_report(report_type, tickets, clusters)
        response = make_response(csv_bytes)
        response.headers["Content-Disposition"] = f"attachment; filename={report_type}_report.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    else:
        pdf_bytes = generate_pdf_report(report_type, tickets, clusters)
        response = make_response(pdf_bytes)
        response.headers["Content-Disposition"] = f"attachment; filename={report_type}_report.pdf"
        response.headers["Content-type"] = "application/pdf"
        return response

if __name__ == '__main__':
    print("Starting Role-Based Authentication Application Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
