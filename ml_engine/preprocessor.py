import re

"""
ml_engine/preprocessor.py
=========================
Text Preprocessing and RegEx Cleaning Module for Enterprise Service Desk Tickets.

This module normalizes raw ticket titles and short descriptions submitted across
multiple intake channels (Email, Chat, Phone, and Web Portal) into clean token sequences.
It applies case normalization, strips URLs/email noise, removes non-alphanumeric symbols,
and filters out generic IT support domain stop-words.
"""

# Custom set of domain-specific IT support stop-words alongside standard English stop-words
STOP_WORDS = set([
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'can\'t', 'cannot',
    'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each',
    'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d',
    'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i',
    'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s',
    'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
    'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll',
    'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs',
    'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve',
    'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll',
    'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which', 'while',
    'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d', 'you\'ll',
    'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves', 
    'issue', 'ticket', 'problem', 'user', 'please', 'help', 'request', 'hi', 'hello', 'thanks', 'regards'
])

def clean_text(text):
    """
    Cleans and normalizes unstructured ticket text.

    Args:
        text (str): Raw input text string from ticket description or title.

    Returns:
        str: Space-separated normalized token string suitable for vectorization.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Step 1: Case Normalization
    text = text.lower()
    
    # Step 2: Remove URLs and Email addresses
    text = re.sub(r'http\S+|www\S+|\S+@\S+', '', text)
    
    # Step 3: Remove non-alphanumeric characters except basic spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Step 4: Remove standalone numeric sequences
    text = re.sub(r'\b\d+\b', '', text)
    
    # Step 5: Filter stop-words and single-letter characters
    tokens = [w for w in text.split() if w not in STOP_WORDS and len(w) > 1]
    
    return " ".join(tokens)
