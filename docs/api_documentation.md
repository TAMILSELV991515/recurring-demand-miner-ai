# REST API Documentation - Recurring Demand Miner

## Base URL
`http://localhost:5000/api`

---

## Endpoints

### 1. Dashboard Metrics
- **`GET /api/dashboard`**
  - Returns executive metrics summary (Total tickets, Open tickets, Closed tickets, Recurring clusters count, Total potential cost savings, Channel breakdown, Monthly trend data).
  - **Response 200 OK**:
    ```json
    {
      "total_tickets": 5000,
      "open_tickets": 750,
      "closed_tickets": 4250,
      "recurring_clusters_count": 6,
      "demand_reduction_pct": 34.2,
      "total_cost_saved_usd": 12450.00
    }
    ```

---

### 2. Ticket Management
- **`GET /api/tickets`**
  - Supports query filters `?search=print&category=Hardware&status=Closed&page=1`.
- **`POST /api/tickets`**
  - Creates a new ticket.
- **`PUT /api/tickets/<id>`**
  - Updates an existing ticket.
- **`DELETE /api/tickets/<id>`**
  - Deletes a ticket by ID.
- **`POST /api/tickets/import`**
  - Imports tickets from uploaded CSV file.
- **`GET /api/tickets/export`**
  - Exports current tickets database to downloadable CSV file.

---

### 3. Demand Miner ML Engine
- **`POST /api/miner/cluster`**
  - Request body: `{"algorithm": "KMeans", "n_clusters": 8}` or `{"algorithm": "DBSCAN", "eps": 0.4}`.
  - Returns list of identified clusters with recurrence intervals, effort hours, confidence scores, and recommended permanent fixes.

---

### 4. ML Model Benchmarks
- **`GET /api/benchmarks/run`**
  - Runs comparative benchmark of KMeans, DBSCAN, and Keyword Matching baseline. Returns Precision, Recall, F1 Score, Execution Time, and Accuracy.

---

### 5. Edge Cases Simulator
- **`POST /api/edge-cases/simulate`**
  - Runs automated edge case detector and returns live resolution log for (1) Duplicate tickets, (2) Missing descriptions, (3) Conflicting categories.

---

### 6. Workflow Coexistence & Rollback
- **`POST /api/workflow/toggle`**
  - Body: `{"workflow": "ai"}` or `{"workflow": "legacy"}`.
- **`POST /api/workflow/rollback`**
  - Reverts system state to legacy mode without loss of data.

---

### 7. Stakeholder Feedback
- **`GET /api/feedback`**: Fetches all service manager feedback entries and average satisfaction rating.
- **`POST /api/feedback`**: Submits new manager feedback.

---

### 8. Downloadable Reports
- **`GET /api/reports/download/<report_type>/<format>`**
  - `report_type`: `recurring_incidents`, `permanent_fixes`, `asset_impact`, `engineer_performance`, `cost_savings`, `monthly_analysis`.
  - `format`: `pdf` or `csv`.
