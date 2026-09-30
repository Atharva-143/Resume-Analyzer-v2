# Resume Analyzer v2

## 📌 Overview

Resume Analyzer v2 is a Flask-based web application that analyzes a candidate's resume against a given job description. It extracts information from the uploaded resume, compares relevant skills and keywords with the job requirements, calculates an ATS-style score, and provides recommendations to improve the resume.

## 🎯 Problem Statement

Recruiters often need to review resumes against specific job requirements. Manually identifying relevant skills, keywords, and missing requirements can be time-consuming. Resume Analyzer v2 helps automate this initial analysis by comparing a resume with a job description and highlighting areas for improvement.

## ✨ Features

- Upload and extract text from PDF resumes
- Analyze resumes against a job description
- Detect relevant resume sections
- Extract and match required skills
- Calculate an ATS-style score
- Identify matched and missing skills
- Provide resume improvement recommendations
- Simple web-based interface
- Deployed and accessible online

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **PDF Processing:** pdfplumber
- **Deployment:** Render
- **Production Server:** Gunicorn
- **Version Control:** Git, GitHub

## ⚙️ How It Works

1. User uploads a resume in PDF format.
2. User provides a job description.
3. The application extracts text from the resume.
4. Resume sections and relevant skills are identified.
5. Required skills and keywords from the job description are compared with the resume.
6. An ATS-style score is calculated.
7. Matched skills, missing skills, and improvement recommendations are displayed.

## 🎯 ATS Scoring

The analyzer evaluates the resume against the job description using factors such as:

- Required skills
- Matched skills
- Missing skills
- Keyword relevance
- Resume section coverage
- Experience and project relevance

The final result includes an ATS-style percentage score along with matched/missing skills and improvement recommendations.

## 📁 Project Structure

Resume-Analyzer-v2/
├── backend/
│   ├── app.py
│   ├── keyword_matcher.py
│   ├── pdf_parser.py
│   ├── requirements.txt
│   ├── section_detector.py
│   ├── skill_extractor.py
│   ├── skill_matcher.py
│   ├── text_cleaner.py
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   └── templates/
│       └── index.html
├── .gitignore
└── README.md

## 🚀 Installation & Run Locally

### 1. Clone the repository

git clone https://github.com/Atharva-143/Resume-Analyzer-v2.git
cd Resume-Analyzer-v2

### 2. Create a virtual environment

python -m venv venv

### 3. Activate the virtual environment

For Windows PowerShell:

.\venv\Scripts\Activate.ps1

### 4. Install dependencies

cd backend
pip install -r requirements.txt

### 5. Run the application

python app.py

The application will be available at:

http://127.0.0.1:5000

## 🌐 Live Demo

The deployed application is available online through Render.

**Live Demo:** [https://resume-analyzer-v2-1.onrender.com](https://resume-analyzer-v2-1.onrender.com)

## 📸 Screenshots

### Resume Analyzer Interface

The application allows users to upload a resume and provide a job description for analysis.

### Analysis Results

The results page displays the ATS score, matched skills, missing skills, and improvement recommendations.

## 🔮 Future Improvements

* Improve ATS scoring accuracy
* Improve skill and keyword extraction
* Support additional resume formats
* Provide more detailed resume feedback
* Enhance the user interface
* Add authentication and user history

## 👨‍💻 Author

**Atharva Besikrao**

Computer Engineering Student

GitHub: [https://github.com/Atharva-143](https://github.com/Atharva-143)

