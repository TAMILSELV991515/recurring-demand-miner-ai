# System Architecture - Recurring Demand Miner

## Overview
The Recurring Demand Miner is an intelligent Enterprise Service Desk problem management platform designed to automate incident text vectorization, machine learning clustering, recurrence interval calculation, and permanent fix recommendation.

## Architectural Diagram

```
+-----------------------------------------------------------------------------------+
|                                   USER INTERFACE                                  |
|          Bootstrap 5 Dashboard / Modern Glassmorphism Admin Interface             |
|    - Real-time Trend Charts (Chart.js)       - Ticket Management & CSV Import/Export|
|    - ML Clustering Playground & Benchmarks   - Coexistence Mode & Rollback Demo   |
|    - Stakeholder Feedback & Manager Approval - Downloadable Reports (PDF / CSV)   |
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST API (JSON)
                                           v
+-----------------------------------------------------------------------------------+
|                                 FLASK REST API CORE                               |
|  app.py Routing Engine, Controller Endpoints & Middleware State Manager          |
+---------------+--------------------------+------------------------+---------------+
                |                          |                        |
                v                          v                        v
+---------------+----------+  +------------+------------+  +--------+---------------+
|     DATABASE LAYER       |  |     ML ENGINE LAYER     |  |   REPORT & EXPORT     |
|   (database.py)          |  |  (ml_engine/)           |  |   (reports/)          |
| - SQLite Database        |  | - TF-IDF Vectorizer     |  | - PDF Generator       |
| - Tickets & Clusters     |  | - KMeans & DBSCAN       |  |   (ReportLab)         |
| - Stakeholder Feedback   |  | - Cosine Similarity     |  | - CSV Export Engine   |
| - System Workflow Config |  | - Fix Recommender (ROI) |  |                       |
| - Edge Case Logs         |  | - Benchmark Evaluator   |  |                       |
+--------------------------+  +-------------------------+  +-----------------------+
```

## Data Processing Pipeline

1. **Intake & Ingestion**: Tickets arrive via Email, Chat, Phone, and Portal. Saved into SQLite database.
2. **Text Preprocessing**: Tokenization, lowercasing, stop-word removal, regex cleaning.
3. **Feature Extraction & Vectorization**: `TfidfVectorizer` computes TF-IDF matrix for title and short description fields.
4. **Clustering & Demand Mining**: KMeans or DBSCAN clusters similar incidents into semantic groups.
5. **Recurrence & Effort Analysis**: Computes recurrence intervals (delta days between incidents), workaround frequencies, and total engineer hours consumed.
6. **Problem Management Fix Engine**: Computes Priority Scores, Expected Ticket Reduction %, Estimated Time Saved, and Cost Saved ($).
7. **Stakeholder Approval**: Service Managers review recommendations and record feedback/approval.
