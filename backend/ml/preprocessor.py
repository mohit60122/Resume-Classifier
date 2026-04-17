"""
Text Preprocessor - Clean and preprocess resume text for ML pipeline.
"""
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (only first run)
nltk_packages = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
for pkg in nltk_packages:
    try:
        nltk.data.find(f'tokenizers/{pkg}' if 'punkt' in pkg else f'corpora/{pkg}')
    except LookupError:
        nltk.download(pkg, quiet=True)


def get_custom_stopwords() -> list:
    """Combine base English stopwords with resume-specific noise words."""
    try:
        base_sw = set(stopwords.words('english'))
    except LookupError:
        nltk.download('stopwords', quiet=True)
        base_sw = set(stopwords.words('english'))
        
    resume_sw = {
        'resume', 'experience', 'summary', 'contact', 'email', 'phone', 
        'skills', 'education', 'profile', 'work', 'project', 'projects', 
        'professional', 'name', 'details', 'personal', 'information',
        'date', 'birth', 'address', 'mobile', 'website', 'social', 'media',
        'status', 'marital', 'nationality', 'languages'
    }
    return list(base_sw.union(resume_sw))


def clean_text(text: str) -> str:
    """
    Clean raw resume text by removing noise.
    - URLs, emails, phone numbers
    - Special characters, extra whitespace
    - HTML tags
    """
    if not text:
        return ""
        
    # Convert to lowercase early
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', ' ', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', ' ', text)

    # Remove phone numbers
    text = re.sub(r'\+?\d[\d\s\-\(\)]{7,}\d', ' ', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # Remove special characters but keep spaces and basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Remove isolated single characters
    text = re.sub(r'\b[a-zA-Z]\b', ' ', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def preprocess(text: str) -> str:
    """
    Full preprocessing pipeline:
    1. Clean text
    2. Lowercase
    3. Tokenize
    4. Remove stopwords
    5. Lemmatize
    """
    # Step 1: Clean
    text = clean_text(text)

    if not text:
        return ""

    # Step 2: Lowercase
    text = text.lower()

    # Step 3: Tokenize
    tokens = word_tokenize(text)

    # Step 4: Remove stopwords and short tokens
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 2]

    # Step 5: Remove pure numbers
    tokens = [t for t in tokens if not t.isdigit()]

    # Step 6: Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    return ' '.join(tokens)
