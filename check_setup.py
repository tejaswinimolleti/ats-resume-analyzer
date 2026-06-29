import fitz                  # PyMuPDF
import docx                  # python-docx
import spacy
import nltk
import sklearn
import sentence_transformers
import streamlit
import numpy

# Print package versions
print("PyMuPDF:", fitz.version)
print("python-docx:", docx.__version__)
print("spaCy:", spacy.__version__)
print("NLTK:", nltk.__version__)
print("scikit-learn:", sklearn.__version__)
print("sentence-transformers:", sentence_transformers.__version__)
print("streamlit:", streamlit.__version__)
print("numpy:", numpy.__version__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

print("\nspaCy model loaded:", nlp.meta["name"])

print("\nAll good! Setup complete.")