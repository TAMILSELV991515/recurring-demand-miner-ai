import sqlite3
import os
import csv
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'demand_miner.db')
CSV_PATH = os.path.join(os.path.dirname(__file__), 'service_desk_tickets.csv')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            created_date TEXT,
            resolved_date TEXT,
            channel TEXT,
            category TEXT,
            subcategory TEXT,
            short_description TEXT,
            affected_asset TEXT,
            asset_type TEXT,
            site TEXT,
            priority TEXT,
            resolver_team TEXT,
            resolution_code TEXT,
            is_workaround INTEGER DEFAULT 0,
            effort_hours REAL DEFAULT 0.0,
            users_affected INTEGER DEFAULT 1,
            reopened_count INTEGER DEFAULT 0,
            status TEXT,
            true_cluster_id TEXT DEFAULT 'NONE',
            assigned_engineer TEXT DEFAULT 'Unassigned',
            department TEXT DEFAULT 'IT Operations',
            predicted_cluster_id TEXT DEFAULT 'NONE',
            category_flag TEXT DEFAULT 'NORMAL',
            user_email TEXT DEFAULT 'user@company.com'
        )
    ''')
    
    # 2. Clusters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clusters (
            cluster_id TEXT PRIMARY KEY,
            cluster_name TEXT,
            issue_description TEXT,
            category TEXT,
            ticket_count INTEGER,
            avg_resolution_time_hrs REAL,
            total_effort_hours REAL,
            workaround_freq_pct REAL,
            affected_assets TEXT,
            recurrence_interval_days REAL,
            estimated_business_impact TEXT,
            confidence_score REAL,
            recommended_fix TEXT,
            priority_score REAL,
            expected_ticket_reduction_pct REAL,
            time_saved_hours REAL,
            cost_saved_usd REAL,
            algorithm_used TEXT DEFAULT 'KMeans'
        )
    ''')
    
    # 3. Stakeholder Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stakeholder_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_name TEXT,
            cluster_id TEXT,
            issue_correct INTEGER,
            recommendation_useful INTEGER,
            approve_fix INTEGER,
            satisfaction_rating INTEGER,
            comments TEXT,
            created_at TEXT
        )
    ''')
    
    # 4. System Config table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    ''')
    
    # 5. Edge Case Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edge_case_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT,
            case_type TEXT,
            description TEXT,
            action_taken TEXT,
            status TEXT,
            timestamp TEXT
        )
    ''')

    # 6. Users Table (NEW)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT DEFAULT '',
            password_hash TEXT NOT NULL,
            created_at TEXT
        )
    ''')

    # 7. Admins Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'Administrator',
            created_at TEXT
        )
    ''')

    # 8. Engineers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engineers (
            engineer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            resolver_team TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            active_tickets INTEGER DEFAULT 0
        )
    ''')

    # 9. Assets Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            asset_id TEXT PRIMARY KEY,
            asset_name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            site TEXT NOT NULL,
            status TEXT DEFAULT 'Operational',
            health_score INTEGER DEFAULT 95
        )
    ''')
    
    # Default system config
    cursor.execute("INSERT OR IGNORE INTO system_config (key, value, updated_at) VALUES ('active_workflow', 'ai', ?)", (datetime.now().isoformat(),))
    cursor.execute("INSERT OR IGNORE INTO system_config (key, value, updated_at) VALUES ('last_rollback', 'None', ?)", (datetime.now().isoformat(),))
    
    # Seed default user (email: user@company.com, password: user123)
    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE email = 'user@company.com'")
    if cursor.fetchone()['cnt'] == 0:
        hashed_user_pw = generate_password_hash('user123')
        cursor.execute('''
            INSERT INTO users (full_name, email, phone, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Tamil', 'user@company.com', '+1 (555) 019-2831', hashed_user_pw, datetime.now().isoformat()))
    else:
        cursor.execute("UPDATE users SET full_name = 'Tamil' WHERE email = 'user@company.com'")

    # Seed default admin (username: admin, password: admin123)
    cursor.execute("SELECT COUNT(*) as cnt FROM admins WHERE username = 'admin'")
    if cursor.fetchone()['cnt'] == 0:
        hashed_admin_pw = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, name, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hashed_admin_pw, 'System Administrator', 'Super Admin', datetime.now().isoformat()))

    # Seed engineers if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM engineers")
    if cursor.fetchone()['cnt'] == 0:
        engineers_data = [
            ('Alex Mercer', 'alex.mercer@servicedesk.com', 'End User Compute', 'Field Support', 5),
            ('Sarah Connor', 'sarah.connor@servicedesk.com', 'Identity & Access', 'Access Team', 3),
            ('David Miller', 'david.miller@servicedesk.com', 'Applications', 'App Support', 7),
            ('Elena Rostova', 'elena.rostova@servicedesk.com', 'End User Compute', 'Field Support', 4),
            ('James Holden', 'james.holden@servicedesk.com', 'Network Ops', 'Network Team', 2),
            ('Priya Sharma', 'priya.sharma@servicedesk.com', 'Database Ops', 'App Support', 6),
            ('Marcus Vance', 'marcus.vance@servicedesk.com', 'Server Ops', 'Server Support', 4)
        ]
        cursor.executemany('''
            INSERT INTO engineers (name, email, department, resolver_team, active_tickets)
            VALUES (?, ?, ?, ?, ?)
        ''', engineers_data)

    # Seed assets if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM assets")
    if cursor.fetchone()['cnt'] == 0:
        assets_data = [
            ('PRT-F2-HQ', 'HQ Floor 2 Shared Printer', 'Printer', 'HQ-Coimbatore', 'Degraded', 72),
            ('ERP-PROD-01', 'Production ERP Database Server', 'Application Server', 'DC-Mumbai', 'Operational', 88),
            ('MAIL-EXCH-01', 'Exchange Mail Server 01', 'Application Server', 'Branch-Kolkata', 'Degraded', 65),
            ('NET-GW-VPN-02', 'GlobalProtect VPN Gateway 02', 'Network Gateway', 'DC-Mumbai', 'Operational', 91),
            ('EUC-FLEET', 'Dell Latitude Fleet Assets', 'Laptop Fleet', 'Remote-WFH', 'Operational', 84),
            ('IDP-OKTA-01', 'Okta SSO Identity Provider', 'Identity Provider', 'HQ-Coimbatore', 'Operational', 99),
            ('MON-F3-HQ', 'Floor 3 USB-C Display Dock Fleet', 'Monitor Fleet', 'HQ-Coimbatore', 'Operational', 90)
        ]
        cursor.executemany('''
            INSERT INTO assets (asset_id, asset_name, asset_type, site, status, health_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', assets_data)

    cursor.execute("PRAGMA table_info(tickets)")
    columns = [row['name'] for row in cursor.fetchall()]
    if 'user_email' not in columns:
        cursor.execute("ALTER TABLE tickets ADD COLUMN user_email TEXT DEFAULT 'user@company.com'")

    conn.commit()
    conn.close()
    
    seed_tickets_if_empty()

def seed_tickets_if_empty():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM tickets")
    count = cursor.fetchone()['cnt']
    
    if count == 0 and os.path.exists(CSV_PATH):
        print(f"Seeding database from {CSV_PATH}...")
        with open(CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            engineers = ['Alex Mercer', 'Sarah Connor', 'David Miller', 'Elena Rostova', 'James Holden', 'Priya Sharma', 'Marcus Vance']
            departments = ['Finance', 'Human Resources', 'Engineering', 'Customer Success', 'Sales & Marketing', 'Legal', 'IT Infrastructure']
            
            records = []
            import random
            random.seed(42)
            
            for row in reader:
                eng = random.choice(engineers)
                dept = random.choice(departments)
                
                records.append((
                    row['ticket_id'],
                    row['created_date'],
                    row.get('resolved_date', ''),
                    row.get('channel', 'Portal'),
                    row.get('category', 'General'),
                    row.get('subcategory', 'Other'),
                    row.get('short_description', ''),
                    row.get('affected_asset', 'N/A'),
                    row.get('asset_type', 'Asset'),
                    row.get('site', 'HQ'),
                    row.get('priority', 'P3-Medium'),
                    row.get('resolver_team', 'IT Support'),
                    row.get('resolution_code', 'Resolved'),
                    int(row.get('is_workaround', 0)),
                    float(row.get('effort_hours', 1.0)),
                    int(row.get('users_affected', 1)),
                    int(row.get('reopened_count', 0)),
                    row.get('status', 'Closed'),
                    row.get('true_cluster_id', 'NONE'),
                    eng,
                    dept,
                    'NONE',
                    'NORMAL',
                    'user@company.com'
                ))
            
            cursor.executemany('''
                INSERT INTO tickets (
                    ticket_id, created_date, resolved_date, channel, category, subcategory,
                    short_description, affected_asset, asset_type, site, priority,
                    resolver_team, resolution_code, is_workaround, effort_hours,
                    users_affected, reopened_count, status, true_cluster_id,
                    assigned_engineer, department, predicted_cluster_id, category_flag, user_email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            conn.commit()
            print(f"Successfully seeded {len(records)} tickets into SQLite database.")
    
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialization complete.")
