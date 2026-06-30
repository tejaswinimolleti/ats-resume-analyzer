# main.py

import os
import tempfile
import streamlit as st

from apps.parser import extract_text
from apps.scorer import compute_ats_score
from apps.preprocessor import preprocess
from apps.advisor import generate_improvement_report

st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
    .score-box {
        text-align: center; padding: 1.5rem;
        border-radius: 12px; border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .score-number { font-size: 3.5rem; font-weight: 600; line-height: 1; }
    .score-label  { font-size: 0.85rem; color: #888; margin-top: 4px; }
    .pill { display:inline-block; padding:4px 12px; border-radius:999px; font-size:0.8rem; margin:3px; }
    .pill-green  { background:#E1F5EE; color:#0F6E56; }
    .pill-red    { background:#FCEBEB; color:#A32D2D; }
    .pill-gray   { background:#F1EFE8; color:#5F5E5A; }
    .pill-amber  { background:#FAEEDA; color:#854F0B; }
    .rec-box     { background:#E6F1FB; color:#0C447C; border-radius:8px; padding:12px 16px; font-size:0.9rem; margin-top:1rem; line-height:1.6; }
    .warn-box    { background:#FAEEDA; color:#854F0B; border-radius:8px; padding:12px 16px; font-size:0.9rem; margin:6px 0; line-height:1.6; }
    .danger-box  { background:#FCEBEB; color:#A32D2D; border-radius:8px; padding:12px 16px; font-size:0.9rem; margin:6px 0; line-height:1.6; }
    .success-box { background:#E1F5EE; color:#0F6E56; border-radius:8px; padding:12px 16px; font-size:0.9rem; margin:6px 0; line-height:1.6; }
    .section-label { font-size:0.75rem; color:#888; text-transform:uppercase; letter-spacing:0.05em; margin:12px 0 6px; }
    .improve-card  { border:0.5px solid #e0e0e0; border-radius:10px; padding:14px 16px; margin-bottom:10px; }
    .improve-title { font-size:0.95rem; font-weight:500; margin-bottom:6px; }
    .priority-tag  { display:inline-block; font-size:0.7rem; padding:1px 7px; border-radius:999px; background:#FCEBEB; color:#A32D2D; margin-left:6px; }
</style>
""", unsafe_allow_html=True)


st.title("📄 ATS Resume Analyzer")
st.caption("Upload your resume and paste a job description to get your ATS score and improvement suggestions.")
st.divider()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("Your inputs")
    uploaded_file = st.file_uploader(
        "Upload resume", type=["pdf", "docx"],
        help="Supports PDF and DOCX"
    )
    jd_text = st.text_area(
        "Paste job description", height=250,
        placeholder="Copy and paste the full job description here..."
    )
    analyze_btn = st.button("Analyze resume", use_container_width=True, type="primary")

with right:
    if analyze_btn:

        if not uploaded_file:
            st.error("Please upload a resume first.")
            st.stop()
        if not jd_text.strip():
            st.error("Please paste a job description.")
            st.stop()

        # ── Parse resume ──────────────────────────────
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
                os.unlink(tmp_path)

        # ── Score + Improve ───────────────────────────
        with st.spinner("Analyzing match and generating suggestions..."):
            result      = compute_ats_score(resume_text, jd_text)
            resume_data = preprocess(resume_text)
            jd_data     = preprocess(jd_text)
            report      = generate_improvement_report(
                              resume_text, resume_data, jd_data, result
                          )

        # ── Tabs ─────────────────────────────────────
        tab1, tab2 = st.tabs(["📊 ATS Score", "🛠 Improvement Plan"])

        # ════════════════════════════════════════════
        # TAB 1 — ATS SCORE
        # ════════════════════════════════════════════
        with tab1:
            score = result["ats_score"]
            if score >= 75:
                color, label = "#0F6E56", "Strong match"
            elif score >= 50:
                color, label = "#854F0B", "Moderate match"
            else:
                color, label = "#A32D2D", "Low match"

            st.markdown(f"""
            <div class="score-box">
                <div class="score-number" style="color:{color}">{score}</div>
                <div class="score-label">/ 100 &nbsp;·&nbsp; {label}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Similarity",  f"{result['similarity_score']}")
            c2.metric("Skills",      f"{result['skill_score']}")
            c3.metric("Education",   f"{result['education_score']}")

            if report["potential_gain"] > 0:
                st.markdown(f"""
                <div class="warn-box">
                    ⚡ Your score could improve by up to
                    <strong>+{report['potential_gain']} points</strong>
                    by following the Improvement Plan tab.
                </div>
                """, unsafe_allow_html=True)

            st.divider()

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
            st.markdown(f"""
            <div class="rec-box">💡 {result['recommendation']}</div>
            """, unsafe_allow_html=True)

            with st.expander("View full details"):
                st.write("**All resume skills:**", result["resume_skills"])
                st.write("**All JD skills:**", result["jd_skills"])
                st.write("**Experience years:**", result["experience_years"])

        # ════════════════════════════════════════════
        # TAB 2 — IMPROVEMENT PLAN
        # ════════════════════════════════════════════
        with tab2:
            st.markdown("### Your personalised resume improvement plan")
            st.caption("Based on your resume vs this job description")

            # ── 1. Priority skills to add ─────────────
            st.markdown("---")
            st.markdown("#### 🎯 Skills to add (ranked by JD importance)")
            if report["priority_missing"]:
                for item in report["priority_missing"]:
                    mentions = item["jd_mentions"]
                    tag = f'<span class="priority-tag">mentioned {mentions}x in JD</span>' if mentions > 1 else ""
                    st.markdown(
                        f'<div class="improve-card">'
                        f'<div class="improve-title">➕ Add <strong>{item["skill"]}</strong> {tag}</div>'
                        f'<div style="font-size:0.85rem;color:#666;">Include this in your skills section or describe relevant experience with it in your projects.</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div class="success-box">✅ Your resume covers all required skills!</div>', unsafe_allow_html=True)

            # ── 2. Skills to reconsider ───────────────
            st.markdown("---")
            st.markdown("#### 🗑 Skills to reconsider removing")
            if report["irrelevant_skills"]:
                st.markdown(
                    '<div class="warn-box">'
                    'These skills are on your resume but not relevant to this JD. '
                    'They don\'t hurt your score but take up space. '
                    'Move them to an "Additional Skills" section or remove if space is tight.'
                    '</div>',
                    unsafe_allow_html=True
                )
                st.markdown(render_pills(report["irrelevant_skills"], "pill-amber"), unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">✅ All your skills are relevant to this JD!</div>', unsafe_allow_html=True)

            # ── 3. Weak language ──────────────────────
            st.markdown("---")
            st.markdown("#### ✍️ Weak language to replace")
            if report["weak_language"]:
                for item in report["weak_language"]:
                    st.markdown(
                        f'<div class="improve-card">'
                        f'<div class="improve-title">Replace <span style="color:#A32D2D">"{item["weak"]}"</span> → '
                        f'<span style="color:#0F6E56">{item["suggestion"]}</span></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div class="success-box">✅ Strong action words detected!</div>', unsafe_allow_html=True)

            # ── 4. Quantification ─────────────────────
            st.markdown("---")
            st.markdown("#### 📊 Quantify your achievements")
            q = report["quantification"]
            if not q["has_quantification"]:
                st.markdown(
                    f'<div class="danger-box">'
                    f'⚠️ {q["suggestion"]}<br><br>'
                    f'<strong>Examples:</strong><br>'
                    f'• "Improved model accuracy by 12%"<br>'
                    f'• "Processed 10,000+ records daily"<br>'
                    f'• "Reduced processing time by 30%"<br>'
                    f'• "Managed a team of 4 interns"'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="success-box">✅ Good — your resume has {q["quant_count"]} quantified achievement(s).</div>',
                    unsafe_allow_html=True
                )

            # ── 5. Missing sections ───────────────────
            st.markdown("---")
            st.markdown("#### 📋 Missing resume sections")
            if report["missing_sections"]:
                for section in report["missing_sections"]:
                    hints = {
                        "summary"     : "Add a 2–3 line career summary at the top. ATS systems and recruiters both scan this first.",
                        "experience"  : "Add a Work Experience or Projects section describing what you've built or done.",
                        "education"   : "Add your degree, institution, graduation year and CGPA.",
                        "skills"      : "Add a dedicated Skills section with comma-separated keywords — this is what ATS scans first.",
                        "achievements": "Add certifications, awards, or notable achievements. These differentiate you."
                    }
                    st.markdown(
                        f'<div class="improve-card">'
                        f'<div class="improve-title">📌 Add a <strong>{section.title()}</strong> section</div>'
                        f'<div style="font-size:0.85rem;color:#666;">{hints.get(section, "")}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div class="success-box">✅ All key sections are present!</div>', unsafe_allow_html=True)

            # ── 6. Contact info ───────────────────────
            st.markdown("---")
            st.markdown("#### 📬 Contact information")
            missing_contact = report["contact_check"]
            if missing_contact:
                st.markdown(
                    f'<div class="warn-box">'
                    f'Missing from resume: <strong>{", ".join(missing_contact)}</strong><br>'
                    f'Add these to the top of your resume — recruiters and ATS systems expect them.'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<div class="success-box">✅ All contact details present!</div>', unsafe_allow_html=True)

            # ── 7. Resume length ──────────────────────
            st.markdown("---")
            st.markdown("#### 📏 Resume length")
            lc = report["length_check"]
            box_class = "success-box" if lc["status"] == "good" else "warn-box"
            icon = "✅" if lc["status"] == "good" else "⚠️"
            st.markdown(
                f'<div class="{box_class}">{icon} {lc["message"]}</div>',
                unsafe_allow_html=True
            )

    else:
        st.info("Upload a resume and paste a job description, then click **Analyze resume**.")