import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from services.logger import logger

# Initialize NLTK resources silently
def download_nltk_resources():
    """
    Downloads NLTK resources required for text cleaning.
    Catches exceptions to prevent internet connection failures from crashing startup.
    """
    resources = ["stopwords", "wordnet", "omw-1.4"]
    for res in resources:
        try:
            nltk.download(res, quiet=True)
            logger.info(f"NLTK resource '{res}' checked/downloaded.")
        except Exception as e:
            logger.warning(f"Failed to download NLTK resource '{res}': {str(e)}")

# Perform NLTK resource setup
download_nltk_resources()

def clean_text_engine(text, use_stemming=False, use_lemmatization=True, remove_stopwords=True):
    """
    Cleanses, normalizes, and pre-processes raw text using NLTK utilities.
    
    Args:
        text (str): Raw input text.
        use_stemming (bool): Apply Porter Stemmer if True.
        use_lemmatization (bool): Apply WordNet Lemmatizer if True.
        remove_stopwords (bool): Filter out standard English stopwords if True.
        
    Returns:
        str: Cleansed and tokenized string.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
        
    # 1. Lowercase normalization
    text = text.lower()
    
    # 2. Punctuation & Special Character Removal (keep only space and alpha-numeric characters)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    
    # 3. Simple Tokenization (split by whitespace)
    tokens = text.split()
    
    # 4. Stopwords filtering
    if remove_stopwords:
        try:
            stop_words = set(stopwords.words("english"))
            tokens = [t for t in tokens if t not in stop_words]
        except Exception:
            # Fallback if stopwords resource is unavailable
            pass
            
    # 5. Lemmatization or Stemming
    if use_lemmatization:
        try:
            lemmatizer = WordNetLemmatizer()
            tokens = [lemmatizer.lemmatize(t) for t in tokens]
        except Exception as e:
            logger.warning(f"Lemmatization failed, skipping step: {str(e)}")
            
    elif use_stemming:
        try:
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(t) for t in tokens]
        except Exception as e:
            logger.warning(f"Stemming failed, skipping step: {str(e)}")
            
    # 6. Reconstruct string
    return " ".join(tokens)
