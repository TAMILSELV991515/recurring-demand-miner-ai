# Recurring Demand Miner - Enterprise Service Desk Problem Management Platform

An intelligent AI-powered system designed for Enterprise Service Desks that analyzes IT support tickets across multiple intake channels (Email, Chat, Phone, Portal), identifies recurring incidents, groups similar tickets into semantic clusters, calculates business impact/effort, and recommends permanent fixes (Problem Management) to systematically eliminate repetitive support demand.

---

## Key Features

1. **Executive Dashboard**: Real-time KPI cards, demand reduction percentage, monthly ticket volume trends, intake channel distribution, and top recurring issue clusters.
2. **Ticket Management**: Full CRUD operations, search & filtering, CSV import/export, and individual ticket details view.
3. **Recurring Demand Miner Engine**: Uses **TF-IDF + Cosine Similarity** with **KMeans** and **DBSCAN** clustering. Computes recurrence intervals (days), total support effort (hours), repeated workaround frequency, and confidence scores.
4. **Permanent Fix Recommendation Engine**: Prioritizes problem management interventions based on ROI, computing expected ticket reduction %, estimated time saved, and cost saved ($).
5. **Downloadable Reports**: Production-ready PDF and CSV exports for 6 standard reports (Recurring Incidents, Monthly Analysis, Permanent Fix Recommendations, Asset Impact, Engineer Performance, Cost Savings).
6. **Machine Learning Benchmarking**: Comparative evaluation table displaying Precision, Recall, F1 Score, Execution Time, and Accuracy comparing KMeans, DBSCAN, and Keyword Matching baseline. Includes structured experiments & error analysis.
7. **Failure Cases Resilience Suite**: Automated detection and graceful handling for (1) Duplicate tickets, (2) Missing descriptions, and (3) Conflicting categories with a live simulator.
8. **Coexistence Mode & Rollback**: Seamless toggle between **New AI Workflow** and **Legacy Manual Workflow**, accompanied by a zero-data-loss **Rollback to Legacy Workflow** demonstration button.
9. **Stakeholder Validation**: Service Manager feedback collection module with real-time approval rates and average satisfaction metrics.
10. **Dataset Generator**: Script to generate up to 10,000 synthetic IT support tickets.
11. **Modern Admin UI**: Built with Bootstrap 5, Chart.js, glassmorphic cards, responsive tables, and a dark/light theme switcher with local storage persistence.

---

## Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism & Themes), JavaScript (ES6+), Bootstrap 5, Chart.js
- **Backend**: Python Flask (REST API)
- **Database**: SQLite3 (`demand_miner.db`)
- **Machine Learning & NLP**: Scikit-learn (`TfidfVectorizer`, `KMeans`, `DBSCAN`, `cosine_similarity`)
- **PDF Generation**: ReportLab
- **Data Utilities**: Pandas, NumPy

---

## Directory Structure

```
coe project/
├── app.py                      # Main Flask application entry point
├── database.py                 # SQLite database initialization & query helpers
├── dataset_generator.py        # Synthetic 10,000 ticket dataset generator
├── requirements.txt            # Python dependencies
├── service_desk_tickets.csv    # Seed dataset (5,002 tickets)
├── README.md                   # Comprehensive guide and documentation
├── ml_engine/
│   ├── __init__.py
│   ├── preprocessor.py         # Text cleaning and preprocessing
│   ├── vectorizer.py           # TF-IDF & Cosine Similarity computation
│   ├── clusterer.py            # KMeans, DBSCAN & Keyword Baseline clustering
│   ├── evaluator.py            # Precision, Recall, F1, Accuracy & Execution time benchmarks
│   └── fix_recommender.py      # Problem Management Fix Recommendation & ROI Engine
├── failure_cases/
│   ├── __init__.py
│   └── edge_case_handler.py    # Detector & handler for duplicate, missing, and misclassified tickets
├── reports/
│   ├── __init__.py
│   └── report_generator.py     # Downloadable PDF & CSV report generator (6 report types)
├── docs/
│   ├── system_architecture.md  # System Architecture & Pipeline Flowchart
│   ├── er_diagram.md           # Entity Relationship Diagram & Schema
│   ├── api_documentation.md    # REST API endpoints reference
│   ├── user_manual.md          # User & Service Manager Guide
│   └── presentation_slides.md  # Presentation deck artifact
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphism & dark/light theme CSS
│   └── js/
│       ├── main.js             # UI interactions & theme toggle logic
│       └── charts.js           # Chart.js graphs initialization
└── templates/
    ├── base.html               # Base layout with sidebar, navbar, dark mode toggle
    ├── dashboard.html          # Real-time metrics & top recurring issues summary
    ├── tickets.html            # Ticket Management (CRUD, filter, search, CSV import/export)
    ├── ticket_detail.html      # Ticket details view
    ├── miner.html              # Recurring Demand Miner ML clustering
    ├── fix_recommendations.html # Permanent Fix Engine with ROI & cost savings metrics
    ├── benchmarks.html         # ML Model Comparison & Experiments
    ├── edge_cases.html         # Failure Cases simulator & resolution logs
    ├── workflow_toggle.html    # Legacy vs AI Coexistence Mode & Rollback Demo
    ├── feedback.html           # Stakeholder Validation module
    ├── reports.html            # PDF & CSV report download center
    └── documentation.html      # Technical Docs, Architecture, ER Diagram & Slides
```

---

## Quick Start Guide

### 1. Prerequisites
Ensure Python 3.9+ is installed on your Windows machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
Seed the SQLite database with 5,000+ realistic service desk tickets:
```bash
python database.py
```

### 4. Run the Application
Start the Flask application server:
```bash
python app.py
```

Open your browser and navigate to:
**`http://localhost:5000`**

---

## Generating 10,000 Synthetic Tickets

To generate a new synthetic dataset containing 10,000 IT support tickets:
```bash
python dataset_generator.py
```
This produces `service_desk_tickets_10k.csv`, which can be imported via the **Ticket Management -> Import CSV** feature on the dashboard.
