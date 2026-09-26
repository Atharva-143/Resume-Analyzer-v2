def match_skills(resume_skills, jd_skills):

    matched_skills = []
    missing_skills = []
    for skill in jd_skills:

        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
    return matched_skills, missing_skills


def calculate_score(matched_skills, jd_skills):

    if len(jd_skills) == 0:
        return 0

    skill_score = (
        len(matched_skills) / len(jd_skills)
    ) * 100

    return round(skill_score, 2)

