# Recurring Demand Miner - Enterprise Service Desk Problem Management Platform

An intelligent AI-powered system designed for Enterprise Service Desks that analyzes IT support tickets across multiple intake channels (Email, Chat, Phone, Portal), identifies recurring incidents, groups similar tickets into semantic clusters, calculates business impact/effort, and recommends permanent fixes (Problem Management) to systematically eliminate repetitive support demand.

---

## Key Features

1. **Executive Dashboard**: Real-time KPI cards, demand reduction percentage, monthly ticket volume trends, intake channel distribution, and top recurring issue clusters.
2. **Ticket Management**: Full CRUD operations, search & filtering, CSV import/export, and individual ticket details view.
3. **Multi-Algorithm Demand Miner Engine**: Employs **TF-IDF Sublinear Vectorization** and **Sentence-Transformers (Dense Semantic Embeddings)** paired with **KMeans**, **DBSCAN**, **HDBSCAN**, and **Agglomerative Hierarchical Clustering**. Computes recurrence intervals (days), total support effort (hours), repeated workaround frequency, and internal cohesion confidence scores.
4. **Prioritization & Permanent Fix Recommendation Engine**: Formally ranks problem management interventions using a mathematical scoring formula ($S_{\text{priority}}$) that integrates effort hours, ticket frequency, workaround reliance, and discrete business impact weight scalars.
5. **Downloadable Reports**: Production-ready PDF and CSV exports for 6 standard reports (Recurring Incidents, Monthly Analysis, Permanent Fix Recommendations, Asset Impact, Engineer Performance, Cost Savings).
6. **Empirical ML Benchmarking Suite**: Comparative evaluation suite displaying **Precision**, **Recall**, **F1 Score**, **Cluster Purity**, **Accuracy**, and **Execution Time** comparing KMeans, DBSCAN, HDBSCAN, Agglomerative, Sentence-Transformers, and Keyword Baseline.
7. **Failure Cases Resilience Suite**: Automated detection and graceful handling for (1) Duplicate tickets, (2) Missing descriptions, and (3) Conflicting categories with a live simulator.
8. **Coexistence Mode & Rollback**: Seamless toggle between **New AI Workflow** and **Legacy Manual Workflow**, accompanied by a zero-data-loss **Rollback to Legacy Workflow** demonstration button.
9. **Stakeholder Validation**: Service Manager feedback collection module with real-time approval rates and average satisfaction metrics.
10. **Automated Unit Testing Suite**: Granular test suite (`tests/test_suite.py`) covering preprocessing, vectorizers, clusterers, prioritization scoring, edge case handling, and REST endpoints.
11. **Modern Admin UI**: Built with Bootstrap 5, Chart.js, glassmorphic cards, responsive tables, and a dark/light theme switcher with local storage persistence.

---

## Technical Specifications: Exact NLP & Clustering Pipeline

```
Raw Ticket Text ──> Regex Cleaning & Tokenization ──> IT Stopword Stripping ──> TF-IDF / Sentence-Transformers ──> Clustering Engine ──> Cohesion & Prioritization Score
```

1. **Text Preprocessing**: Lowercasing, URL/email stripping, regex non-alphanumeric removal, IT domain stop-word filtering (`issue`, `ticket`, `problem`, `user`, `please`, `help`, `request`), and unigram/bigram tokenization ($1 \le n \le 2$).
2. **Feature Representation**:
   - **TF-IDF Scaling**: $\text{tf}_{\text{sub}} = 1 + \log(\text{tf})$, $\text{idf}(t) = \log\frac{1 + N}{1 + \text{df}(t)} + 1$, $L_2$ normalized.
   - **Dense Embeddings**: Pre-trained Transformer embeddings (`all-MiniLM-L6-v2`) with Latent Semantic Analysis (TruncatedSVD LSA) dense fallback.
3. **Clustering Algorithms**:
   - **KMeans**: Partitioning via centroid optimization.
   - **DBSCAN**: Cosine density clustering ($\epsilon=0.4$, $\text{min\_samples}=3$).
   - **HDBSCAN**: Hierarchical density estimation with noise isolation.
   - **Agglomerative**: Bottom-up cosine hierarchical linkage.
   - **Keyword Baseline**: Naive rule-based matching.

---

## Mathematical Formula for Demand Prioritization

The recurring demand priority score ($S_{\text{priority}}$) is computed as follows:

$$S_{\text{priority}} = (w_f \cdot N_{\text{tickets}}) + (w_w \cdot P_{\text{workaround}}) + (w_e \cdot E_{\text{total}}) + I_{\text{impact}}$$

Where:
- $N_{\text{tickets}}$ = Cluster ticket volume ($w_f = 0.4$)
- $P_{\text{workaround}}$ = Percentage of tickets resolved using temporary workaround ($w_w = 0.3$)
- $E_{\text{total}}$ = Total accumulated support effort in engineer hours ($w_e = 0.3$)
- $I_{\text{impact}}$ = Discrete business impact weight scalar:

$$I_{\text{impact}} = \begin{cases} 30 & \text{if } N_{\text{tickets}} \ge 15 \text{ or } E_{\text{total}} \ge 20 \text{ (CRITICAL)} \\ 20 & \text{if } N_{\text{tickets}} \ge 8 \text{ or } E_{\text{total}} \ge 10 \text{ (HIGH)} \\ 10 & \text{otherwise (MEDIUM)} \end{cases}$$

---

## Empirical Benchmarks

Empirical performance evaluation across 1,000 ground-truth tagged support tickets:

| Model / Algorithm | Precision % | Recall % | F1 Score % | Cluster Purity % | Accuracy % | Execution Time (sec) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **HDBSCAN (Hierarchical Density)** | **64.76%** | **77.50%** | **69.52%** | **78.00%** | **77.50%** | 0.0857s |
| **DBSCAN (Density-Based)** | **64.76%** | **77.50%** | **69.52%** | **77.50%** | **77.50%** | 0.0200s |
| **Sentence-Transformers + KMeans** | 46.88% | 67.00% | 54.66% | 67.00% | 67.00% | 0.1185s |
| **KMeans (TF-IDF)** | 46.88% | 67.00% | 54.66% | 67.00% | 67.00% | 3.1206s |
| **Agglomerative (Hierarchical)** | 53.71% | 56.00% | 52.05% | 56.00% | 56.00% | 0.2312s |
| **Keyword Baseline (Rule-Based)** | 35.08% | 56.50% | 42.73% | 60.50% | 56.50% | 0.0028s |

---

## Unit Testing & Error Boundaries Architecture

### 1. Automated Unit Test Suite (`tests/test_suite.py`)
The codebase includes an automated unit test suite built with Python's `unittest` framework. It validates component contracts across 18 distinct test cases:

- **`TestTextPreprocessor`**: Validates lowercasing, RegEx URL/email stripping, domain stop-word filtering, and null handling.
- **`TestTextVectorizer`**: Tests TF-IDF matrix dimensions, vocabulary extraction, L2 normalization, and `DenseEmbedder` (SBERT & LSA fallback).
- **`TestClusteringAlgorithms`**: Tests `KMeansClusterer`, `DBSCANClusterer`, `HDBSCANClusterer`, `AgglomerativeClusterer`, and `KeywordBaselineClusterer` output label types and boundary conditions.
- **`TestPrioritizationEngine`**: Verifies $S_{\text{priority}}$ calculation, $I_{\text{impact}}$ scalars, recurrence interval calculations, and ROI metrics.
- **`TestModelEvaluatorAndMetrics`**: Verifies calculation of Precision, Recall, F1, Accuracy, Cluster Purity %, and Execution Time.
- **`TestEdgeCaseResilienceHandler`**: Tests automated detection and resolution of duplicate tickets, missing descriptions, and category mismatches.
- **`TestRESTAPIEndpointsAndErrorBoundaries`**: Tests REST endpoints (`/api/dashboard`, `/api/miner/cluster`, `/api/benchmarks/run`, `/api/workflow/toggle`) and HTTP 404/500 error boundaries.

**Running the Unit Test Suite:**
```bash
python -m unittest tests/test_suite.py
```

### 2. Error Boundaries & System Resilience Strategy
The system implements explicit error boundaries at both application middleware and ML execution layers:
- **Zero-Vector Boundary Protection**: `AgglomerativeClusterer` automatically checks for zero-norm feature vectors and injects a $1e-9$ epsilon offset, preventing Scikit-Learn `ValueError: Cosine affinity cannot be used when X contains zero vectors`.
- **HDBSCAN Import Fallback**: If `hdbscan` C-extension libraries fail to load in light environments, `HDBSCANClusterer` gracefully falls back to Cosine DBSCAN density clustering without crashing.
- **Dense Embedder LSA Fallback**: `DenseEmbedder` detects `sentence_transformers` presence; if missing, it switches to Latent Semantic Analysis (TruncatedSVD LSA) on TF-IDF matrices.
- **REST Middleware Error Boundary**: `@app.errorhandler(403)`, `@app.errorhandler(404)`, and `@app.errorhandler(500)` return sanitized JSON error envelopes and glassmorphic UI fallback pages.

---

## Database Schema Documentation

The system utilizes SQLite3 (`demand_miner.db`). Complete schema specification across all 9 tables:

### 1. `tickets`
Stores incident records across all intake channels:
- `ticket_id` (TEXT, PK): Unique ticket identifier (e.g., `INC100001`).
- `created_date` (TEXT): Creation timestamp (`YYYY-MM-DD HH:MM`).
- `resolved_date` (TEXT): Resolution timestamp.
- `channel` (TEXT): Intake channel (`Email`, `Chat`, `Phone`, `Portal`).
- `category` (TEXT): Primary category (`Hardware`, `Application`, `Access`, `Network`, `Server`, `Facilities`).
- `subcategory` (TEXT): Secondary categorization.
- `short_description` (TEXT): Unstructured title and summary text.
- `affected_asset` (TEXT): Asset serial number or hostname.
- `asset_type` (TEXT): Asset category (e.g., `Laptop`, `Printer`, `Router`).
- `site` (TEXT): Physical site location.
- `priority` (TEXT): SLA priority (`P1-Critical`, `P2-High`, `P3-Medium`, `P4-Low`).
- `resolver_team` (TEXT): Assigned support squad.
- `resolution_code` (TEXT): Outcome status.
- `is_workaround` (INTEGER): Flag (`1` if resolved via temporary workaround, `0` otherwise).
- `effort_hours` (REAL): Support effort spent by engineers.
- `users_affected` (INTEGER): Number of impacted end-users.
- `reopened_count` (INTEGER): Number of times ticket was reopened.
- `status` (TEXT): Lifecycle status (`Open`, `In Progress`, `Resolved`, `Closed`).
- `true_cluster_id` (TEXT): Ground truth cluster tag for benchmarking.
- `assigned_engineer` (TEXT): Assigned IT technician name.
- `department` (TEXT): User department.
- `predicted_cluster_id` (TEXT): Model predicted cluster ID.
- `category_flag` (TEXT): Mismatch flag from edge-case detector (`NORMAL` or `MISMATCH: Category`).
- `user_email` (TEXT): User email identifier.

### 2. `clusters`
Stores mined problem management issue clusters:
- `cluster_id` (TEXT, PK): Cluster identifier (e.g., `CL-HAR-01`).
- `cluster_name` (TEXT): Generated cluster title.
- `category` (TEXT): Majority incident category.
- `ticket_count` (INTEGER): Total ticket volume in cluster.
- `total_effort_hours` (REAL): Accumulated support effort.
- `recurrence_interval_days` (REAL): Mean days between consecutive incidents ($\Delta t_{\text{avg}}$).
- `confidence_score` (REAL): Intra-cluster Cosine similarity cohesion score ($C_{\text{confidence}}$).
- `recommended_fix` (TEXT): Actionable Permanent Fix solution template.
- `priority_score` (REAL): Calculated urgency score ($S_{\text{priority}}$).
- `cost_saved_usd` (REAL): Projected financial savings ($).

### 3. `users` & `admins`
Stores Portal user accounts and Admin authentication credentials.
- `users`: `user_id` (PK), `full_name`, `email`, `phone`, `password_hash`, `created_at`.
- `admins`: `admin_id` (PK), `username`, `password_hash`, `name`, `email`, `role`.

### 4. `engineers` & `assets`
Tracks IT support personnel and asset inventory:
- `engineers`: `engineer_id` (PK), `name`, `email`, `department`, `resolver_team`, `active_tickets`.
- `assets`: `asset_id` (PK), `asset_name`, `asset_type`, `site`, `status`, `health_score`.

### 5. `stakeholder_feedback`
Stores Service Manager evaluations:
- `feedback_id` (INTEGER, PK), `manager_name`, `cluster_id`, `issue_correct` (INT), `recommendation_useful` (INT), `approve_fix` (INT), `satisfaction_rating` (INT 1-5), `comments`, `created_at`.

### 6. `system_config` & `edge_case_logs`
- `system_config`: `key` (PK), `value`, `updated_at` (tracks `active_workflow` mode: `ai` vs `legacy`).
- `edge_case_logs`: `log_id` (PK), `ticket_id`, `case_type`, `description`, `action_taken`, `status`, `timestamp`.

---

## REST API Endpoints Reference

Base URL: `http://localhost:5000/api`

### 1. Dashboard Metrics
- **`GET /api/dashboard`**
  - **Description**: Returns executive metrics summary.
  - **Response 200 OK**:
    ```json
    {
      "total_tickets": 5000,
      "open_tickets": 750,
      "closed_tickets": 4250,
      "recurring_clusters_count": 8,
      "demand_reduction_pct": 34.2,
      "total_cost_saved_usd": 72500.00
    }
    ```

### 2. Demand Miner ML Engine
- **`POST /api/miner/cluster`**
  - **Description**: Executes text mining over tickets.
  - **Request Body**:
    ```json
    {
      "algorithm": "KMeans",
      "n_clusters": 8,
      "eps": 0.4
    }
    ```
    *Supported `algorithm` values: `"KMeans"`, `"DBSCAN"`, `"HDBSCAN"`, `"Agglomerative"`, `"SentenceTransformers"`.*
  - **Response 200 OK**: Returns array of cluster objects with $S_{\text{priority}}$, effort hours, recurrence intervals, and recommended fixes.

### 3. Machine Learning Benchmarks
- **`GET /api/benchmarks/run`**
  - **Description**: Evaluates KMeans, DBSCAN, HDBSCAN, Agglomerative, Sentence-Transformers, and Keyword Baseline against ground-truth tags.
  - **Response 200 OK**:
    ```json
    {
      "status": "success",
      "benchmarks": {
        "HDBSCAN (Hierarchical Density)": {
          "precision": 64.76,
          "recall": 77.5,
          "f1_score": 69.52,
          "purity": 78.0,
          "accuracy": 77.5,
          "execution_time_sec": 0.0857
        }
      }
    }
    ```

### 4. Edge Cases Simulator
- **`POST /api/edge-cases/simulate`**
  - **Description**: Runs edge case detector for duplicates, missing descriptions, and category mismatches.
  - **Response 200 OK**: Returns JSON resolution logs.

### 5. Workflow Coexistence & Rollback
- **`POST /api/workflow/toggle`**: Request body `{"workflow": "ai"}` or `{"workflow": "legacy"}`.
- **`POST /api/workflow/rollback`**: Reverts system to legacy workflow with zero data loss.

### 6. Stakeholder Feedback
- **`GET /api/feedback`**: Returns manager reviews and average rating metrics.
- **`POST /api/feedback`**: Form submission endpoint for manager feedback.

### 7. Ticket Management & Reports Export
- **`GET /api/tickets`**: Searchable and paginated tickets.
- **`GET /api/tickets/export`**: Downloads full tickets database as CSV.
- **`GET /api/reports/download/<report_type>/<format>`**: Downloads PDF or CSV reports.

---

## Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism & Themes), JavaScript (ES6+), Bootstrap 5, Chart.js
- **Backend**: Python Flask (REST API)
- **Database**: SQLite3 (`demand_miner.db`)
- **Machine Learning & NLP**: Scikit-learn (`TfidfVectorizer`, `KMeans`, `DBSCAN`, `HDBSCAN`, `AgglomerativeClustering`, `TruncatedSVD`), `sentence_transformers`
- **PDF Generation**: ReportLab
- **Data Utilities**: Pandas, NumPy

---

## Directory Structure

```
coe project/
├── app.py                      # Main Flask application entry point & REST controllers
├── database.py                 # SQLite database initialization & schema helpers
├── dataset_generator.py        # Synthetic 10,000 ticket dataset generator
├── requirements.txt            # Python dependencies
├── service_desk_tickets.csv    # Seed dataset (5,002 tickets)
├── README.md                   # Comprehensive guide, API & Schema docs
├── tests/
│   └── test_suite.py           # Automated unit test suite (18 unit tests)
├── ml_engine/
│   ├── __init__.py
│   ├── preprocessor.py         # RegEx text cleaning and domain stop-word filtering
│   ├── vectorizer.py           # Sublinear TF-IDF & Sentence-Transformers Dense Vectorizer
│   ├── clusterer.py            # KMeans, DBSCAN, HDBSCAN, Agglomerative & Baseline clusterers
│   ├── evaluator.py            # Precision, Recall, F1, Accuracy, Purity & Runtime benchmarks
│   └── fix_recommender.py      # Prioritization Scoring Formula ($S_priority$) & ROI Engine
├── failure_cases/
│   ├── __init__.py
│   └── edge_case_handler.py    # Detector & handler for duplicate, missing, and misclassified tickets
├── reports/
│   ├── __init__.py
│   └── report_generator.py     # Downloadable PDF & CSV report generator (6 report types)
├── docs/
│   ├── system_architecture.md  # System Architecture, NLP Specs, Formulas & Benchmarks
│   ├── er_diagram.md           # Entity Relationship Diagram & Schema
│   ├── api_documentation.md    # REST API endpoints reference
│   ├── user_manual.md          # User & Service Manager Guide
│   ├── student_phase_report.md # Academic Student Phase Report
│   └── presentation_slides.md  # Presentation deck artifact
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphism & dark/light theme CSS
│   └── js/
│       ├── main.js             # UI interactions & theme toggle logic
│       └── charts.js           # Chart.js graphs & benchmark visualization
└── templates/
    ├── base.html               # Base layout with sidebar, navbar, dark mode toggle
    ├── dashboard.html          # Real-time metrics & top recurring issues summary
    ├── tickets.html            # Ticket Management (CRUD, filter, search, CSV import/export)
    ├── miner.html              # Recurring Demand Miner ML clustering
    ├── fix_recommendations.html # Permanent Fix Engine with ROI & cost savings metrics
    ├── benchmarks.html         # ML Model Comparison & Experiments
    ├── edge_cases.html         # Failure Cases simulator & resolution logs
    ├── workflow_toggle.html    # Legacy vs AI Coexistence Mode & Rollback Demo
    ├── feedback.html           # Stakeholder Validation module
    ├── reports.html            # PDF & CSV report download center
    └── documentation.html      # Technical Docs, Architecture, ER Diagram & Math Formulas
```

---

## Quick Start Guide

### 1. Prerequisites
Ensure Python 3.9+ is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
Seed the SQLite database with 5,000+ realistic service desk tickets:
```bash
python database.py
```

### 4. Run Automated Unit Tests
Execute the unit test suite to verify system integrity:
```bash
python -m unittest tests/test_suite.py
```

### 5. Run the Application
Start the Flask application server:
```bash
python app.py
```

Open your browser and navigate to:
**`http://localhost:5000`**
