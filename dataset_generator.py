import csv
import random
from datetime import datetime, timedelta

RECURRING_TEMPLATES = [
    {
        "cluster_id": "CL-PRINT-SPOOL-02",
        "category": "Hardware",
        "subcategory": "Printing",
        "title": "Print jobs stuck in spooler on floor shared printer",
        "desc": "Print queue is frozen on print server. Jobs accumulate and timeout. Restarting spooler service clears queue temporarily.",
        "asset": "PRT-F2-HQ",
        "asset_type": "Printer",
        "fix": "Deploy print driver v4.2 update and configure automatic print spooler service health monitor.",
        "team": "Field Support"
    },
    {
        "cluster_id": "CL-ERP-BATCH-FAIL-02",
        "category": "Application",
        "subcategory": "ERP Batch Job",
        "title": "Nightly ERP batch job fails at step 1, requires manual rerun",
        "desc": "Automated ledger sync fails due to lock timeout on SQL database. Engineer manually re-runs batch at 6 AM.",
        "asset": "ERP-PROD-01",
        "asset_type": "Application Server",
        "fix": "Optimize SQL database query index on transactions table and increase connection timeout from 30s to 120s.",
        "team": "App Support"
    },
    {
        "cluster_id": "CL-EMAIL-QUOTA-03",
        "category": "Application",
        "subcategory": "Email",
        "title": "Mailbox over quota, user cannot send/receive email",
        "desc": "Exchange mailbox exceeds 10GB threshold. User blocked from sending emails. Temporary 2GB quota extension granted.",
        "asset": "MAIL-EXCH-01",
        "asset_type": "Application Server",
        "fix": "Implement automated 30-day auto-archive policy for attachments >10MB and expand default mailbox limit to 25GB.",
        "team": "App Support"
    },
    {
        "cluster_id": "CL-VPN-AUTH-01",
        "category": "Network",
        "subcategory": "VPN",
        "title": "GlobalProtect VPN handshake failure after MFA prompt",
        "desc": "Remote user disconnected every 45 mins due to RADIUS timeout. Re-authenticating token bypasses error temporarily.",
        "asset": "NET-GW-VPN-02",
        "asset_type": "Network Gateway",
        "fix": "Upgrade RADIUS server authentication timeout configuration and deploy client patch v5.3.1.",
        "team": "Network Ops"
    },
    {
        "cluster_id": "CL-BATTERY-DRAIN-04",
        "category": "Hardware",
        "subcategory": "Laptop",
        "title": "Laptop battery drains rapidly / device shuts down unexpectedly",
        "desc": "Dell Latitude 5420 battery drops from 80% to 5% within 30 minutes. Power plan reset resolves temporarily.",
        "asset": "EUC-FLEET",
        "asset_type": "Laptop",
        "fix": "Issue battery replacement recall for batch Dell Latitude 5420 devices manufactured Q3 2023.",
        "team": "End User Compute"
    },
    {
        "cluster_id": "CL-SSO-TOKEN-EXPIRE",
        "category": "Access",
        "subcategory": "Authentication",
        "title": "Okta SSO session expires prematurely during active work",
        "desc": "User logged out of internal web portal without warning. Clearing browser cache & cookies allows re-login.",
        "asset": "IDP-OKTA-01",
        "asset_type": "Identity Provider",
        "fix": "Adjust SAML token lifetime settings from 1 hour to 8 hours with idle keep-alive refresh.",
        "team": "Identity & Access"
    }
]

ONE_OFF_TEMPLATES = [
    ("Access", "New Hire", "New hire onboarding - provision accounts and equipment", "User Account"),
    ("Access", "Offboarding", "Offboarding - disable accounts for departing employee", "User Account"),
    ("Hardware", "Monitor", "External monitor not detected via USB-C dock", "Monitor"),
    ("Hardware", "Peripheral", "Wireless mouse/keyboard replacement request", "Peripheral"),
    ("Server", "Provisioning", "Request to provision new test/dev Virtual Machine", "Virtual Machine"),
    ("Facilities", "Badge Access", "Badge access request for main building second floor", "Badge System"),
    ("Application", "License", "Specialized CAD software license key activation issue", "Application"),
    ("Network", "Wifi", "Guest Wi-Fi password reset request for visitor", "Access Point")
]

CHANNELS = ['Phone', 'Email', 'Chat', 'Portal']
PRIORITIES = ['P1-Critical', 'P2-High', 'P3-Medium', 'P4-Low']
RESOLVER_TEAMS = ['App Support', 'Field Support', 'Identity & Access', 'Network Ops', 'Server Ops', 'End User Compute']
SITES = ['HQ-Coimbatore', 'DC-Mumbai', 'Branch-Kolkata', 'Branch-Delhi', 'Plant-Pune', 'Plant-Bengaluru', 'Remote-WFH']
ENGINEERS = ['Alex Mercer', 'Sarah Connor', 'David Miller', 'Elena Rostova', 'James Holden', 'Priya Sharma', 'Marcus Vance']
DEPARTMENTS = ['Finance', 'Human Resources', 'Engineering', 'Customer Success', 'Sales & Marketing', 'Legal', 'IT Infrastructure']

def generate_dataset(output_filename="service_desk_tickets_10k.csv", num_records=10000):
    start_date = datetime(2024, 1, 1, 8, 0, 0)
    records = []
    
    random.seed(12345)
    
    print(f"Generating {num_records} synthetic tickets...")
    
    for i in range(1, num_records + 1):
        ticket_id = f"INC{100000 + i}"
        
        # 60% recurring incidents, 40% one-off incidents
        is_recurring = random.random() < 0.60
        
        if is_recurring:
            template = random.choice(RECURRING_TEMPLATES)
            cluster_id = template['cluster_id']
            category = template['category']
            subcategory = template['subcategory']
            short_desc = template['title']
            asset = template['asset']
            asset_type = template['asset_type']
            team = template['team']
            is_workaround = 1 if random.random() < 0.75 else 0
            res_code = "Workaround Applied" if is_workaround else "Resolved - No Root Cause Found"
        else:
            template = random.choice(ONE_OFF_TEMPLATES)
            cluster_id = "NONE"
            category = template[0]
            subcategory = template[1]
            short_desc = template[2]
            asset = f"AST-{random.randint(100, 999)}"
            asset_type = template[3]
            team = random.choice(RESOLVER_TEAMS)
            is_workaround = 1 if random.random() < 0.20 else 0
            res_code = "Permanent Fix Applied" if random.random() < 0.5 else "Resolved - Standard Procedure"
            
        created_delta_minutes = random.randint(0, 365 * 24 * 60)
        created_dt = start_date + timedelta(minutes=created_delta_minutes)
        resolution_hrs = round(random.uniform(0.2, 8.0), 2)
        resolved_dt = created_dt + timedelta(hours=resolution_hrs)
        
        effort_hours = round(random.uniform(0.2, 4.0), 2)
        channel = random.choice(CHANNELS)
        priority = random.choice(PRIORITIES)
        site = random.choice(SITES)
        users_affected = random.randint(1, 15) if priority in ['P1-Critical', 'P2-High'] else 1
        reopened_count = 1 if random.random() < 0.15 else 0
        status = 'Closed' if random.random() < 0.85 else 'Resolved'
        
        records.append({
            'ticket_id': ticket_id,
            'created_date': created_dt.strftime('%Y-%m-%d %H:%M'),
            'resolved_date': resolved_dt.strftime('%Y-%m-%d %H:%M'),
            'channel': channel,
            'category': category,
            'subcategory': subcategory,
            'short_description': short_desc,
            'affected_asset': asset,
            'asset_type': asset_type,
            'site': site,
            'priority': priority,
            'resolver_team': team,
            'resolution_code': res_code,
            'is_workaround': is_workaround,
            'effort_hours': effort_hours,
            'users_affected': users_affected,
            'reopened_count': reopened_count,
            'status': status,
            'true_cluster_id': cluster_id
        })
        
    fieldnames = list(records[0].keys())
    with open(output_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Dataset generator complete. Saved {num_records} tickets to {output_filename}.")

if __name__ == '__main__':
    generate_dataset()
