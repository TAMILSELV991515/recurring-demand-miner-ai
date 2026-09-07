import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from collections import Counter, defaultdict
import re

class KMeansClusterer:
    def __init__(self, n_clusters=8, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model = None

    def fit_predict(self, matrix):
        # Adjust n_clusters if sample size is smaller
        actual_clusters = min(self.n_clusters, max(1, matrix.shape[0]))
        self.model = KMeans(n_clusters=actual_clusters, random_state=self.random_state, n_init=10)
        labels = self.model.fit_predict(matrix)
        return labels

class DBSCANClusterer:
    def __init__(self, eps=0.5, min_samples=3):
        self.eps = eps
        self.min_samples = min_samples
        self.model = None

    def fit_predict(self, matrix):
        self.model = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='cosine')
        labels = self.model.fit_predict(matrix)
        return labels

class KeywordBaselineClusterer:
    """Rule-based keyword baseline clustering for benchmarking comparison."""
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
        words.extend([w for w in re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()) if w not in ['issue', 'problem', 'request', 'user', 'fails', 'error']])
    
    top_words = Counter(words).most_common(3)
    if top_words:
        title_terms = " ".join([w[0].capitalize() for w in top_words])
        return f"{title_terms} Cluster"
    return "Unclassified Incident Cluster"
