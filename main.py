# main.py

import os
import tempfile
import streamlit as st

from apps.parser import extract_text
from apps.scorer import compute_ats_score

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding: 2rem; }
    .score-box {
        text-align: center;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .score-number {
        font-size: 3.5rem;
        font-weight: 600;
        line-height: 1;
    }
    .score-label {
        font-size: 0.85rem;
        color: #888;
        margin-top: 4px;
    }
    .pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        margin: 3px;
    }
    .pill-green { background:#E1F5EE; color:#0F6E56; }
    .pill-red   { background:#FCEBEB; color:#A32D2D; }
    .pill-gray  { background:#F1EFE8; color:#5F5E5A; }
    .rec-box {
        background: #E6F1FB;
        color: #0C447C;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.9rem;
        margin-top: 1rem;
        line-height: 1.6;
    }
    .section-label {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 12px 0 6px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("📄 ATS Resume Analyzer")
st.caption("Upload your resume and paste a job description to get your ATS match score.")
st.divider()


# ─────────────────────────────────────────────
# LAYOUT — two columns
# ─────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")


# ── LEFT COLUMN — inputs ──────────────────────
with left:
    st.subheader("Your inputs")

    uploaded_file = st.file_uploader(
        "Upload resume",
        type=["pdf", "docx"],
        help="Supports PDF and DOCX formats"
    )

    jd_text = st.text_area(
        "Paste job description",
        height=250,
        placeholder="Copy and paste the full job description here..."
    )

    analyze_btn = st.button("Analyze resume", use_container_width=True, type="primary")


# ── RIGHT COLUMN — results ────────────────────
with right:
    st.subheader("ATS analysis")

    if analyze_btn:
        # ── Validate inputs ───────────────────
        if not uploaded_file:
            st.error("Please upload a resume first.")
            st.stop()

        if not jd_text.strip():
            st.error("Please paste a job description.")
            st.stop()

        # ── Extract resume text ───────────────
        with st.spinner("Reading resume..."):
            suffix = ".pdf" if uploaded_file.name.endswith(".pdf") else ".docx"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                resume_text = extract_text(tmp_path)
            except Exception as e:
                st.error(f"Could not parse resume: {e}")
                st.stop()
            finally:
                os.unlink(tmp_path)   # clean up temp file

        # ── Compute ATS score ─────────────────
        with st.spinner("Analyzing match..."):
            result = compute_ats_score(resume_text, jd_text)

        # ── ATS Score display ─────────────────
        score = result["ats_score"]

        if score >= 75:
            color = "#0F6E56"
            label = "Strong match"
        elif score >= 50:
            color = "#854F0B"
            label = "Moderate match"
        else:
            color = "#A32D2D"
            label = "Low match"

        st.markdown(f"""
        <div class="score-box">
            <div class="score-number" style="color:{color}">{score}</div>
            <div class="score-label">/ 100 &nbsp;·&nbsp; {label}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Sub scores ────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("Similarity", f"{result['similarity_score']}")
        c2.metric("Skills", f"{result['skill_score']}")
        c3.metric("Education", f"{result['education_score']}")

        st.divider()

        # ── Skill pills ───────────────────────
        def render_pills(skills, css_class):
            if not skills:
                return "<span style='color:#aaa;font-size:0.85rem'>None</span>"
            return " ".join(
                f'<span class="pill {css_class}">{s}</span>'
                for s in skills
            )

        st.markdown('<div class="section-label">Matched skills</div>', unsafe_allow_html=True)
        st.markdown(render_pills(result["matched_skills"], "pill-green"), unsafe_allow_html=True)

        st.markdown('<div class="section-label">Missing skills</div>', unsafe_allow_html=True)
        st.markdown(render_pills(result["missing_skills"], "pill-red"), unsafe_allow_html=True)

        st.markdown('<div class="section-label">Extra skills you have</div>', unsafe_allow_html=True)
        st.markdown(render_pills(result["extra_skills"], "pill-gray"), unsafe_allow_html=True)

        st.divider()

        # ── Recommendation ────────────────────
        st.markdown(f"""
        <div class="rec-box">
            💡 {result['recommendation']}
        </div>
        """, unsafe_allow_html=True)

        # ── Raw details expander ──────────────
        with st.expander("View full details"):
            st.write("**All resume skills detected:**", result["resume_skills"])
            st.write("**All JD skills required:**", result["jd_skills"])
            st.write("**Experience years detected:**", result["experience_years"])

    else:
        st.info("Upload a resume and paste a job description, then click **Analyze resume**.")