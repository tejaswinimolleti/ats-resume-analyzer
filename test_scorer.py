# test_scorer.py

from apps.parser import extract_text
from apps.scorer import compute_ats_score
# app/scorer.py — update these three lines

WEIGHT_SIMILARITY = 0.20   # reduced — TF-IDF struggles with short text
WEIGHT_SKILLS     = 0.60   # increased — skills are the most reliable signal
WEIGHT_EDUCATION  = 0.20   # unchanged

# ── Load resume ──────────────────────────────
resume_path = r"C:\Users\tejas\OneDrive\Documents\Teju Resume (2).pdf"
resume_text = extract_text(resume_path)

# ── Sample Job Description ───────────────────
jd_text = """
We are looking for a Machine Learning Engineer with 2+ years of experience.
Required skills: Python, TensorFlow, scikit-learn, NLP, SQL, Docker, Git.
Experience with deep learning, data preprocessing, and model evaluation.
Familiarity with AWS or GCP is a plus. B.Tech in Computer Science preferred.
"""

# ── Run ATS Scoring ──────────────────────────
result = compute_ats_score(resume_text, jd_text)

# ── Print Results ────────────────────────────
print("=" * 50)
print(f"  ATS SCORE        : {result['ats_score']} / 100")
print("=" * 50)
print(f"  Similarity Score : {result['similarity_score']} / 100")
print(f"  Skill Score      : {result['skill_score']} / 100")
print(f"  Education Score  : {result['education_score']} / 100")
print("-" * 50)
print(f"  Matched Skills   : {result['matched_skills']}")
print(f"  Missing Skills   : {result['missing_skills']}")
print(f"  Extra Skills     : {result['extra_skills']}")
print("-" * 50)
print(f"  Recommendation   : {result['recommendation']}")
print("=" * 50)