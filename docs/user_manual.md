# User Manual & Operating Guide

## Introduction
The Recurring Demand Miner empowers Enterprise Service Desk teams to shift from reactive incident handling to proactive Problem Management.

## Step-by-Step Guide

### 1. Dashboard Navigation
- View top-level KPIs: Total Tickets, Open/Closed Tickets, Recurring Incidents count, and Demand Reduction Percentage.
- Inspect real-time Chart.js visual graphs for monthly ticket trends and intake channel distribution.

### 2. Managing Tickets
- Go to **Ticket Management**.
- Use the search bar to find tickets by ID, keyword, or asset.
- Click **Add Ticket** to log a new incident manually, or **Import CSV** to batch load thousands of tickets.
- Click on any Ticket ID to view full metadata, resolution details, and workaround flags.

### 3. Running the Demand Miner
- Navigate to **Demand Miner**.
- Choose your preferred clustering algorithm (**KMeans** or **DBSCAN**) and set cluster parameters.
- Click **Run Demand Mining**.
- Review the generated cluster cards: Check recurrence interval (days), total engineer effort hours, repeated workaround percentage, and confidence score.

### 4. Reviewing Permanent Fix Recommendations
- Navigate to **Permanent Fix Recommendations**.
- Inspect ranked issues by Priority Score.
- Review expected ticket reduction %, estimated time saved, and cost savings ($).

### 5. Evaluating Machine Learning Models & Experiments
- Open **ML Benchmarks**.
- Compare performance metrics across KMeans, DBSCAN, and Keyword Baseline.
- Review Precision, Recall, F1 Score, Accuracy, and Execution Time.

### 6. Edge Case Failure Handling
- Open **Failure Cases**.
- Click **Run Edge Case Simulator** to view live detection of duplicate tickets, missing descriptions, and conflicting categories.

### 7. Workflow Coexistence & Rollback
- Open **Workflow Coexistence**.
- Toggle between **Legacy Manual Workflow** and **New AI Workflow**.
- Use the **Rollback to Legacy Workflow** button whenever needed to maintain data integrity.

### 8. Stakeholder Validation
- Service Managers can submit feedback on identified clusters and approve permanent fixes.
- Track average manager satisfaction ratings in real time.

### 9. Generating Reports
- Open **Reports Center**.
- Download PDF or CSV exports for any of the 6 standard reports.
