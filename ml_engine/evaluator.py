import time
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from collections import Counter
from .preprocessor import clean_text
from .vectorizer import TextVectorizer, DenseEmbedder
from .clusterer import KMeansClusterer, DBSCANClusterer, HDBSCANClusterer, AgglomerativeClusterer, KeywordBaselineClusterer

"""
ml_engine/evaluator.py
======================
Machine Learning Benchmarking & Performance Evaluation Engine.

Computes Precision, Recall, F1 Score, Accuracy, Cluster Purity %, and Execution Time (sec)
comparing KMeans, DBSCAN, HDBSCAN, Agglomerative, Sentence-Transformers, and Keyword Baseline.
"""

def evaluate_models(tickets_data):
    """
    Evaluates KMeans, DBSCAN, HDBSCAN, Agglomerative, Sentence-Transformers, and Keyword Baseline 
    against ground truth true_cluster_id tags.

    Args:
        tickets_data (list of dict): Ticket records containing short_description and true_cluster_id.

    Returns:
        dict: Performance metrics (precision, recall, f1_score, accuracy, purity, execution_time_sec).
    """
    corpus = [clean_text(t['short_description']) for t in tickets_data]
    y_true = [t['true_cluster_id'] for t in tickets_data]
    
    # Vectorize using TF-IDF
    start_vec = time.time()
    vectorizer = TextVectorizer(max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    vec_time = time.time() - start_vec
    
    results = {}
    
    # 1. KMeans (TF-IDF) Evaluation
    start_k = time.time()
    kmeans = KMeansClusterer(n_clusters=8)
    k_labels = kmeans.fit_predict(tfidf_matrix)
    k_time = (time.time() - start_k) + vec_time
    mapped_k_labels = map_clusters_to_ground_truth(k_labels, y_true)
    results['KMeans (TF-IDF)'] = compute_metrics(y_true, mapped_k_labels, k_labels, k_time)
    
    # 2. DBSCAN (Density) Evaluation
    start_d = time.time()
    dbscan = DBSCANClusterer(eps=0.4, min_samples=3)
    d_labels = dbscan.fit_predict(tfidf_matrix)
    d_time = (time.time() - start_d) + vec_time
    mapped_d_labels = map_clusters_to_ground_truth(d_labels, y_true)
    results['DBSCAN (Density)'] = compute_metrics(y_true, mapped_d_labels, d_labels, d_time)
    
    # 3. HDBSCAN (Hierarchical Density) Evaluation
    start_h = time.time()
    hdbscan = HDBSCANClusterer(min_cluster_size=3, min_samples=2)
    h_labels = hdbscan.fit_predict(tfidf_matrix)
    h_time = (time.time() - start_h) + vec_time
    mapped_h_labels = map_clusters_to_ground_truth(h_labels, y_true)
    results['HDBSCAN (Hierarchical Density)'] = compute_metrics(y_true, mapped_h_labels, h_labels, h_time)

    # 4. Agglomerative (Hierarchical Linkage) Evaluation
    start_a = time.time()
    agg = AgglomerativeClusterer(n_clusters=8, metric='cosine', linkage='average')
    a_labels = agg.fit_predict(tfidf_matrix)
    a_time = (time.time() - start_a) + vec_time
    mapped_a_labels = map_clusters_to_ground_truth(a_labels, y_true)
    results['Agglomerative (Hierarchical)'] = compute_metrics(y_true, mapped_a_labels, a_labels, a_time)

    # 5. Sentence-Transformers / Dense Embedding + KMeans
    start_st_vec = time.time()
    embedder = DenseEmbedder()
    dense_matrix = embedder.fit_transform(corpus)
    st_vec_time = time.time() - start_st_vec
    
    start_st_k = time.time()
    st_kmeans = KMeansClusterer(n_clusters=8)
    st_k_labels = st_kmeans.fit_predict(dense_matrix)
    st_time = (time.time() - start_st_k) + st_vec_time
    mapped_st_k_labels = map_clusters_to_ground_truth(st_k_labels, y_true)
    results['Sentence-Transformers + KMeans'] = compute_metrics(y_true, mapped_st_k_labels, st_k_labels, st_time)

    # 6. Keyword Baseline Evaluation
    start_b = time.time()
    baseline = KeywordBaselineClusterer()
    b_labels = baseline.predict([t['short_description'] for t in tickets_data])
    b_time = time.time() - start_b
    results['Keyword Baseline'] = compute_metrics(y_true, b_labels, b_labels, b_time)
    
    return results

def map_clusters_to_ground_truth(cluster_labels, y_true):
    label_mapping = {}
    clusters = set(cluster_labels)
    
    for c in clusters:
        if c == -1: # DBSCAN / HDBSCAN noise
            label_mapping[c] = "NONE"
            continue
        indices = [i for i, l in enumerate(cluster_labels) if l == c]
        true_labels = [y_true[i] for i in indices]
        if true_labels:
            most_common = Counter(true_labels).most_common(1)[0][0]
            label_mapping[c] = most_common
        else:
            label_mapping[c] = "NONE"
        
    return [label_mapping[c] for c in cluster_labels]

def calculate_cluster_purity(y_true, raw_cluster_labels):
    """Calculates Cluster Purity metric (0.0 to 100.0%)."""
    if y_true is None or raw_cluster_labels is None or len(y_true) == 0 or len(raw_cluster_labels) == 0 or len(y_true) != len(raw_cluster_labels):
        return 0.0
    
    total_correct = 0
    raw_list = list(raw_cluster_labels)
    clusters = set(raw_list)
    for c in clusters:
        indices = [i for i, l in enumerate(raw_list) if l == c]
        true_labels_in_c = [y_true[i] for i in indices]
        if true_labels_in_c:
            most_common_cnt = Counter(true_labels_in_c).most_common(1)[0][1]
            total_correct += most_common_cnt
            
    purity = (total_correct / len(y_true)) * 100.0
    return round(purity, 2)

def compute_metrics(y_true, y_pred, raw_cluster_labels, exec_time):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    purity = calculate_cluster_purity(y_true, raw_cluster_labels)
    
    return {
        'precision': round(float(prec) * 100, 2),
        'recall': round(float(rec) * 100, 2),
        'f1_score': round(float(f1) * 100, 2),
        'accuracy': round(float(acc) * 100, 2),
        'purity': purity,
        'execution_time_sec': round(float(exec_time), 4)
    }
