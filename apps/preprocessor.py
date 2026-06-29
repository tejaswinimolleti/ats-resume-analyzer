# app/preprocessor.py

import re
import spacy
import nltk
from nltk.corpus import stopwords

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Download NLTK data if not already present
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

STOP_WORDS = set(stopwords.words("english"))

# ─────────────────────────────────────────────
# SKILLS DICTIONARY — extend this list freely
# ─────────────────────────────────────────────
SKILLS_DB = [
    # Programming languages
    "python", "java", "javascript", "c++", "c#", "r", "sql", "scala",
    "typescript", "go", "rust", "kotlin", "swift",

    # ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "neural networks",
    "tensorflow", "keras", "pytorch", "scikit-learn", "xgboost", "lightgbm",

    # Data
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "data analysis", "data visualization", "feature engineering",
    "data preprocessing", "eda", "statistics",

    # Cloud & MLOps
    "aws", "gcp", "azure", "docker", "kubernetes", "mlflow",
    "airflow", "ci/cd", "git", "github",

    # Web
    "flask", "fastapi", "django", "react", "node.js", "rest api",
    "html", "css",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "redis",

    # Other
    "excel", "power bi", "tableau", "linux", "agile", "scrum"
]


def clean_text(text: str) -> str:
    """Lowercase, remove special characters and extra whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)   # keep only letters/numbers
    text = re.sub(r"\s+", " ", text)             # collapse multiple spaces
    return text.strip()


def remove_stopwords(text: str) -> str:
    """Remove common English stopwords."""
    words = text.split()
    filtered = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    return " ".join(filtered)


def extract_skills(text: str) -> list:
    """Match skills from SKILLS_DB against the text."""
    text_lower = text.lower()
    found = []
    for skill in SKILLS_DB:
        # Use word boundary matching so 'r' doesn't match 'react'
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_experience_years(text: str) -> float:
    """Try to extract years of experience from text."""
    patterns = [
        r"(\d+)\+?\s*years?\s*of\s*experience",
        r"experience\s*of\s*(\d+)\+?\s*years?",
        r"(\d+)\+?\s*years?\s*experience",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
    return 0.0


def extract_education(text: str) -> list:
    """Extract education-related keywords."""
    edu_keywords = [
        "b tech", "btech", "b.tech", "bachelor", "b.e", "be",
        "m tech", "mtech", "m.tech", "master", "mba", "phd",
        "computer science", "information technology", "electronics",
        "data science", "artificial intelligence"
    ]
    text_lower = text.lower()
    found = []
    for kw in edu_keywords:
        if kw in text_lower:
            found.append(kw)
    return list(set(found))


def extract_entities(text: str) -> dict:
    """Use spaCy NER to extract organizations and locations."""
    doc = nlp(text[:5000])  # spaCy works best under 5000 chars
    entities = {"organizations": [], "locations": []}
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["organizations"].append(ent.text.strip())
        elif ent.label_ in ("GPE", "LOC"):
            entities["locations"].append(ent.text.strip())
    # Deduplicate
    entities["organizations"] = list(set(entities["organizations"]))
    entities["locations"] = list(set(entities["locations"]))
    return entities


def preprocess(text: str) -> dict:
    """
    Master function — runs full NLP pipeline on any text.
    Returns a structured dict with all extracted features.
    """
    cleaned       = clean_text(text)
    no_stopwords  = remove_stopwords(cleaned)
    skills        = extract_skills(text)        # use original for better matching
    education     = extract_education(text)
    exp_years     = extract_experience_years(text)
    entities      = extract_entities(text)

    return {
        "original_text"  : text,
        "clean_text"     : cleaned,
        "tokens"         : no_stopwords,
        "skills"         : skills,
        "education"      : education,
        "experience_years": exp_years,
        "entities"       : entities,
        "word_count"     : len(text.split())
    }