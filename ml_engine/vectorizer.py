from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

"""
ml_engine/vectorizer.py
=======================
Text Vectorization & Feature Representation Module.

Provides dual-representation vectorization for IT service desk tickets:
1. TF-IDF Vectorizer with sublinear term frequency scaling and L2 normalization.
2. Dense Semantic Embeddings using SentenceTransformers (all-MiniLM-L6-v2)
   with Latent Semantic Analysis (TruncatedSVD LSA) dense fallback.
"""

class TextVectorizer:
    """
    Sublinear TF-IDF Text Vectorizer.
    
    Transforms normalized ticket corpora into sparse TF-IDF feature matrices.
    Applies sublinear scaling: tf_sub = 1 + log(tf) to dampen high-frequency term bias.
    """
    def __init__(self, max_features=1000, ngram_range=(1, 2)):
        """
        Initialize TF-IDF Vectorizer.
        
        Args:
            max_features (int): Maximum vocabulary size for feature extraction.
            ngram_range (tuple): Range of n-gram dimensions (unigrams & bigrams).
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            sublinear_tf=True
        )
        self.feature_names = []
        
    def fit_transform(self, corpus):
        """Fits vectorizer model on ticket corpus and returns L2 normalized sparse matrix."""
        if not corpus:
            return np.array([])
        matrix = self.vectorizer.fit_transform(corpus)
        self.feature_names = self.vectorizer.get_feature_names_out()
        return matrix
        
    def transform(self, corpus):
        """Transforms new ticket corpus using fitted TF-IDF vocabulary."""
        return self.vectorizer.transform(corpus)


class DenseEmbedder:
    """
    Dense Semantic Embedding Vectorizer using SentenceTransformers or LSA Fallback.
    
    Generates dense continuous vector embeddings capturing deep semantic intent.
    Falls back gracefully to Latent Semantic Analysis (TruncatedSVD on TF-IDF) if
    sentence_transformers library is not installed in the local environment.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2', n_components=64):
        self.model_name = model_name
        self.n_components = n_components
        self.st_model = None
        self.svd_model = None
        self.tfidf = None

        if SentenceTransformer is not None:
            try:
                self.st_model = SentenceTransformer(model_name)
            except Exception:
                self.st_model = None

    def fit_transform(self, corpus):
        """Generates L2 normalized dense feature embeddings for corpus."""
        if not corpus:
            return np.array([])
        
        if self.st_model is not None:
            embeddings = self.st_model.encode(corpus, show_progress_bar=False)
            return normalize(embeddings)
        else:
            # Fallback: Latent Semantic Analysis (TF-IDF + TruncatedSVD)
            self.tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), sublinear_tf=True)
            tfidf_mat = self.tfidf.fit_transform(corpus)
            n_comp = min(self.n_components, max(2, tfidf_mat.shape[1] - 1), tfidf_mat.shape[0])
            self.svd_model = TruncatedSVD(n_components=n_comp, random_state=42)
            dense_mat = self.svd_model.fit_transform(tfidf_mat)
            return normalize(dense_mat)


def compute_cosine_similarity(matrix):
    """
    Computes pairwise Cosine Similarity matrix between all ticket vector representations.

    Args:
        matrix: Sparse or dense feature matrix (N x D).

    Returns:
        ndarray: Symmetric Cosine Similarity matrix (N x N) with values between 0.0 and 1.0.
    """
    return cosine_similarity(matrix)
