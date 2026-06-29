# app/scorer.py
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from apps.preprocessor import preprocess
from sentence_transformers import SentenceTransformer, util  # ← add this

# Load SBERT model once at startup
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")  # ← add this

WEIGHT_SIMILARITY = 0.20
WEIGHT_SKILLS     = 0.60
WEIGHT_EDUCATION  = 0.20

def compute_similarity_score(resume_tokens: str, jd_tokens: str) -> float:
    """
    TF-IDF cosine similarity between resume and JD.
    Returns a score from 0 to 100.
    """
    if not resume_tokens.strip() or not jd_tokens.strip():
        return 0.0

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_tokens, jd_tokens])
        score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        return round(score * 100, 2)
    except Exception:
        return 0.0
def compute_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Sentence-BERT semantic similarity. Understands meaning not just keywords."""
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    embeddings = sbert_model.encode(
        [resume_text[:512], jd_text[:512]],
        convert_to_tensor=True
    )
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(max(score, 0) * 100, 2)


def compute_skill_score(resume_skills: list, jd_skills: list) -> dict:
    """
    Compare resume skills vs JD required skills.
    Returns score + matched/missing lists.
    """
    if not jd_skills:
        return {"score": 0.0, "matched": [], "missing": []}

    resume_set = set(resume_skills)
    jd_set     = set(jd_skills)

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    extra   = sorted(resume_set - jd_set)  # skills you have beyond JD

    score = round((len(matched) / len(jd_set)) * 100, 2)

    return {
        "score"  : score,
        "matched": matched,
        "missing": missing,
        "extra"  : extra
    }


def compute_education_score(resume_edu: list, jd_edu: list) -> float:
    """
    Check if resume education matches JD education requirements.
    Returns 100 if match found, 50 if partial, 0 if none.
    """
    if not jd_edu:
        return 100.0   # JD has no edu requirement — full marks

    resume_edu_str = " ".join(resume_edu).lower()
    jd_edu_str     = " ".join(jd_edu).lower()

    # Full match keywords
    full_match_pairs = [
        ("b tech", "b.tech"), ("btech", "b.tech"),
        ("computer science", "computer science"),
        ("data science", "data science"),
        ("master", "master"), ("phd", "phd")
    ]

    # Check for direct overlap
    resume_set = set(resume_edu)
    jd_set     = set(jd_edu)
    overlap    = resume_set & jd_set

    if overlap:
        return 100.0

    # Partial match — some words in common
    resume_words = set(resume_edu_str.split())
    jd_words     = set(jd_edu_str.split())
    if resume_words & jd_words:
        return 50.0

    return 0.0


def generate_recommendation(ats_score: float, missing_skills: list) -> str:
    """Generate a human-readable recommendation based on score."""
    if ats_score >= 80:
        msg = "Excellent match! Your resume is well-aligned with this job."
    elif ats_score >= 60:
        msg = "Good match! A few tweaks will make your resume stronger."
    elif ats_score >= 40:
        msg = "Moderate match. Focus on adding the missing skills below."
    else:
        msg = "Low match. Consider tailoring your resume more closely to the JD."

    if missing_skills:
        skills_str = ", ".join(missing_skills[:5])  # show top 5
        msg += f" Key missing skills: {skills_str}."

    return msg


def compute_ats_score(resume_text: str, jd_text: str) -> dict:
    """
    Master scoring function.
    Takes raw resume text + raw JD text.
    Returns complete ATS analysis dict.
    """
    # Step 1 — preprocess both
    resume_data = preprocess(resume_text)
    jd_data     = preprocess(jd_text)

    # Step 2 — individual scores
    similarity_score = compute_similarity_score(
        resume_data["clean_text"],
        jd_data["clean_text"]
    )

    skill_result = compute_skill_score(
        resume_data["skills"],
        jd_data["skills"]
    )

    education_score = compute_education_score(
        resume_data["education"],
        jd_data["education"]
    )

    # Step 3 — weighted ATS score
    ats_score = round(
        (similarity_score  * WEIGHT_SIMILARITY) +
        (skill_result["score"] * WEIGHT_SKILLS) +
        (education_score   * WEIGHT_EDUCATION),
        2
    )

    # Step 4 — recommendation
    recommendation = generate_recommendation(ats_score, skill_result["missing"])

    return {
        "ats_score"        : ats_score,
        "similarity_score" : similarity_score,
        "skill_score"      : skill_result["score"],
        "education_score"  : education_score,
        "matched_skills"   : skill_result["matched"],
        "missing_skills"   : skill_result["missing"],
        "extra_skills"     : skill_result["extra"],
        "resume_skills"    : resume_data["skills"],
        "jd_skills"        : jd_data["skills"],
        "experience_years" : resume_data["experience_years"],
        "recommendation"   : recommendation
    }