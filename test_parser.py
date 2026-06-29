# test_parser.py

from apps.parser import extract_text, load_job_description

# --- Test resume parsing ---
resume_path = r"C:\Users\tejas\OneDrive\Documents\Teju Resume (2).pdf"
resume_text = extract_text(resume_path)

print("=" * 50)
print("RESUME TEXT (first 500 chars):")
print("=" * 50)
print(resume_text[:500])
print(f"\nTotal characters extracted: {len(resume_text)}")

# --- Test job description loading ---
sample_jd = """
We are looking for a Machine Learning Engineer with experience in Python,
TensorFlow, scikit-learn, and NLP. The candidate should have strong knowledge
of data preprocessing, model evaluation, and REST APIs. Experience with
Docker and cloud platforms (AWS/GCP) is a plus.
"""

jd_text = load_job_description(sample_jd)
print("\n" + "=" * 50)
print("JOB DESCRIPTION (first 200 chars):")
print("=" * 50)
print(jd_text[:200])
print("\nParser working correctly!")