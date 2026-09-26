import re
KNOWN_SKILLS = [
    "Python",
    "C++",
    "Java",
    "JavaScript",
    "SQL",
    "HTML",
    "CSS",
    "Flask",
    "React",
    "Node.js",
    "Express.js",
    "Git",
    "GitHub",
    "AWS",
    "MongoDB",
    "MySQL",
    "Docker",
    "REST API",
    "Data Structures",
    "Algorithms",
    "OOP"
]

SKILL_ALIASES = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "reactjs": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "rest": "REST API"
}

def extract_skills(skills_text):

    found_skills = []

    skills_text = skills_text.lower()

    # Replace skill aliases with standard skill names
    for alias, standard_skill in SKILL_ALIASES.items():
        skills_text = re.sub(
            r"\b" + re.escape(alias) + r"\b",
            standard_skill.lower(),
            skills_text
        )

    # Find known skills
    for skill in KNOWN_SKILLS:

        if re.search(
            r"\b" + re.escape(skill.lower()) + r"\b",
            skills_text
        ):
            found_skills.append(skill)

    return found_skills