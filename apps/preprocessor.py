# apps/preprocessor.py

import re
import spacy
import nltk
from nltk.corpus import stopwords

nlp = spacy.load("en_core_web_sm")

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

STOP_WORDS = set(stopwords.words("english"))

# ─────────────────────────────────────────────
# TECH WORDS TO FILTER FROM NER (false positives)
# ─────────────────────────────────────────────
TECH_NOISE = {
    "csv", "cgpa", "gpa", "sql", "git", "docker", "anaconda", "linux",
    "python", "java", "github", "certifications", "html", "css", "api",
    "json", "xml", "http", "rest", "aws", "gcp", "azure", "excel",
    "numpy", "pandas", "tensorflow", "keras", "pytorch", "flask",
    "django", "react", "node", "mongodb", "mysql", "sqlite", "redis",
    "tableau", "powerbi", "power bi", "kubernetes", "mlflow", "airflow",
    "scikit", "matplotlib", "seaborn", "plotly", "jupyter", "vscode",
    "android", "ios", "kotlin", "swift", "typescript", "javascript",
    "k-means", "linear regression", "logistic regression", "random forest",
    "neural network", "deep learning", "machine learning"
}

# ─────────────────────────────────────────────
# SKILLS DICTIONARY
# ─────────────────────────────────────────────
SKILLS_DB = [
    # Programming languages
    "python", "java", "javascript", "c++", "c#", "r", "sql", "scala",
    "typescript", "go", "rust", "kotlin", "swift", "php", "ruby",

    # ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "neural networks",
    "tensorflow", "keras", "pytorch", "scikit-learn", "xgboost", "lightgbm",
    "ml", "ai", "data science",

    # Data
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "data analysis", "data analytics", "data visualization",
    "feature engineering", "feature extraction",
    "data preprocessing", "data cleaning", "data wrangling",
    "eda", "exploratory data analysis",
    "statistics", "statistical analysis",
    "data structures", "algorithms",

    # Cloud & MLOps
    "aws", "gcp", "azure", "docker", "kubernetes", "mlflow",
    "airflow", "ci/cd", "git", "github", "gitlab", "bitbucket",

    # Web
    "flask", "fastapi", "django", "react", "node.js", "nodejs", "node js",
    "rest api", "rest apis", "restful", "html", "css",
    "javascript", "typescript",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle",
    "sql server", "nosql",

    # Mobile
    "android", "ios", "kotlin", "swift", "react native", "flutter",

    # Other tools
    "excel", "power bi", "powerbi", "tableau", "linux", "unix",
    "agile", "scrum", "jira", "oop", "oops",
    "data structures", "algorithms", "problem solving",

    # Cyber / Networking
    "networking", "cyber security", "cybersecurity", "ethical hacking",
    "penetration testing"
]


def clean_text(text: str) -> str:
    """Lowercase, remove special characters and extra whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
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
        r"(\d+)\+?\s*yrs?\s*experience",
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
        "m tech", "mtech", "m.tech", "master", "mba", "phd", "m.sc", "b.sc",
        "computer science", "information technology", "electronics",
        "data science", "artificial intelligence", "electrical engineering",
        "mechanical engineering", "civil engineering"
    ]
    text_lower = text.lower()
    found = []
    for kw in edu_keywords:
        if kw in text_lower:
            found.append(kw)
    return list(set(found))


def extract_entities(text: str) -> dict:
    """Use spaCy NER to extract organizations and locations — with noise filtering."""
    doc = nlp(text[:5000])
    entities = {"organizations": [], "locations": []}

    for ent in doc.ents:
        value = ent.text.strip()
        value_lower = value.lower()

        # Skip if it's a known tech word or too short
        if value_lower in TECH_NOISE or len(value) <= 2:
            continue

        # Skip if it looks like an acronym made of numbers/symbols
        if re.match(r"^[\d\W]+$", value):
            continue

        if ent.label_ == "ORG":
            # Skip all-caps short strings that are likely acronyms e.g. "CSV", "API"
            if value.isupper() and len(value) <= 4:
                continue
            entities["organizations"].append(value)

        elif ent.label_ in ("GPE", "LOC"):
            # Only keep proper location names (start with uppercase)
            if value[0].isupper():
                entities["locations"].append(value)

    entities["organizations"] = list(set(entities["organizations"]))
    entities["locations"] = list(set(entities["locations"]))
    return entities


def preprocess(text: str) -> dict:
    """
    Master function — runs full NLP pipeline on any text.
    Returns a structured dict with all extracted features.
    """
    cleaned      = clean_text(text)
    no_stopwords = remove_stopwords(cleaned)
    skills       = extract_skills(text)
    education    = extract_education(text)
    exp_years    = extract_experience_years(text)
    entities     = extract_entities(text)

    return {
        "original_text"   : text,
        "clean_text"      : cleaned,
        "tokens"          : no_stopwords,
        "skills"          : skills,
        "education"       : education,
        "experience_years": exp_years,
        "entities"        : entities,
        "word_count"      : len(text.split())
    }