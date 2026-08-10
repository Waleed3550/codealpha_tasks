import nltk
import string

_is_initialized = False
lemmatizer = None
stop_words = None

def initialize_nltk_resources():
    """
    Checks if required NLTK resources are available and downloads them if missing.
    """
    global _is_initialized, lemmatizer, stop_words
    
    if _is_initialized:
        return
        
    required_corpora = ['wordnet', 'stopwords']
    required_tokenizers = ['punkt', 'punkt_tab']
    
    missing_resources = []
    
    for resource in required_tokenizers:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except Exception:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                missing_resources.append(resource)
            
    for resource in required_corpora:
        try:
            nltk.data.find(f'corpora/{resource}')
        except Exception:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                missing_resources.append(resource)
                
    if missing_resources:
        raise RuntimeError(f"Backend NLP Initialization Error: Required NLTK resources ({', '.join(missing_resources)}) are missing and could not be downloaded. Please check server connectivity.")
            
    # Initialize NLTK objects lazily to prevent loading overhead or crashes on import
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import stopwords
    
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    _is_initialized = True


def preprocess_text(text):
    """
    Lowercases, tokenizes, removes punctuation, removes stopwords, and lemmatizes the input text.
    """
    initialize_nltk_resources()
    
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = nltk.word_tokenize(text)
    
    lemmatized_tokens = [
        lemmatizer.lemmatize(token) for token in tokens
        if token not in stop_words
    ]
    
    return " ".join(lemmatized_tokens)
