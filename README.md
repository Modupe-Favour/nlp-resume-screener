# 🤖 NLP Resume Screener

An NLP-powered web app that scores how well a CV matches a job
description — highlighting missing skills and providing
actionable improvement tips.

## 🔗 Live Demo
[Click here to view the live app](#) ← Add your deployed link

## 📌 Project Overview
Job seekers often struggle to tailor their CVs to specific roles.
This tool solves that by:
- Calculating a match score using TF-IDF cosine similarity
- Identifying which required skills are present or missing
- Extracting and comparing top keywords from both documents
- Providing personalised tips on how to improve the CV

## 🛠️ Tools & Technologies
| Area | Tools |
|---|---|
| Language | Python 3.11 |
| NLP | spaCy, NLTK |
| ML | Scikit-learn (TF-IDF, Cosine Similarity) |
| Visualisation | Plotly, Plotly Dash |
| UI Framework | Dash Bootstrap Components |
| IDE | VS Code |

## 🚀 How to Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/nlp-resume-screener.git
cd nlp-resume-screener
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```
Then open: http://127.0.0.1:8050

## 📁 Project Structure
```
nlp-resume-screener/
├── Data/               # Sample CV and job description
├── Notebook/           # NLP analysis notebook
├── app.py              # Plotly Dash web app
├── nlp_utils.py        # NLP utility functions
├── requirements.txt
└── README.md
```

## 💼 Use Case
Built to help job seekers optimise their CVs before applying —
especially useful for data science and tech roles where specific
keywords and skills are critical for passing ATS screening systems.