from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TextVectorizer:
    def __init__(self, max_features=1000, ngram_range=(1, 2)):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            sublinear_tf=True
        )
        self.feature_names = []
        
    def fit_transform(self, corpus):
        if not corpus:
            return np.array([])
        matrix = self.vectorizer.fit_transform(corpus)
        self.feature_names = self.vectorizer.get_feature_names_out()
        return matrix
        
    def transform(self, corpus):
        return self.vectorizer.transform(corpus)

def compute_cosine_similarity(matrix):
    return cosine_similarity(matrix)
