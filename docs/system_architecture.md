# System Architecture & Technical Specifications - Recurring Demand Miner

## Overview
The Recurring Demand Miner is an intelligent Enterprise Service Desk problem management platform designed to automate incident text vectorization, machine learning clustering, recurrence interval calculation, and permanent fix recommendation.

---

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
| - SQLite Database        |  | - Preprocessor & RegEx  |  | - PDF Generator       |
| - Tickets & Clusters     |  | - TF-IDF Vectorizer     |  |   (ReportLab)         |
| - Stakeholder Feedback   |  | - Sentence-Transformers |  | - CSV Export Engine   |
| - System Workflow Config |  | - KMeans/DBSCAN/HDBSCAN |  |                       |
| - Edge Case Logs         |  | - Agglomerative Cluster |  |                       |
|                          |  | - Prioritization Engine |  |                       |
|                          |  | - Benchmark Evaluator   |  |                       |
+--------------------------+  +-------------------------+  +-----------------------+
```

---

## Exact NLP and Clustering Pipeline

### 1. Text Preprocessing & Cleaning
- **Lowercasing & Normalization**: Standardizes all ticket title and short description text to lowercase.
- **Noise & Entity Stripping**: Removes URLs (`http\S+`), email addresses (`\S+@\S+`), and special non-alphanumeric symbols.
- **Stop-Word Removal**: Filters standard English stop-words plus IT domain noise (`issue`, `ticket`, `problem`, `user`, `please`, `help`, `request`).
- **N-Gram Tokenization**: Extracts unigrams and bigrams ($1 \le n \le 2$) to preserve contextual domain phrases (e.g., *"spooler service"*, *"vpn disconnect"*, *"token expired"*).

### 2. Feature Representation & Vectorization
- **TF-IDF Vectorization ($V_{\text{TF-IDF}}$)**:
  - Sublinear Term Frequency Scaling: $\text{tf}_{\text{sub}} = 1 + \log(\text{tf})$
  - Smoothed Inverse Document Frequency: $\text{idf}(t) = \log\left(\frac{1 + N}{1 + \text{df}(t)}\right) + 1$
  - Vector Normalization: $L_2$ norm constraint $\|\mathbf{v}\|_2 = 1$.
- **Dense Semantic Embeddings ($V_{\text{Dense}}$)**:
  - Encodes deep semantic intent using Sentence-Transformers (`all-MiniLM-L6-v2`) or Latent Semantic Analysis (TruncatedSVD LSA) dense projections.

### 3. Machine Learning Clustering Algorithms
- **KMeans Clustering**: Partitions vector space into $K$ hyper-spherical clusters by minimizing inertia (within-cluster sum-of-squares).
- **DBSCAN (Density-Based Spatial Clustering)**: Group points with high density ($\epsilon=0.4$, $\text{min\_samples}=3$) using Cosine metric; flags low-density outliers as noise ($-1$).
- **HDBSCAN (Hierarchical Density-Based Clustering)**: Builds a condensed hierarchy of density-based clusters without requiring a static $\epsilon$ threshold.
- **Agglomerative Clustering**: Bottom-up hierarchical merging utilizing Cosine distance and Average/Ward linkage criteria.
- **Keyword Baseline**: Naive rule-based matching over predefined dictionary rules for benchmark comparison.

---

## Mathematical Formulas for Prioritization & ROI Scoring

### 1. Recurring Demand Prioritization Score ($S_{\text{priority}}$)
Calculates the relative urgency of problem management intervention by weighting ticket frequency, workaround reliance, total support effort, and business impact:

$$S_{\text{priority}} = (w_f \cdot N_{\text{tickets}}) + (w_w \cdot P_{\text{workaround}}) + (w_e \cdot E_{\text{total}}) + I_{\text{impact}}$$

Where:
- $N_{\text{tickets}}$ = Total ticket frequency in cluster
- $P_{\text{workaround}}$ = Percentage of tickets resolved via temporary workaround ($\% = \frac{N_{\text{workaround}}}{N_{\text{tickets}}} \times 100$)
- $E_{\text{total}}$ = Total accumulated support effort in engineer hours ($\sum_{i \in \text{cluster}} e_i$)
- $w_f = 0.4$ (Frequency weight coefficient)
- $w_w = 0.3$ (Workaround weight coefficient)
- $w_e = 0.3$ (Effort weight coefficient)
- $I_{\text{impact}}$ = Discrete business impact weight scalar:

$$I_{\text{impact}} = \begin{cases} 30 & \text{if } N_{\text{tickets}} \ge 15 \text{ or } E_{\text{total}} \ge 20 \text{ (CRITICAL)} \\ 20 & \text{if } N_{\text{tickets}} \ge 8 \text{ or } E_{\text{total}} \ge 10 \text{ (HIGH)} \\ 10 & \text{otherwise (MEDIUM)} \end{cases}$$

### 2. Recurrence Interval ($\Delta t_{\text{avg}}$)
$$\Delta t_{\text{avg}} = \frac{1}{M-1} \sum_{i=1}^{M-1} (t_{i+1} - t_i)$$

where $t_1 \le t_2 \le \dots \le t_M$ are ticket creation dates sorted chronologically.

### 3. Cluster Purity Metric
$$\text{Purity}(\Omega, C) = \frac{1}{N} \sum_{k=1}^{K} \max_{j} |\omega_k \cap c_j| \times 100\%$$

---

## Unit Testing Architecture & Error Boundaries Specification

### 1. Granular Unit Test Suite (`tests/test_suite.py`)
The system includes an automated test runner built on Python's `unittest` framework covering 18 test cases across 7 modules:

1. **`TestTextPreprocessor`**: Validates regex lowercasing, URL/email stripping, IT stopword filtering (`clean_text`), and empty/None handling.
2. **`TestTextVectorizer`**: Tests TF-IDF feature matrix generation, vocabulary creation, $L_2$ normalization, and `DenseEmbedder` (SBERT & LSA fallback).
3. **`TestClusteringAlgorithms`**: Tests `KMeansClusterer`, `DBSCANClusterer`, `HDBSCANClusterer`, `AgglomerativeClusterer`, and `KeywordBaselineClusterer` output shape and label assignment.
4. **`TestPrioritizationEngine`**: Validates $S_{\text{priority}}$ calculation, business impact scalar assignment ($I_{\text{impact}}$), recurrence interval calculation, and ROI time/cost savings.
5. **`TestModelEvaluatorAndMetrics`**: Validates `evaluate_models` and `calculate_cluster_purity` metric calculations.
6. **`TestEdgeCaseResilienceHandler`**: Tests automated detection and resolution of duplicate tickets, missing descriptions, and category mismatches.
7. **`TestRESTAPIEndpointsAndErrorBoundaries`**: Tests REST endpoints (`/api/dashboard`, `/api/miner/cluster`, `/api/benchmarks/run`, `/api/workflow/toggle`) and HTTP 404/500 error boundaries.

**Test Execution Command:**
```bash
python -m unittest tests/test_suite.py
```

### 2. System Error Boundaries & Fallback Strategy
- **Zero-Vector Protection Boundary**: `AgglomerativeClusterer` injects $1e-9$ epsilon to rows with zero norm before computing Cosine distance, eliminating `ValueError: Cosine affinity cannot be used when X contains zero vectors`.
- **HDBSCAN Library Boundary**: Gracefully falls back to Cosine DBSCAN density clustering if native HDBSCAN C-extension binaries fail to import in limited environments.
- **Dense Embedder LSA Boundary**: `DenseEmbedder` checks for `sentence_transformers`; if absent, it dynamically switches to Latent Semantic Analysis (TruncatedSVD LSA) without breaking vectorizer interfaces.
- **HTTP Endpoint Middleware Boundaries**: `@app.errorhandler(403)`, `@app.errorhandler(404)`, and `@app.errorhandler(500)` return structured JSON error payloads for API calls and styled glassmorphic pages for UI views.

---

## Empirical ML Benchmarks

Empirical performance evaluation comparing clustering models against true incident categories ($N=1,000$ seed tickets):

| Model / Algorithm | Precision % | Recall % | F1 Score % | Cluster Purity % | Accuracy % | Execution Time (sec) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **HDBSCAN (Hierarchical Density)** | **64.76%** | **77.50%** | **69.52%** | **78.00%** | **77.50%** | 0.0857s |
| **DBSCAN (Density-Based)** | **64.76%** | **77.50%** | **69.52%** | **77.50%** | **77.50%** | 0.0200s |
| **Sentence-Transformers + KMeans** | 46.88% | 67.00% | 54.66% | 67.00% | 67.00% | 0.1185s |
| **KMeans (TF-IDF)** | 46.88% | 67.00% | 54.66% | 67.00% | 67.00% | 3.1206s |
| **Agglomerative (Hierarchical)** | 53.71% | 56.00% | 52.05% | 56.00% | 56.00% | 0.2312s |
| **Keyword Baseline (Rule-Based)** | 35.08% | 56.50% | 42.73% | 60.50% | 56.50% | 0.0028s |
