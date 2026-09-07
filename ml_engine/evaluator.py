import time
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from collections import Counter
from .preprocessor import clean_text
from .vectorizer import TextVectorizer
from .clusterer import KMeansClusterer, DBSCANClusterer, KeywordBaselineClusterer

def evaluate_models(tickets_data):
    """
    Evaluates KMeans, DBSCAN, and Keyword Baseline against ground truth true_cluster_id.
    Returns comparison dictionary with metrics and execution times.
    """
    corpus = [clean_text(t['short_description']) for t in tickets_data]
    y_true = [t['true_cluster_id'] for t in tickets_data]
    
    # Vectorize
    start_vec = time.time()
    vectorizer = TextVectorizer(max_features=1000)
    matrix = vectorizer.fit_transform(corpus)
    vec_time = time.time() - start_vec
    
    results = {}
    
    # 1. KMeans Evaluation
    start_k = time.time()
    kmeans = KMeansClusterer(n_clusters=8)
    k_labels = kmeans.fit_predict(matrix)
    k_time = (time.time() - start_k) + vec_time
    
    # Map cluster int labels to majority ground truth string
    mapped_k_labels = map_clusters_to_ground_truth(k_labels, y_true)
    results['KMeans (TF-IDF)'] = compute_metrics(y_true, mapped_k_labels, k_time)
    
    # 2. DBSCAN Evaluation
    start_d = time.time()
    dbscan = DBSCANClusterer(eps=0.4, min_samples=3)
    d_labels = dbscan.fit_predict(matrix)
    d_time = (time.time() - start_d) + vec_time
    
    mapped_d_labels = map_clusters_to_ground_truth(d_labels, y_true)
    results['DBSCAN (Density)'] = compute_metrics(y_true, mapped_d_labels, d_time)
    
    # 3. Keyword Baseline Evaluation
    start_b = time.time()
    baseline = KeywordBaselineClusterer()
    b_labels = baseline.predict([t['short_description'] for t in tickets_data])
    b_time = time.time() - start_b
    
    results['Keyword Baseline'] = compute_metrics(y_true, b_labels, b_time)
    
    return results

def map_clusters_to_ground_truth(cluster_labels, y_true):
    label_mapping = {}
    clusters = set(cluster_labels)
    
    for c in clusters:
        if c == -1: # DBSCAN noise
            label_mapping[c] = "NONE"
            continue
        indices = [i for i, l in enumerate(cluster_labels) if l == c]
        true_labels = [y_true[i] for i in indices]
        most_common = Counter(true_labels).most_common(1)[0][0]
        label_mapping[c] = most_common
        
    return [label_mapping[c] for c in cluster_labels]

def compute_metrics(y_true, y_pred, exec_time):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    return {
        'precision': round(float(prec) * 100, 2),
        'recall': round(float(rec) * 100, 2),
        'f1_score': round(float(f1) * 100, 2),
        'accuracy': round(float(acc) * 100, 2),
        'execution_time_sec': round(float(exec_time), 4)
    }
