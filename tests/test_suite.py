import unittest
import numpy as np
import os
import json
from datetime import datetime

# Import project ML engine & system modules
from ml_engine.preprocessor import clean_text
from ml_engine.vectorizer import TextVectorizer, DenseEmbedder
from ml_engine.clusterer import (
    KMeansClusterer,
    DBSCANClusterer,
    HDBSCANClusterer,
    AgglomerativeClusterer,
    KeywordBaselineClusterer,
    extract_cluster_name
)
from ml_engine.evaluator import evaluate_models, calculate_cluster_purity
from ml_engine.fix_recommender import analyze_and_rank_clusters
from failure_cases.edge_case_handler import detect_and_handle_edge_cases
from database import get_db_connection, init_db
import app as flask_app_module


class TestTextPreprocessor(unittest.TestCase):
    """Unit tests for text preprocessing, regex cleaning, and stopword stripping."""

    def test_clean_text_normal(self):
        raw_text = "User cannot connect to VPN on GlobalProtect! Please help."
        cleaned = clean_text(raw_text)
        self.assertIn("vpn", cleaned.split())       # Domain keyword preserved
        self.assertNotIn("please", cleaned)        # Generic stopword removed
        self.assertNotIn("help", cleaned)          # Generic stopword removed
        self.assertIn("globalprotect", cleaned)

    def test_clean_text_url_email_stripping(self):
        raw_text = "Check http://example.com/login and email support@company.com for printer spooler issue."
        cleaned = clean_text(raw_text)
        self.assertNotIn("http", cleaned)
        self.assertNotIn("support@company.com", cleaned)
        self.assertIn("printer", cleaned)
        self.assertIn("spooler", cleaned)

    def test_clean_text_empty_and_none(self):
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")


class TestTextVectorizer(unittest.TestCase):
    """Unit tests for TF-IDF and Dense Embedding Vectorizers."""

    def setUp(self):
        self.corpus = [
            "print spooler service fails repeatedly on win11",
            "vpn globalprotect disconnects during radius authentication",
            "outlook mailbox quota exceeded send receive error",
            "okta sso saml token expired user session login"
        ]

    def test_tfidf_vectorizer_fit_transform(self):
        vec = TextVectorizer(max_features=100)
        matrix = vec.fit_transform(self.corpus)
        self.assertEqual(matrix.shape[0], len(self.corpus))
        self.assertGreater(matrix.shape[1], 0)
        self.assertGreater(len(vec.feature_names), 0)

    def test_dense_embedder(self):
        embedder = DenseEmbedder()
        matrix = embedder.fit_transform(self.corpus)
        self.assertEqual(matrix.shape[0], len(self.corpus))
        self.assertGreater(matrix.shape[1], 0)


class TestClusteringAlgorithms(unittest.TestCase):
    """Unit tests for KMeans, DBSCAN, HDBSCAN, Agglomerative, and Baseline Clusterers."""

    def setUp(self):
        self.corpus = [
            "print spooler printer paper jam queue",
            "printer spooler driver error paper jam",
            "vpn globalprotect radius disconnect mfa failure",
            "vpn authentication radius handshake dropped",
            "outlook email mailbox quota full",
            "email quota exceeded send receive error"
        ]
        vec = TextVectorizer(max_features=100)
        self.matrix = vec.fit_transform(self.corpus)

    def test_kmeans_clusterer(self):
        clusterer = KMeansClusterer(n_clusters=3, random_state=42)
        labels = clusterer.fit_predict(self.matrix)
        self.assertEqual(len(labels), len(self.corpus))
        self.assertLessEqual(len(set(labels)), 3)

    def test_dbscan_clusterer(self):
        clusterer = DBSCANClusterer(eps=0.8, min_samples=2)
        labels = clusterer.fit_predict(self.matrix)
        self.assertEqual(len(labels), len(self.corpus))

    def test_hdbscan_clusterer(self):
        clusterer = HDBSCANClusterer(min_cluster_size=2, min_samples=1)
        labels = clusterer.fit_predict(self.matrix)
        self.assertEqual(len(labels), len(self.corpus))

    def test_agglomerative_clusterer(self):
        clusterer = AgglomerativeClusterer(n_clusters=3, metric='cosine', linkage='average')
        labels = clusterer.fit_predict(self.matrix)
        self.assertEqual(len(labels), len(self.corpus))

    def test_keyword_baseline_clusterer(self):
        baseline = KeywordBaselineClusterer()
        labels = baseline.predict(self.corpus)
        self.assertEqual(len(labels), len(self.corpus))


class TestPrioritizationEngine(unittest.TestCase):
    """Unit tests for priority score calculation and ROI estimation."""

    def test_prioritization_score_ranking(self):
        mock_tickets = [
            {
                'ticket_id': 'INC1001',
                'created_date': '2026-09-01 10:00',
                'category': 'Hardware',
                'short_description': 'print spooler printer paper jam queue',
                'affected_asset': 'EUC-PRN-01',
                'is_workaround': 1,
                'effort_hours': 2.5
            },
            {
                'ticket_id': 'INC1002',
                'created_date': '2026-09-02 11:00',
                'category': 'Hardware',
                'short_description': 'print spooler printer paper jam queue',
                'affected_asset': 'EUC-PRN-01',
                'is_workaround': 1,
                'effort_hours': 3.0
            },
            {
                'ticket_id': 'INC1003',
                'created_date': '2026-09-03 12:00',
                'category': 'Hardware',
                'short_description': 'print spooler printer paper jam queue',
                'affected_asset': 'EUC-PRN-01',
                'is_workaround': 0,
                'effort_hours': 1.5
            }
        ]
        clusters = analyze_and_rank_clusters(mock_tickets, algorithm='KMeans', n_clusters=1)
        self.assertGreater(len(clusters), 0)
        top_cluster = clusters[0]
        self.assertIn('priority_score', top_cluster)
        self.assertGreater(top_cluster['priority_score'], 0)
        self.assertIn('cost_saved_usd', top_cluster)


class TestModelEvaluatorAndMetrics(unittest.TestCase):
    """Unit tests for model evaluator metrics and cluster purity."""

    def test_calculate_cluster_purity(self):
        y_true = ['CL-PRINT', 'CL-PRINT', 'CL-VPN', 'CL-VPN']
        raw_labels = [0, 0, 1, 1]
        purity = calculate_cluster_purity(y_true, raw_labels)
        self.assertEqual(purity, 100.0)

    def test_evaluate_models_output_structure(self):
        sample_tickets = [
            {'short_description': 'print spooler paper jam', 'true_cluster_id': 'CL-PRINT'},
            {'short_description': 'printer spooler driver queue', 'true_cluster_id': 'CL-PRINT'},
            {'short_description': 'vpn globalprotect disconnect', 'true_cluster_id': 'CL-VPN'},
            {'short_description': 'vpn radius mfa failure', 'true_cluster_id': 'CL-VPN'}
        ]
        results = evaluate_models(sample_tickets)
        self.assertIn('KMeans (TF-IDF)', results)
        self.assertIn('DBSCAN (Density)', results)
        self.assertIn('HDBSCAN (Hierarchical Density)', results)
        self.assertIn('purity', results['KMeans (TF-IDF)'])


class TestEdgeCaseResilienceHandler(unittest.TestCase):
    """Unit tests for failure cases resilience suite."""

    def test_detect_and_handle_edge_cases(self):
        init_db()
        conn = get_db_connection()
        logs = detect_and_handle_edge_cases(conn)
        conn.close()
        self.assertIsInstance(logs, list)


class TestRESTAPIEndpointsAndErrorBoundaries(unittest.TestCase):
    """Unit tests for Flask REST API controller and error boundaries."""

    def setUp(self):
        init_db()
        flask_app_module.app.config['TESTING'] = True
        self.client = flask_app_module.app.test_client()

    def test_api_benchmark_run(self):
        res = self.client.get('/api/benchmarks/run')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('benchmarks', data)

    def test_api_miner_cluster_post(self):
        payload = {'algorithm': 'KMeans', 'n_clusters': 4}
        res = self.client.post('/api/miner/cluster', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')

    def test_api_workflow_toggle(self):
        res = self.client.post('/api/workflow/toggle', json={'workflow': 'ai'})
        self.assertEqual(res.status_code, 200)

    def test_api_404_error_boundary(self):
        res = self.client.get('/api/non_existent_endpoint_xyz')
        self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main()
