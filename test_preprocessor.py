# test_preprocessor.py

from apps.parser import extract_text, load_job_description
from apps.preprocessor import preprocess

# ── Resume ──────────────────────────────────
resume_path = r"C:\Users\tejas\OneDrive\Documents\Teju Resume (2).pdf"
resume_text = extract_text(resume_path)
resume_data = preprocess(resume_text)

print("=" * 50)
print("RESUME ANALYSIS")
print("=" * 50)
print(f"Word count       : {resume_data['word_count']}")
print(f"Skills found     : {resume_data['skills']}")
print(f"Education        : {resume_data['education']}")
print(f"Experience years : {resume_data['experience_years']}")
print(f"Organizations    : {resume_data['entities']['organizations']}")
print(f"Locations        : {resume_data['entities']['locations']}")

# ── Job Description ──────────────────────────
sample_jd = """
We are looking for a Machine Learning Engineer with 2+ years of experience.
Required skills: Python, TensorFlow, scikit-learn, NLP, SQL, Docker, Git.
Experience with deep learning, data preprocessing, and model evaluation.
Familiarity with AWS or GCP is a plus. B.Tech in Computer Science preferred.
"""

jd_data = preprocess(sample_jd)

print("\n" + "=" * 50)
print("JOB DESCRIPTION ANALYSIS")
print("=" * 50)
print(f"Skills required  : {jd_data['skills']}")
print(f"Education        : {jd_data['education']}")
print(f"Experience years : {jd_data['experience_years']}")

# ── Skill Gap ────────────────────────────────
resume_skills = set(resume_data["skills"])
jd_skills     = set(jd_data["skills"])
matched       = resume_skills & jd_skills
missing       = jd_skills - resume_skills

print("\n" + "=" * 50)
print("SKILL GAP PREVIEW")
print("=" * 50)
print(f"Matched skills   : {sorted(matched)}")
print(f"Missing skills   : {sorted(missing)}")
print(f"Match rate       : {round(len(matched)/len(jd_skills)*100)}% of JD skills found")