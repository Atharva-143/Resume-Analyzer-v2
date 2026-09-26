import re

from skill_extractor import KNOWN_SKILLS


def extract_keywords(text):

    text = text.lower()

    keywords = []

    # Extract known skills as complete phrases
    for skill in KNOWN_SKILLS:

        if re.search(
            r"\b" + re.escape(skill.lower()) + r"\b",
            text
        ):
            keywords.append(skill.lower())

    # Extract important multi-word phrases
    important_phrases = [
        "version control",
        "problem solving",
        "object oriented programming",
        "data structures",
        "rest api"
    ]

    for phrase in important_phrases:

        if phrase in text and phrase not in keywords:
            keywords.append(phrase)

    # Extract individual words
    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b",
        text
    )

    stop_words = {
    "the", "a", "an", "and", "or", "to", "of",
    "in", "on", "for", "with", "using", "is",
    "are", "be", "this", "that", "as", "by",
    "from", "will", "work", "working", "required",
    "skills", "responsibilities",

    # Generic job-description words
    "software", "developer", "intern",
    "build", "web", "applications",
    "develop", "test", "use", "apply",
    "solve", "problems", "team",
    "design", "implement", "features",
    "improve", "application"
    }

    for word in words:

        if word not in stop_words and len(word) > 2:

            # Skip words already included in an important phrase
            part_of_phrase = any(
                word in phrase.split()
                for phrase in important_phrases
                if phrase in text
            )

            if part_of_phrase:
                continue

            # Don't add words that are already part of a known skill
            already_part_of_skill = any(
                word in skill.lower().split()
                for skill in KNOWN_SKILLS
                if len(skill.split()) > 1
            )

            if not already_part_of_skill and word not in keywords:
                keywords.append(word)

    return keywords