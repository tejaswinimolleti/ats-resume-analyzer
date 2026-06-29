# app/utils.py

import os
import re

def save_text(text: str, output_path: str) -> None:
    """Save extracted text to a .txt file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def load_text(file_path: str) -> str:
    """Load text from a saved .txt file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def clean_filename(name: str) -> str:
    """Strip special characters from a filename."""
    return re.sub(r'[^a-zA-Z0-9_\-.]', '_', name)

def word_count(text: str) -> int:
    """Return word count of a text string."""
    return len(text.split())