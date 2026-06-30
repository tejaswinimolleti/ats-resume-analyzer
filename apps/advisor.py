# apps/advisor.py

import re

# ─────────────────────────────────────────────
# WEAK ACTION WORDS → STRONGER ALTERNATIVES
# ─────────────────────────────────────────────
WEAK_WORDS = {
    "worked on"      : "developed / engineered / built",
    "worked with"    : "collaborated with / leveraged",
    "helped"         : "contributed to / supported / facilitated",
    "assisted"       : "supported / coordinated / enabled",
    "did"            : "executed / implemented / delivered",
    "made"           : "designed / built / created / developed",
    "was responsible": "led / managed / owned / delivered",
    "handled"        : "managed / administered / oversaw",
    "used"           : "utilized / applied / implemented",
    "tried"          : "implemented / applied / experimented with",
    "good at"        : "proficient in / experienced in",
    "know"           : "proficient in / skilled in",
    "familiar with"  : "experienced in / knowledgeable in",
    "exposure to"    : "hands-on experience with",
    "basic knowledge": "foundational knowledge / working knowledge",
    "learned"        : "acquired expertise in / trained in",
}

# ─────────────────────────────────────────────
# ESSENTIAL RESUME SECTIONS ATS LOOKS FOR
# ─────────────────────────────────────────────
REQUIRED_SECTIONS = {
    "summary"    : ["summary", "objective", "profile", "about me", "career objective"],
    "experience" : ["experience", "work experience", "employment", "internship", "projects"],
    "education"  : ["education", "qualification", "academic"],
    "skills"     : ["skills", "technical skills", "core competencies", "expertise"],
    "achievements": ["achievement", "award", "honor", "certification", "accomplishment"],
}

# ─────────────────────────────────────────────
# QUANTIFICATION SIGNALS
# ─────────────────────────────────────────────
QUANT_PATTERNS = [
    r"\d+\%",           # percentages
    r"\d+\+",           # 10+ years
    r"\$[\d,]+",        # dollar amounts
    r"₹[\d,]+",         # rupee amounts
    r"\d+\s*(users?|clients?|customers?|projects?|teams?|members?)",
    r"(increased|decreased|improved|reduced|saved|generated)\s.*\d+",
]


def check_missing_sections(resume_text: str) -> list:
    """Check which important sections are missing from the resume."""
    text_lower = resume_text.lower()
    missing = []
    for section, keywords in REQUIRED_SECTIONS.items():
        if not any(kw in text_lower for kw in keywords):
            missing.append(section)
    return missing


def check_weak_language(resume_text: str) -> list:
    """Find weak action words and suggest replacements."""
    text_lower = resume_text.lower()
    found = []
    for weak, strong in WEAK_WORDS.items():
        if weak in text_lower:
            found.append({
                "weak"      : weak,
                "suggestion": strong
            })
    return found


def check_quantification(resume_text: str) -> dict:
    """Check if resume has quantified achievements."""
    has_numbers = bool(re.search(r'\b\d+\b', resume_text))
    quant_count = sum(
        1 for p in QUANT_PATTERNS
        if re.search(p, resume_text, re.IGNORECASE)
    )
    return {
        "has_quantification": quant_count > 0,
        "quant_count"       : quant_count,
        "suggestion"        : "Add numbers to your achievements (e.g. 'Improved model accuracy by 15%', 'Managed a team of 5')"
                              if quant_count == 0 else None
    }


def get_irrelevant_skills(resume_skills: list, jd_skills: list, top_n: int = 5) -> list:
    """
    Find skills on resume that are completely absent from the JD.
    These may dilute ATS relevance score — candidate should
    consider moving them to a separate 'Additional Skills' section
    or removing if they fill critical space.
    """
    jd_set     = set(jd_skills)
    resume_set = set(resume_skills)
    irrelevant = sorted(resume_set - jd_set)
    return irrelevant[:top_n]


def get_priority_missing_skills(missing_skills: list, jd_text: str) -> list:
    """
    Rank missing skills by how many times they appear in the JD.
    Skills mentioned more in the JD = higher priority to add.
    """
    jd_lower = jd_text.lower()
    scored = []
    for skill in missing_skills:
        count = len(re.findall(r'\b' + re.escape(skill) + r'\b', jd_lower))
        scored.append({"skill": skill, "jd_mentions": count})
    scored.sort(key=lambda x: x["jd_mentions"], reverse=True)
    return scored


def check_resume_length(resume_text: str) -> dict:
    """Check if resume length is appropriate."""
    word_count = len(resume_text.split())
    if word_count < 150:
        status = "too_short"
        msg = f"Resume is very short ({word_count} words). ATS systems prefer 300–700 words. Add more detail to your experience and projects."
    elif word_count > 800:
        status = "too_long"
        msg = f"Resume is long ({word_count} words). Consider trimming to 400–600 words for better ATS parsing."
    else:
        status = "good"
        msg = f"Resume length is good ({word_count} words)."
    return {"status": status, "word_count": word_count, "message": msg}


def check_contact_info(resume_text: str) -> list:
    """Check if basic contact info is present."""
    missing = []
    checks = {
        "email"  : r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone"  : r"(\+?\d[\d\s\-]{8,}\d)",
        "linkedin": r"linkedin\.com",
        "github" : r"github\.com",
    }
    for field, pattern in checks.items():
        if not re.search(pattern, resume_text, re.IGNORECASE):
            missing.append(field)
    return missing


def generate_improvement_report(
    resume_text  : str,
    resume_data  : dict,
    jd_data      : dict,
    result       : dict
) -> dict:
    """
    Master function — generates a complete improvement report.
    Call this after compute_ats_score().
    """
    missing_sections  = check_missing_sections(resume_text)
    weak_language     = check_weak_language(resume_text)
    quantification    = check_quantification(resume_text)
    irrelevant_skills = get_irrelevant_skills(
                            result["resume_skills"],
                            result["jd_skills"]
                        )
    priority_missing  = get_priority_missing_skills(
                            result["missing_skills"],
                            jd_data.get("original_text", "")
                        )
    length_check      = check_resume_length(resume_text)
    contact_check     = check_contact_info(resume_text)

    # Overall improvement potential
    potential_gain = 0
    if missing_sections:
        potential_gain += len(missing_sections) * 3
    if weak_language:
        potential_gain += min(len(weak_language) * 2, 10)
    if not quantification["has_quantification"]:
        potential_gain += 8
    if priority_missing:
        potential_gain += min(len(priority_missing) * 4, 20)

    return {
        "missing_sections" : missing_sections,
        "weak_language"    : weak_language,
        "quantification"   : quantification,
        "irrelevant_skills": irrelevant_skills,
        "priority_missing" : priority_missing,
        "length_check"     : length_check,
        "contact_check"    : contact_check,
        "potential_gain"   : min(potential_gain, 30),  # cap at 30 points
    }