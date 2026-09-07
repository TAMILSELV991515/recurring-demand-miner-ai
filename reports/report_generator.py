import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_csv_report(report_type, tickets, clusters):
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'recurring_incidents':
        writer.writerow(['Cluster ID', 'Cluster Name', 'Category', 'Ticket Count', 'Avg Res Time (Hrs)', 'Total Effort (Hrs)', 'Workaround %', 'Affected Assets', 'Recurrence Interval (Days)', 'Confidence Score'])
        for c in clusters:
            writer.writerow([c['cluster_id'], c['cluster_name'], c['category'], c['ticket_count'], c['avg_resolution_time_hrs'], c['total_effort_hours'], f"{c['workaround_freq_pct']}%", c['affected_assets'], c['recurrence_interval_days'], f"{c['confidence_score']}%"])
            
    elif report_type == 'permanent_fixes':
        writer.writerow(['Cluster ID', 'Issue Name', 'Priority Score', 'Recommended Permanent Fix', 'Expected Reduction %', 'Time Saved (Hrs)', 'Cost Saved ($)'])
        for c in clusters:
            writer.writerow([c['cluster_id'], c['cluster_name'], c['priority_score'], c['recommended_fix'], f"{c['expected_ticket_reduction_pct']}%", c['time_saved_hours'], f"${c['cost_saved_usd']}"])
            
    elif report_type == 'asset_impact':
        writer.writerow(['Asset Name', 'Asset Type', 'Total Tickets', 'Total Effort Hours', 'Workaround Count'])
        asset_map = {}
        for t in tickets:
            asset = t['affected_asset']
            if asset not in asset_map:
                asset_map[asset] = {'type': t['asset_type'], 'count': 0, 'effort': 0.0, 'workaround': 0}
            asset_map[asset]['count'] += 1
            asset_map[asset]['effort'] += t['effort_hours']
            if t['is_workaround'] == 1:
                asset_map[asset]['workaround'] += 1
        for asset, data in sorted(asset_map.items(), key=lambda x: x[1]['count'], reverse=True)[:50]:
            writer.writerow([asset, data['type'], data['count'], round(data['effort'], 2), data['workaround']])
            
    elif report_type == 'engineer_performance':
        writer.writerow(['Assigned Engineer', 'Department', 'Tickets Resolved', 'Total Effort (Hrs)', 'Avg Effort/Ticket'])
        eng_map = {}
        for t in tickets:
            eng = t.get('assigned_engineer', 'Unassigned')
            dept = t.get('department', 'IT Operations')
            if eng not in eng_map:
                eng_map[eng] = {'dept': dept, 'count': 0, 'effort': 0.0}
            eng_map[eng]['count'] += 1
            eng_map[eng]['effort'] += t['effort_hours']
        for eng, data in eng_map.items():
            avg_e = data['effort'] / data['count'] if data['count'] > 0 else 0
            writer.writerow([eng, data['dept'], data['count'], round(data['effort'], 2), round(avg_e, 2)])
            
    elif report_type == 'cost_savings':
        writer.writerow(['Cluster ID', 'Category', 'Total Support Effort (Hrs)', 'Expected Time Saved (Hrs)', 'Hourly Rate ($)', 'Estimated Cost Savings ($)'])
        total_sav = 0
        for c in clusters:
            writer.writerow([c['cluster_id'], c['category'], c['total_effort_hours'], c['time_saved_hours'], "$50.00", f"${c['cost_saved_usd']}"])
            total_sav += c['cost_saved_usd']
        writer.writerow([])
        writer.writerow(['', '', '', '', 'TOTAL SAVINGS:', f"${total_sav:,.2f}"])
        
    else: # Monthly Analysis default
        writer.writerow(['Ticket ID', 'Created Date', 'Category', 'Priority', 'Channel', 'Status', 'Effort Hours', 'Workaround Used'])
        for t in tickets[:200]:
            writer.writerow([t['ticket_id'], t['created_date'], t['category'], t['priority'], t['channel'], t['status'], t['effort_hours'], t['is_workaround']])
            
    return output.getvalue().encode('utf-8')

def generate_pdf_report(report_type, tickets, clusters):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#1e293b'), spaceAfter=10)
    subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=15)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#0f172a'), spaceBefore=10, spaceAfter=8)
    cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#334155'))
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#0f172a'))
    
    elements = []
    
    title_map = {
        'recurring_incidents': 'Recurring Incidents & Cluster Demand Mining Report',
        'permanent_fixes': 'Permanent Fix Recommendations & ROI Strategy',
        'asset_impact': 'Asset Impact & Fleet Vulnerability Analysis',
        'engineer_performance': 'Engineer Support Performance & Workload Metrics',
        'cost_savings': 'Cost Savings & Problem Management ROI Report',
        'monthly_analysis': 'Monthly Incident Trend & Support Demand Analysis'
    }
    
    report_title = title_map.get(report_type, 'Enterprise Service Desk Executive Report')
    elements.append(Paragraph(report_title, title_style))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y - %H:%M:%S')} | Enterprise Service Desk Problem Management", subtitle_style))
    elements.append(Spacer(1, 10))
    
    if report_type == 'recurring_incidents' or report_type == 'permanent_fixes':
        table_data = [[
            Paragraph('<b>ID</b>', cell_bold),
            Paragraph('<b>Cluster Issue Name</b>', cell_bold),
            Paragraph('<b>Category</b>', cell_bold),
            Paragraph('<b>Tickets</b>', cell_bold),
            Paragraph('<b>Effort (h)</b>', cell_bold),
            Paragraph('<b>Interval</b>', cell_bold),
            Paragraph('<b>Rec. Fix Strategy</b>', cell_bold)
        ]]
        for c in clusters[:10]:
            table_data.append([
                Paragraph(c['cluster_id'], cell_style),
                Paragraph(c['cluster_name'][:30], cell_style),
                Paragraph(c['category'], cell_style),
                Paragraph(str(c['ticket_count']), cell_style),
                Paragraph(str(c['total_effort_hours']), cell_style),
                Paragraph(f"{c['recurrence_interval_days']}d", cell_style),
                Paragraph(c['recommended_fix'][:40] + '...', cell_style)
            ])
            
    elif report_type == 'cost_savings':
        table_data = [[
            Paragraph('<b>Cluster ID</b>', cell_bold),
            Paragraph('<b>Issue Category</b>', cell_bold),
            Paragraph('<b>Total Effort (hrs)</b>', cell_bold),
            Paragraph('<b>Time Saved (hrs)</b>', cell_bold),
            Paragraph('<b>Cost Saved ($)</b>', cell_bold),
            Paragraph('<b>ROI Impact</b>', cell_bold)
        ]]
        for c in clusters[:10]:
            table_data.append([
                Paragraph(c['cluster_id'], cell_style),
                Paragraph(c['category'], cell_style),
                Paragraph(str(c['total_effort_hours']), cell_style),
                Paragraph(str(c['time_saved_hours']), cell_style),
                Paragraph(f"${c['cost_saved_usd']:,.2f}", cell_bold),
                Paragraph(c['estimated_business_impact'][:20], cell_style)
            ])
            
    else:
        table_data = [[
            Paragraph('<b>Ticket ID</b>', cell_bold),
            Paragraph('<b>Date</b>', cell_bold),
            Paragraph('<b>Category</b>', cell_bold),
            Paragraph('<b>Priority</b>', cell_bold),
            Paragraph('<b>Channel</b>', cell_bold),
            Paragraph('<b>Short Description</b>', cell_bold)
        ]]
        for t in tickets[:15]:
            table_data.append([
                Paragraph(t['ticket_id'], cell_style),
                Paragraph(t['created_date'][:10], cell_style),
                Paragraph(t['category'], cell_style),
                Paragraph(t['priority'], cell_style),
                Paragraph(t['channel'], cell_style),
                Paragraph(t['short_description'][:40], cell_style)
            ])
            
    t_table = Table(table_data, colWidths=None)
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(t_table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Confidential - Internal Enterprise Service Desk Report", subtitle_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
