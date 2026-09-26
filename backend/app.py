from flask import Flask, render_template, request
import os

from pdf_parser import extract_text_from_pdf
from text_cleaner import clean_text
from section_detector import detect_sections
from skill_extractor import extract_skills
from skill_matcher import match_skills, calculate_score
from keyword_matcher import extract_keywords


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # Get Job Description
        job_description = request.form.get("job_description", "")

        print("Job Description:")
        print(job_description)

        # Check if Job Description is empty
        if not job_description.strip():
            return render_template(
                "index.html",
                error="Please enter a Job Description."
            )

        # Extract skills from Job Description
        jd_skills = extract_skills(job_description)

        # Extract meaningful JD keywords
        jd_keywords = extract_keywords(job_description)

        print("JD Skills:", jd_skills)
        print("JD Keywords:", jd_keywords)

        # Get uploaded resume
        file = request.files.get("resume")

        # Check if resume was uploaded
        if not file or file.filename == "":
            return render_template(
                "index.html",
                error="Please upload a resume PDF."
            )

        # Check file type
        if (
            not file.filename.lower().endswith(".pdf")
            or file.mimetype != "application/pdf"
        ):
            return render_template(
                "index.html",
                error="Please upload a valid PDF file."
            )

        # Upload folder
        upload_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "uploads"
        )

        # Save PDF
        file.save(
            os.path.join(upload_folder, file.filename)
        )

        pdf_path = os.path.join(
            upload_folder,
            file.filename
        )

        # Extract text from PDF
        resume_text = extract_text_from_pdf(pdf_path)

        # Clean extracted text
        cleaned_text = clean_text(resume_text)

        print("===== CLEANED RESUME TEXT =====")
        print(repr(cleaned_text))
        print("================================")

        # Detect resume sections
        sections = detect_sections(cleaned_text)

        print(sections)

        # Calculate Resume Section Score
        section_score = 0

        for section in ["SKILLS", "EXPERIENCE", "EDUCATION", "PROJECTS"]:
            if sections.get(section, "").strip():
                section_score += 25

        print("Resume Section Score:", section_score)

        # Get SKILLS section
        skills_text = sections.get("SKILLS", "")

        print("SKILLS SECTION:")
        print(skills_text)

        # Extract Resume skills
        skills = extract_skills(skills_text)

        print("Skills Found:", skills)

        # Match Resume Skills with JD Skills
        matched_skills, missing_skills = match_skills(
            skills,
            jd_skills
        )

        print("Matched Skills:", matched_skills)
        print("Missing Skills:", missing_skills)

        # Convert matched skills to lowercase
        # so they can be excluded from keyword-based scoring
        matched_skill_keywords = [
            skill.lower() for skill in matched_skills
        ]

        # -------------------------------------------------
        # Experience Relevance Score
        # -------------------------------------------------

        experience_text = sections.get("EXPERIENCE", "")
        projects_text = sections.get("PROJECTS", "")

        relevant_text = (
            experience_text + " " + projects_text
        )

        relevant_text = relevant_text.lower()

        # Remove skills already counted by Skill Match
        experience_keywords = [
            keyword
            for keyword in jd_keywords
            if keyword not in matched_skill_keywords
        ]

        # Related-word mappings for Experience matching
        experience_aliases = {
            "development": ["develop", "developed", "developing"],
            "apis": ["api", "apis"],
            "programming": ["program", "programming"],
            "debug": ["debug", "debugging", "debugged"],
            "performance": ["performance", "optimization", "optimized"],
            "collaborate": ["collaborate", "collaboration", "teamwork"],
        }

        matched_relevant_keywords = []

        for keyword in experience_keywords:

            if keyword in relevant_text:
                matched_relevant_keywords.append(keyword)
                continue

            if keyword in experience_aliases:
                for alias in experience_aliases[keyword]:
                    if alias in relevant_text:
                        matched_relevant_keywords.append(keyword)
                        break

        experience_score = 0

        if experience_keywords:
            experience_score = (
                len(matched_relevant_keywords)
                / len(experience_keywords)
            ) * 100

        print(
            "Matched Relevant Keywords:",
            matched_relevant_keywords
        )

        print(
            "Experience Relevance Score:",
            experience_score
        )

        # -------------------------------------------------
        # Keyword Relevance Score
        # -------------------------------------------------

        # Extract keywords from the complete resume
        resume_keywords = extract_keywords(cleaned_text)

        remaining_jd_keywords = [
            keyword
            for keyword in jd_keywords
            if keyword not in matched_skill_keywords
        ]

        # Find remaining JD keywords present in resume
        matched_keywords = [
            keyword
            for keyword in remaining_jd_keywords
            if keyword in resume_keywords
        ]

        print("Resume Keywords:", resume_keywords)
        print("Remaining JD Keywords:", remaining_jd_keywords)
        print("Matched Keywords:", matched_keywords)

        # Calculate ATS Skill Match Score
        score = calculate_score(
            matched_skills,
            jd_skills
        )

        # Calculate Keyword Relevance Score
        keyword_score = 0

        if remaining_jd_keywords:
            keyword_score = (
                len(matched_keywords)
                / len(remaining_jd_keywords)
            ) * 100

        # -------------------------------------------------
        # Multi-Factor ATS Score
        # -------------------------------------------------

        final_score = (
        (score * 0.50)
        + (section_score * 0.20)
        + (keyword_score * 0.15)
        + (experience_score * 0.15)
    )

        print("Keyword Relevance Score:", keyword_score)
        final_score = round(final_score, 2)

        # Generate Resume Improvement Recommendations

        recommendations = []

        if missing_skills:
            recommendations.append(
                "Consider adding relevant missing skills: "
                + ", ".join(missing_skills)
            )

        if section_score < 100:
            recommendations.append(
                "Add or improve important resume sections such as "
                "Skills, Experience, Education, and Projects."
            )

        if keyword_score < 50:
            recommendations.append(
                "Improve keyword relevance by using more terms related "
                "to the job description."
            )

        if experience_score < 50:
            recommendations.append(
                "Improve experience relevance by highlighting projects "
                "or experience related to the job requirements."
            )

        if not recommendations:
            recommendations.append(
                "Resume has good alignment with the provided job description."
            )

        print("Final ATS Score:", final_score)

        # Required skills count
        matched_skills_count = len(matched_skills)
        missing_skills_count = len(missing_skills)

        required_skills_count = (
            matched_skills_count
            + missing_skills_count
        )

        print("ATS Score:", score)

        print("File saved:", file.filename)

        # Send results to webpage
        return render_template(
            "index.html",
            score=final_score,
            section_score=section_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            required_skills_count=required_skills_count,
            matched_skills_count=matched_skills_count,
            missing_skills_count=missing_skills_count,
            recommendations=recommendations
        )

    # Normal GET request
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)