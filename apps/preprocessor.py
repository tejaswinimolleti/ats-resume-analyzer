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
# NER NOISE FILTER
# ─────────────────────────────────────────────
TECH_NOISE = {
    "csv", "cgpa", "gpa", "sql", "git", "docker", "anaconda", "linux",
    "python", "java", "github", "certifications", "html", "css", "api",
    "json", "xml", "http", "rest", "aws", "gcp", "azure", "excel",
    "numpy", "pandas", "tensorflow", "keras", "pytorch", "flask",
    "django", "react", "node", "mongodb", "mysql", "sqlite", "redis",
    "tableau", "powerbi", "kubernetes", "mlflow", "airflow", "scikit",
    "matplotlib", "seaborn", "plotly", "jupyter", "android", "ios",
    "k-means", "linear regression", "logistic regression", "random forest",
    "neural network", "deep learning", "machine learning"
}

# ─────────────────────────────────────────────
# UNIVERSAL SKILLS DICTIONARY — ALL DOMAINS
# ─────────────────────────────────────────────
SKILLS_DB = {

    # ── COMPUTER SCIENCE & SOFTWARE ───────────────────────────────────────
    "programming_languages": [
        "python", "java", "javascript", "c++", "c#", "c", "r", "sql",
        "scala", "typescript", "go", "rust", "kotlin", "swift", "php",
        "ruby", "perl", "matlab", "bash", "shell scripting", "vba"
    ],
    "ml_ai": [
        "machine learning", "deep learning", "nlp",
        "natural language processing", "computer vision",
        "reinforcement learning", "neural networks", "tensorflow",
        "keras", "pytorch", "scikit-learn", "xgboost", "lightgbm",
        "ml", "ai", "data science", "llm", "generative ai",
        "prompt engineering", "feature engineering", "model deployment"
    ],
    "data": [
        "pandas", "numpy", "matplotlib", "seaborn", "plotly",
        "data analysis", "data analytics", "data visualization",
        "data preprocessing", "data cleaning", "data wrangling",
        "eda", "exploratory data analysis", "statistics",
        "statistical analysis", "data structures", "algorithms",
        "etl", "data pipeline", "data modeling", "big data",
        "data mining", "business intelligence"
    ],
    "cloud_devops": [
        "aws", "gcp", "azure", "docker", "kubernetes", "mlflow",
        "airflow", "ci/cd", "git", "github", "gitlab", "devops",
        "terraform", "jenkins", "ansible", "linux", "unix"
    ],
    "web_dev": [
        "flask", "fastapi", "django", "react", "angular", "vue",
        "node.js", "nodejs", "rest api", "restful", "graphql",
        "html", "css", "sass", "webpack", "spring boot", "asp.net"
    ],
    "databases": [
        "mysql", "postgresql", "mongodb", "sqlite", "redis",
        "oracle", "sql server", "nosql", "cassandra", "elasticsearch",
        "firebase", "dynamodb"
    ],
    "cybersecurity": [
        "cyber security", "cybersecurity", "ethical hacking",
        "penetration testing", "network security", "cryptography",
        "soc", "siem", "vulnerability assessment", "firewall",
        "intrusion detection", "malware analysis", "owasp"
    ],
    "mobile": [
        "android", "ios", "kotlin", "swift", "react native",
        "flutter", "xamarin", "mobile development"
    ],

    # ── MECHANICAL / CIVIL / ELECTRICAL ENGINEERING ───────────────────────
    "mechanical_engineering": [
        "autocad", "solidworks", "catia", "ansys", "fusion 360",
        "creo", "nx", "pro/e", "finite element analysis", "fea",
        "cad", "cam", "cnc", "thermodynamics", "fluid mechanics",
        "heat transfer", "manufacturing", "lean manufacturing",
        "six sigma", "product design", "mechanical design",
        "robotics", "automation", "hydraulics", "pneumatics",
        "quality control", "quality assurance", "iso standards",
        "3d printing", "additive manufacturing", "metrology"
    ],
    "civil_engineering": [
        "autocad", "revit", "staad pro", "etabs", "primavera",
        "ms project", "structural analysis", "structural design",
        "concrete design", "steel design", "geotechnical",
        "surveying", "quantity estimation", "construction management",
        "project management", "building information modeling", "bim",
        "hvac", "plumbing design", "road design", "bridge design",
        "environmental engineering", "water treatment"
    ],
    "electrical_engineering": [
        "matlab", "simulink", "autocad electrical", "plc", "scada",
        "vlsi", "embedded systems", "arduino", "raspberry pi",
        "microcontrollers", "circuit design", "pcb design",
        "power systems", "power electronics", "control systems",
        "signal processing", "dsp", "fpga", "vhdl", "verilog",
        "iot", "sensors", "actuators", "motor drives"
    ],

    # ── BUSINESS, MANAGEMENT & FINANCE ───────────────────────────────────
    "business_management": [
        "project management", "agile", "scrum", "kanban", "waterfall",
        "pmp", "prince2", "business analysis", "business development",
        "strategic planning", "operations management", "supply chain",
        "logistics", "procurement", "vendor management",
        "stakeholder management", "change management",
        "risk management", "process improvement",
        "lean", "six sigma", "kaizen", "erp", "sap", "oracle erp"
    ],
    "finance_accounting": [
        "financial analysis", "financial modeling", "financial reporting",
        "accounting", "bookkeeping", "taxation", "gst", "tds",
        "auditing", "budgeting", "forecasting", "cash flow",
        "balance sheet", "profit and loss", "ms excel",
        "tally", "quickbooks", "sap fi", "ifrs", "gaap",
        "investment analysis", "valuation", "equity research",
        "portfolio management", "risk assessment", "banking",
        "credit analysis", "loan underwriting", "wealth management"
    ],
    "marketing": [
        "digital marketing", "seo", "sem", "social media marketing",
        "content marketing", "email marketing", "google analytics",
        "google ads", "facebook ads", "instagram marketing",
        "influencer marketing", "brand management", "market research",
        "consumer behavior", "copywriting", "content writing",
        "public relations", "pr", "crm", "hubspot", "salesforce",
        "product marketing", "growth hacking", "affiliate marketing"
    ],
    "sales": [
        "sales", "b2b sales", "b2c sales", "inside sales",
        "field sales", "lead generation", "cold calling",
        "negotiation", "client relationship", "account management",
        "customer success", "revenue generation", "salesforce",
        "crm", "sales forecasting", "channel sales"
    ],
    "hr": [
        "recruitment", "talent acquisition", "onboarding",
        "performance management", "hr operations", "payroll",
        "employee relations", "training and development",
        "learning and development", "succession planning",
        "compensation and benefits", "hris", "workday",
        "sap hr", "organizational development", "labor law",
        "statutory compliance", "pf", "esi", "gratuity"
    ],

    # ── HEALTHCARE & MEDICINE ─────────────────────────────────────────────
    "healthcare": [
        "clinical research", "clinical trials", "pharmacovigilance",
        "medical coding", "icd-10", "cpt codes", "ehr", "emr",
        "epic", "cerner", "nursing", "patient care", "ward management",
        "medical imaging", "radiology", "pathology", "surgery",
        "anesthesia", "pharmaceutical", "drug development",
        "regulatory affairs", "fda", "gcp", "gmp", "sop",
        "healthcare management", "public health", "epidemiology",
        "medical writing", "clinical data management"
    ],

    # ── DESIGN & CREATIVE ─────────────────────────────────────────────────
    "design": [
        "ui design", "ux design", "ui/ux", "user research",
        "wireframing", "prototyping", "figma", "sketch", "adobe xd",
        "adobe photoshop", "photoshop", "adobe illustrator",
        "illustrator", "adobe indesign", "indesign",
        "graphic design", "visual design", "motion graphics",
        "after effects", "premiere pro", "video editing",
        "3d modeling", "blender", "maya", "cinema 4d",
        "product design", "interaction design", "design thinking",
        "branding", "typography", "color theory", "canva"
    ],

    # ── LEGAL ─────────────────────────────────────────────────────────────
    "legal": [
        "legal research", "legal drafting", "contract drafting",
        "contract review", "litigation", "corporate law",
        "intellectual property", "ip law", "patent law",
        "trademark", "copyright", "mergers and acquisitions",
        "due diligence", "compliance", "regulatory compliance",
        "gdpr", "data privacy", "employment law", "labor law",
        "tax law", "dispute resolution", "arbitration",
        "legal writing", "case management"
    ],

    # ── EDUCATION & RESEARCH ──────────────────────────────────────────────
    "education_research": [
        "curriculum development", "lesson planning", "instructional design",
        "e-learning", "lms", "moodle", "teaching", "training",
        "research methodology", "qualitative research",
        "quantitative research", "literature review", "thesis writing",
        "academic writing", "spss", "r", "stata", "nvivo",
        "grant writing", "data collection", "survey design"
    ],

    # ── UNIVERSAL SOFT SKILLS ─────────────────────────────────────────────
    "soft_skills": [
        "communication", "leadership", "teamwork", "team management",
        "problem solving", "critical thinking", "analytical thinking",
        "time management", "multitasking", "adaptability",
        "creativity", "attention to detail", "decision making",
        "conflict resolution", "mentoring", "coaching",
        "presentation skills", "public speaking", "negotiation",
        "collaboration", "interpersonal skills", "emotional intelligence"
    ],

    # ── LANGUAGES ─────────────────────────────────────────────────────────
    "languages": [
        "english", "hindi", "telugu", "tamil", "kannada", "malayalam",
        "marathi", "bengali", "gujarati", "punjabi",
        "french", "german", "spanish", "japanese", "mandarin", "arabic"
    ],

    # ── TOOLS (UNIVERSAL) ─────────────────────────────────────────────────
    "tools": [
        "microsoft office", "ms office", "ms word", "ms excel",
        "ms powerpoint", "google workspace", "google sheets",
        "google docs", "slack", "zoom", "teams", "jira", "confluence",
        "notion", "trello", "asana", "monday.com", "power bi",
        "tableau", "excel", "visio"
    ]
}

# Flatten all skills into one list for matching
ALL_SKILLS = []
for category_skills in SKILLS_DB.values():
    ALL_SKILLS.extend(category_skills)
ALL_SKILLS = list(set(ALL_SKILLS))


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
    """Match skills from ALL_SKILLS against the text."""
    text_lower = text.lower()
    found = []
    for skill in ALL_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def get_skill_domain(skill: str) -> str:
    """Return which domain a skill belongs to."""
    for domain, skills in SKILLS_DB.items():
        if skill.lower() in [s.lower() for s in skills]:
            return domain
    return "general"


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
    """Extract education-related keywords — all disciplines."""
    edu_keywords = [
        # Engineering
        "b tech", "btech", "b.tech", "be", "b.e",
        "m tech", "mtech", "m.tech", "me", "m.e",
        # Science
        "b.sc", "bsc", "m.sc", "msc",
        # Commerce / Business
        "b.com", "bcom", "m.com", "mcom", "mba", "bba",
        # Arts
        "ba", "b.a", "ma", "m.a",
        # Medicine
        "mbbs", "bds", "bpharm", "mpharm", "md", "ms",
        # Law
        "llb", "llm", "ba llb",
        # Computer Science
        "bca", "mca", "b.sc cs", "b.sc it",
        # PhD
        "phd", "doctorate",
        # Fields
        "computer science", "information technology", "electronics",
        "electrical engineering", "mechanical engineering",
        "civil engineering", "chemical engineering",
        "data science", "artificial intelligence",
        "finance", "accounting", "economics", "statistics",
        "mathematics", "physics", "chemistry", "biology",
        "medicine", "pharmacy", "nursing", "law", "management",
        "commerce", "arts", "humanities", "social science",
        "psychology", "education", "architecture"
    ]
    text_lower = text.lower()
    found = []
    for kw in edu_keywords:
        if kw in text_lower:
            found.append(kw)
    return list(set(found))


def extract_entities(text: str) -> dict:
    """Use spaCy NER to extract organizations and locations with noise filtering."""
    doc = nlp(text[:5000])
    entities = {"organizations": [], "locations": []}

    for ent in doc.ents:
        value = ent.text.strip()
        value_lower = value.lower()

        if value_lower in TECH_NOISE or len(value) <= 2:
            continue
        if re.match(r"^[\d\W]+$", value):
            continue

        if ent.label_ == "ORG":
            if value.isupper() and len(value) <= 4:
                continue
            entities["organizations"].append(value)
        elif ent.label_ in ("GPE", "LOC"):
            if value[0].isupper():
                entities["locations"].append(value)

    entities["organizations"] = list(set(entities["organizations"]))
    entities["locations"] = list(set(entities["locations"]))
    return entities


def preprocess(text: str) -> dict:
    """
    Master function — runs full NLP pipeline on any text.
    Works for any domain: CS, engineering, business, healthcare, design, law.
    Returns a structured dict with all extracted features.
    """
    cleaned      = clean_text(text)
    no_stopwords = remove_stopwords(cleaned)
    skills       = extract_skills(text)
    education    = extract_education(text)
    exp_years    = extract_experience_years(text)
    entities     = extract_entities(text)

    # Group detected skills by domain
    skill_domains = {}
    for skill in skills:
        domain = get_skill_domain(skill)
        skill_domains.setdefault(domain, []).append(skill)

    return {
        "original_text"   : text,
        "clean_text"      : cleaned,
        "tokens"          : no_stopwords,
        "skills"          : skills,
        "skill_domains"   : skill_domains,
        "education"       : education,
        "experience_years": exp_years,
        "entities"        : entities,
        "word_count"      : len(text.split())
    }