SECTION_HEADINGS = [
    "PROFILE",
    "SUMMARY",
    "PROFESSIONAL EXPERIENCE",
    "EXPERIENCE",
    "INTERNSHIP EXPERIENCE",
    "EDUCATION",
    "SKILLS",
    "TECHNICAL SKILLS",
    "PROJECTS",
    "LANGUAGES",
    "CERTIFICATIONS"
]


def detect_sections(text):

    sections = {}

    current_section = None

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if line.upper() in SECTION_HEADINGS:

            current_section = line.upper()

            if current_section == "TECHNICAL SKILLS":
                current_section = "SKILLS"

            elif current_section == "INTERNSHIP EXPERIENCE":
                current_section = "EXPERIENCE"

            sections[current_section] = ""

        elif current_section:
            sections[current_section] += line + " "

    return sections