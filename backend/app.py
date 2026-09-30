from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid

from pdf_parser import extract_text_from_pdf
from text_cleaner import clean_text
from section_detector import detect_sections
from skill_extractor import extract_skills
from skill_matcher import match_skills, calculate_score
from keyword_matcher import extract_keywords


app = Flask(__name__)

# Secret key for storing analysis results safely in the session
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "resume-analyzer-development-key"
)

# Maximum upload size: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# -------------------------------------------------
# Helper: render validation/error message
# -------------------------------------------------

def show_error(message):
    return render_template(
        "index.html",
        error=message
    )


# -------------------------------------------------
# Handle very large file uploads
# -------------------------------------------------

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(error):
    return show_error(
        "The uploaded file is too large. Please upload a PDF smaller than 5 MB."
    )


# -------------------------------------------------
# Home / Resume Analysis
# -------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    # -------------------------------------------------
    # GET request
    # -------------------------------------------------

    if request.method == "GET":

        # Display previous analysis result if available
        analysis = session.get("analysis_result")

        if analysis:
            return render_template(
                "index.html",
                **analysis
            )

        return render_template("index.html")


    # -------------------------------------------------
    # POST request
    # -------------------------------------------------

    # Get Job Description
    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    # Check if Job Description is empty
    if not job_description:
        return show_error(
            "Please enter a Job Description."
        )

    # Optional protection against extremely large JD text
    if len(job_description) > 20000:
        return show_error(
            "Job Description is too long. Please keep it under 20,000 characters."
        )


    # -------------------------------------------------
    # Get uploaded resume
    # -------------------------------------------------

    file = request.files.get("resume")

    # Check if resume was uploaded
    if not file or not file.filename:
        return show_error(
            "Please upload a resume PDF."
        )


    # -------------------------------------------------
    # Validate filename
    # -------------------------------------------------

    original_filename = file.filename

    safe_filename = secure_filename(
        original_filename
    )

    if not safe_filename:
        return show_error(
            "The uploaded file has an invalid filename."
        )


    # -------------------------------------------------
    # Validate PDF extension
    # -------------------------------------------------

    if not safe_filename.lower().endswith(".pdf"):
        return show_error(
            "Please upload a PDF file only."
        )


    # -------------------------------------------------
    # Validate actual PDF file signature
    # -------------------------------------------------
    # A real PDF normally begins with %PDF.
    # This prevents someone from simply renaming
    # another file to .pdf.

    try:
        file_header = file.stream.read(5)
        file.stream.seek(0)

    except Exception:
        return show_error(
            "Unable to read the uploaded file."
        )

    if file_header != b"%PDF-":
        return show_error(
            "The uploaded file is not a valid PDF."
        )


    # -------------------------------------------------
    # Create upload directory
    # -------------------------------------------------

    upload_folder = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        "uploads"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    # -------------------------------------------------
    # Generate unique temporary filename
    # -------------------------------------------------

    temporary_filename = (
        f"{uuid.uuid4().hex}.pdf"
    )

    pdf_path = os.path.join(
        upload_folder,
        temporary_filename
    )


    try:

        # -------------------------------------------------
        # Save uploaded PDF
        # -------------------------------------------------

        file.save(pdf_path)


        # -------------------------------------------------
        # Extract text from PDF
        # -------------------------------------------------

        try:
            resume_text = extract_text_from_pdf(
                pdf_path
            )

        except Exception:
            return show_error(
                "The PDF could not be processed. "
                "It may be corrupted, encrypted, or unreadable."
            )


        # -------------------------------------------------
        # Check extraction result
        # -------------------------------------------------

        if not resume_text or not resume_text.strip():
            return show_error(
                "No readable text could be extracted from this PDF. "
                "Please upload a text-based resume PDF."
            )


        # -------------------------------------------------
        # Clean extracted text
        # -------------------------------------------------

        try:
            cleaned_text = clean_text(
                resume_text
            )

        except Exception:
            return show_error(
                "The resume text could not be processed."
            )


        if not cleaned_text or not cleaned_text.strip():
            return show_error(
                "The resume does not contain enough readable text for analysis."
            )


        # -------------------------------------------------
        # Extract skills and keywords from JD
        # -------------------------------------------------

        try:
            jd_skills = extract_skills(
                job_description
            )

            jd_keywords = extract_keywords(
                job_description
            )

        except Exception:
            return show_error(
                "The Job Description could not be analyzed. "
                "Please try again with a valid Job Description."
            )


        # -------------------------------------------------
        # Detect resume sections
        # -------------------------------------------------

        try:
            sections = detect_sections(
                cleaned_text
            )

        except Exception:
            return show_error(
                "The resume sections could not be detected."
            )


        # -------------------------------------------------
        # Calculate Resume Section Score
        # -------------------------------------------------

        section_score = 0

        for section in [
            "SKILLS",
            "EXPERIENCE",
            "EDUCATION",
            "PROJECTS"
        ]:

            if sections.get(
                section,
                ""
            ).strip():

                section_score += 25


        # -------------------------------------------------
        # Extract Resume Skills
        # -------------------------------------------------

        skills_text = sections.get(
            "SKILLS",
            ""
        )

        try:
            skills = extract_skills(
                skills_text
            )

        except Exception:
            # If skill extraction fails, continue safely
            skills = []


        # -------------------------------------------------
        # Match Resume Skills with JD Skills
        # -------------------------------------------------

        try:

            matched_skills, missing_skills = match_skills(
                skills,
                jd_skills
            )

        except Exception:
            return show_error(
                "Skills could not be matched successfully."
            )


        # -------------------------------------------------
        # Convert matched skills to lowercase
        # -------------------------------------------------

        matched_skill_keywords = [
            skill.lower()
            for skill in matched_skills
        ]


        # -------------------------------------------------
        # Experience Relevance Score
        # -------------------------------------------------

        experience_text = sections.get(
            "EXPERIENCE",
            ""
        )

        projects_text = sections.get(
            "PROJECTS",
            ""
        )

        relevant_text = (
            experience_text
            + " "
            + projects_text
        ).lower()


        # Remove skills already counted
        experience_keywords = [
            keyword
            for keyword in jd_keywords
            if keyword not in matched_skill_keywords
        ]


        # Related-word mappings
        experience_aliases = {

            "development": [
                "develop",
                "developed",
                "developing"
            ],

            "apis": [
                "api",
                "apis"
            ],

            "programming": [
                "program",
                "programming"
            ],

            "debug": [
                "debug",
                "debugging",
                "debugged"
            ],

            "performance": [
                "performance",
                "optimization",
                "optimized"
            ],

            "collaborate": [
                "collaborate",
                "collaboration",
                "teamwork"
            ],
        }


        matched_relevant_keywords = []


        for keyword in experience_keywords:

            if keyword in relevant_text:

                matched_relevant_keywords.append(
                    keyword
                )

                continue


            if keyword in experience_aliases:

                for alias in experience_aliases[keyword]:

                    if alias in relevant_text:

                        matched_relevant_keywords.append(
                            keyword
                        )

                        break


        experience_score = 0

        if experience_keywords:

            experience_score = (
                len(matched_relevant_keywords)
                / len(experience_keywords)
            ) * 100


        # -------------------------------------------------
        # Keyword Relevance Score
        # -------------------------------------------------

        try:

            resume_keywords = extract_keywords(
                cleaned_text
            )

        except Exception:

            resume_keywords = []


        remaining_jd_keywords = [
            keyword
            for keyword in jd_keywords
            if keyword not in matched_skill_keywords
        ]


        matched_keywords = [
            keyword
            for keyword in remaining_jd_keywords
            if keyword in resume_keywords
        ]


        keyword_score = 0

        if remaining_jd_keywords:

            keyword_score = (
                len(matched_keywords)
                / len(remaining_jd_keywords)
            ) * 100


        # -------------------------------------------------
        # ATS Skill Match Score
        # -------------------------------------------------

        try:

            score = calculate_score(
                matched_skills,
                jd_skills
            )

        except Exception:

            score = 0


        # -------------------------------------------------
        # Multi-Factor ATS Score
        # -------------------------------------------------

        final_score = (
            (score * 0.50)
            + (section_score * 0.20)
            + (keyword_score * 0.15)
            + (experience_score * 0.15)
        )


        final_score = round(
            final_score,
            2
        )


        # -------------------------------------------------
        # Generate Recommendations
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Required Skills Count
        # -------------------------------------------------

        matched_skills_count = len(
            matched_skills
        )

        missing_skills_count = len(
            missing_skills
        )

        required_skills_count = (
            matched_skills_count
            + missing_skills_count
        )


        # -------------------------------------------------
        # Store results for safe GET redirect
        # -------------------------------------------------

        analysis_result = {

            "score": final_score,

            "section_score": section_score,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "required_skills_count":
                required_skills_count,

            "matched_skills_count":
                matched_skills_count,

            "missing_skills_count":
                missing_skills_count,

            "recommendations":
                recommendations
        }


        session["analysis_result"] = (
            analysis_result
        )


        # -------------------------------------------------
        # Redirect to GET
        # -------------------------------------------------
        # This prevents the browser from re-submitting
        # the form when the user refreshes the result page.

        return redirect(
            url_for("home")
        )


    except Exception:
        # Catch unexpected errors without exposing
        # technical details to the user.

        return show_error(
            "Something went wrong while analyzing the resume. "
            "Please try another PDF."
        )


    finally:

        # -------------------------------------------------
        # Delete temporary uploaded PDF
        # -------------------------------------------------
        # The uploaded resume is only needed during analysis.
        # This prevents unnecessary files from accumulating.

        if os.path.exists(pdf_path):

            try:
                os.remove(pdf_path)

            except OSError:
                pass


# -------------------------------------------------
# Run application
# -------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True
    )