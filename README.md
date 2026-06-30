# 📄 ATS Resume Analyzer

> Upload a resume + paste a job description → get an instant ATS compatibility score, skill gap breakdown, and an actionable improvement plan.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://ats-resume-analyzer-e7txpyeulkpmjaxnwvd9m2.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[🚀 Try it live](https://ats-resume-analyzer-e7txpyeulkpmjaxnwvd9m2.streamlit.app)** — no install needed.

<!--
  TODO: Add a screenshot or GIF here. This is the single highest-impact
  thing you can do for views — visitors decide in ~5 seconds whether
  to keep reading. Record a 10-15s screen capture of uploading a resume
  and getting a score, convert to GIF (e.g. with ezgif.com), and embed:

  ![demo](docs/demo.gif)
-->

## Why this exists

Most resumes get filtered out by Applicant Tracking Systems (ATS) before a human ever sees them. This tool simulates that filtering process — scoring your resume against a specific job description the same way many real ATS pipelines do — and tells you *exactly* what's missing, not just a vague score.

## Features

- 📎 **Upload PDF or DOCX** resumes — parsed automatically with PyMuPDF / python-docx
- 🎯 **ATS Score (0–100)** using TF-IDF + cosine similarity against the job description
- ✅ **Matched, missing, and extra skills** detected against a database of 300+ skills across multiple domains
- 🛠 **Resume Improvement Advisor** — a second tab with concrete, actionable suggestions to raise your score
- ⚡ Fast, fully local NLP pipeline (spaCy + NLTK) — no external API calls needed to score

## Tech Stack

| Layer | Tools |
|---|---|
| Frontend | Streamlit |
| NLP | spaCy, NLTK, sentence-transformers |
| Scoring | scikit-learn (TF-IDF + cosine similarity) |
| Parsing | PyMuPDF (PDF), python-docx (DOCX) |
| Deployment | Streamlit Community Cloud |

## How it works

1. Upload your resume (PDF/DOCX) and paste the target job description
2. The text is cleaned and normalized (`apps/preprocessor.py`)
3. Skills and keywords are extracted and matched against the JD (`apps/parser.py`)
4. A similarity score is computed and broken down into matched / missing / extra skills (`apps/scorer.py`)
5. The **Improvement Plan** tab (`apps/advisor.py`) turns the gaps into specific, actionable suggestions

## Run it locally

```bash
git clone https://github.com/tejaswinimolleti/ats-resume-analyzer.git
cd ats-resume-analyzer
pip install -r requirements.txt
streamlit run main.py
```

## Project structure

```
ats-resume-analyzer/
├── apps/
│   ├── parser.py        # Resume/JD text extraction
│   ├── preprocessor.py  # Text cleaning & normalization
│   ├── scorer.py        # TF-IDF + cosine similarity scoring
│   ├── advisor.py        # Resume improvement recommendations
│   └── utils.py
├── data/                 # Sample resumes & job descriptions
├── main.py               # Streamlit app entry point
└── requirements.txt
```

## Roadmap

- [ ] Support for multiple job descriptions / batch scoring
- [ ] Export improvement plan as PDF
- [ ] Industry-specific skill weighting

## Contributing

Issues and PRs are welcome — feel free to open one if you spot a bug or have an idea.

## License

MIT — see [LICENSE](LICENSE) for details.

---

⭐ If this project helped you, consider starring the repo — it genuinely helps with visibility.
