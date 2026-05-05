import re
import pandas as pd
import nltk
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words("english"))

# ── Tech skills master list ──────────────────────────────────
TECH_SKILLS = [
    "python", "sql", "r", "java", "scala", "spark",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas",
    "numpy", "matplotlib", "seaborn", "plotly", "tableau",
    "power bi", "aws", "gcp", "azure", "docker", "kubernetes",
    "airflow", "dbt", "git", "mlops", "nlp", "deep learning",
    "machine learning", "data science", "statistics",
    "neural network", "transformer", "bert", "llm",
    "excel", "mongodb", "postgresql", "mysql", "hadoop",
    "fastapi", "flask", "django", "streamlit", "dash",
    "computer vision", "reinforcement learning", "xgboost",
    "lightgbm", "shap", "feature engineering", "etl"
]

def clean_text(text):
    """Clean and preprocess text"""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    tokens = word_tokenize(text)
    tokens = [t for t in tokens
              if t not in stop_words and len(t) > 2]
    return " ".join(tokens)

def calculate_match_score(cv_text, job_text):
    """Calculate TF-IDF cosine similarity score"""
    cv_clean = clean_text(cv_text)
    job_clean = clean_text(job_text)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([cv_clean, job_clean])
    score = cosine_similarity(
        tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)

def find_skill_gaps(cv_text, job_text):
    """Find skills present and missing"""
    cv_lower = cv_text.lower()
    job_lower = job_text.lower()
    present = []
    missing = []
    for skill in TECH_SKILLS:
        if skill in job_lower:
            if skill in cv_lower:
                present.append(skill)
            else:
                missing.append(skill)
    return present, missing

def extract_top_keywords(text, top_n=20):
    """Extract top keywords using spaCy"""
    doc = nlp(text.lower())
    keywords = [token.lemma_ for token in doc
                if token.pos_ in ["NOUN", "PROPN"]
                and not token.is_stop
                and len(token.text) > 2]
    freq = pd.Series(keywords).value_counts().head(top_n)
    return freq

def get_score_label(score):
    """Return label and colour based on score"""
    if score >= 70:
        return "Strong Match 🟢", "#00CC96"
    elif score >= 45:
        return "Moderate Match 🟡", "#FFA500"
    else:
        return "Weak Match 🔴", "#EF553B"

def get_improvement_tips(missing, score):
    """Return actionable improvement tips"""
    tips = []
    if score < 45:
        tips.append("Your CV has a low match score. "
                    "Rewrite your summary to include "
                    "keywords from the job description.")
    if len(missing) > 5:
        tips.append(f"You are missing {len(missing)} key skills. "
                    "Consider adding relevant projects or courses "
                    "to address these gaps.")
    if missing:
        top_missing = ", ".join(missing[:5])
        tips.append(f"Priority skills to add or learn: {top_missing}.")
    if score >= 70:
        tips.append("Great match! Make sure your experience bullet "
                    "points use the exact keywords from the job posting.")
    return tips