import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
try:
    from sklearn.cluster import HDBSCAN
except ImportError:
    HDBSCAN = None
from collections import Counter, defaultdict
import re

"""
ml_engine/clusterer.py
======================
Unsupervised Machine Learning & Rule-Based Clustering Suite.

Implements multi-algorithm clustering models for recurring demand mining:
1. KMeans Clusterer: Centroid-based partitioning minimizing vector inertia.
2. DBSCAN Clusterer: Cosine density-based spatial clustering isolating noise.
3. HDBSCAN Clusterer: Hierarchical density-based clustering with variable density profiles.
4. Agglomerative Clusterer: Bottom-up hierarchical merging with Cosine affinity.
5. Keyword Baseline Clusterer: Rule-based keyword matching algorithm for comparative evaluation.
"""

class KMeansClusterer:
    """KMeans Partitioning Clusterer."""
    def __init__(self, n_clusters=8, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model = None

    def fit_predict(self, matrix):
        actual_clusters = min(self.n_clusters, max(1, matrix.shape[0]))
        self.model = KMeans(n_clusters=actual_clusters, random_state=self.random_state, n_init=10)
        labels = self.model.fit_predict(matrix)
        return labels


class DBSCANClusterer:
    """Density-Based Spatial Clustering of Applications with Noise (DBSCAN)."""
    def __init__(self, eps=0.5, min_samples=3):
        self.eps = eps
        self.min_samples = min_samples
        self.model = None

    def fit_predict(self, matrix):
        self.model = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='cosine')
        labels = self.model.fit_predict(matrix)
        return labels


class HDBSCANClusterer:
    """Hierarchical Density-Based Spatial Clustering of Applications with Noise (HDBSCAN)."""
    def __init__(self, min_cluster_size=3, min_samples=2):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.model = None

    def fit_predict(self, matrix):
        dense_matrix = matrix.toarray() if hasattr(matrix, 'toarray') else np.asarray(matrix)
        if HDBSCAN is not None:
            actual_min_size = min(self.min_cluster_size, max(2, dense_matrix.shape[0]))
            try:
                self.model = HDBSCAN(min_cluster_size=actual_min_size, min_samples=self.min_samples, metric='euclidean', copy=True)
            except TypeError:
                self.model = HDBSCAN(min_cluster_size=actual_min_size, min_samples=self.min_samples, metric='euclidean')
            labels = self.model.fit_predict(dense_matrix)
        else:
            # Fallback to DBSCAN if HDBSCAN import fails
            db = DBSCAN(eps=0.45, min_samples=self.min_samples, metric='cosine')
            labels = db.fit_predict(dense_matrix)
        return labels


class AgglomerativeClusterer:
    """Hierarchical Agglomerative Clustering with Cosine or Euclidean distance."""
    def __init__(self, n_clusters=8, metric='cosine', linkage='average'):
        self.n_clusters = n_clusters
        self.metric = metric
        self.linkage = linkage
        self.model = None

    def fit_predict(self, matrix):
        dense_matrix = matrix.toarray() if hasattr(matrix, 'toarray') else np.array(matrix, copy=True)
        if self.metric == 'cosine' and dense_matrix.shape[0] > 0:
            row_norms = np.linalg.norm(dense_matrix, axis=1)
            zero_rows = (row_norms == 0)
            if np.any(zero_rows):
                dense_matrix[zero_rows] = 1e-9
        actual_clusters = min(self.n_clusters, max(1, dense_matrix.shape[0]))
        self.model = AgglomerativeClustering(
            n_clusters=actual_clusters,
            metric=self.metric,
            linkage=self.linkage
        )
        labels = self.model.fit_predict(dense_matrix)
        return labels


class KeywordBaselineClusterer:
    """Rule-based keyword baseline clustering for comparative evaluation."""
    def __init__(self):
        self.keywords_map = {
            'CL-PRINT-SPOOL-02': ['print', 'spooler', 'printer', 'paper', 'jam', 'queue'],
            'CL-ERP-BATCH-FAIL-02': ['erp', 'batch', 'job', 'fails', 'step', 'ledger'],
            'CL-EMAIL-QUOTA-03': ['mailbox', 'quota', 'email', 'outlook', 'send', 'receive'],
            'CL-VPN-AUTH-01': ['vpn', 'globalprotect', 'disconnect', 'mfa', 'radius', 'handshake'],
            'CL-BATTERY-DRAIN-04': ['battery', 'drain', 'shuts', 'power', 'charge', 'latitude'],
            'CL-SSO-TOKEN-EXPIRE': ['okta', 'sso', 'token', 'session', 'login', 'saml']
        }

    def predict(self, corpus):
        labels = []
        for text in corpus:
            text_lower = text.lower()
            matched = "NONE"
            max_matches = 0
            for cluster_id, kw_list in self.keywords_map.items():
                matches = sum(1 for kw in kw_list if kw in text_lower)
                if matches > max_matches and matches >= 2:
                    max_matches = matches
                    matched = cluster_id
            labels.append(matched)
        return labels


def extract_cluster_name(texts_in_cluster, feature_names=None, tfidf_matrix=None, sample_indices=None):
    """Generates a readable cluster name based on top TF-IDF keywords or most frequent title phrases."""
    if not texts_in_cluster:
        return "General Issue Cluster"
    
    words = []
    for text in texts_in_cluster:
        words.extend([w for w in re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()) if w not in ['issue', 'problem', 'request', 'user', 'fails', 'error', 'ticket']])
    
    top_words = Counter(words).most_common(3)
    if top_words:
        title_terms = " ".join([w[0].capitalize() for w in top_words])
        return f"{title_terms} Cluster"
    return "Unclassified Incident Cluster"
