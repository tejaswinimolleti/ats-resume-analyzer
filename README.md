# ATS Resume Analyzer

An ML-powered web app that analyzes resumes against job descriptions 
and gives an ATS compatibility score.

## Live Demo
https://ats-resume-analyzer-e7txpyeulkpmjaxnwvd9m2.streamlit.app

## Tech Stack
Python · spaCy · scikit-learn · NLTK · PyMuPDF · Streamlit

## Features
- Upload PDF or DOCX resume
- Paste any job description
- Get ATS score out of 100
- See matched, missing, and extra skills
- Actionable recommendation

## How to run locally
pip install -r requirements.txt
streamlit run main.py