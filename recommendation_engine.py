
# =========================================================
# INTERN ALIGN AI - RECOMMENDATION ENGINE
# =========================================================

import re


# =========================================================
# 1. SKILL SYNONYMS
# =========================================================

SKILL_SYNONYMS = {
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "js": "javascript",
    "powerbi": "power bi",
    "data analytics": "data analysis",
    "python programming": "python",
    "deep-learning": "deep learning"
}


# =========================================================
# 2. NORMALIZE SKILLS
# =========================================================

def normalize_skill(skill):

    skill = str(skill).strip().lower()

    skill = re.sub(r"\s+", " ", skill)

    return SKILL_SYNONYMS.get(skill, skill)


# =========================================================
# 3. NORMALIZE DEGREE
# =========================================================

def normalize_degree(degree):

    degree = str(degree).strip().lower()

    degree = degree.replace(".", "").replace(" ", "")

    if degree in ["be", "btech", "bachelorofengineering",
                  "bacheloroftechnology"]:

        return "be/btech"

    return degree


# =========================================================
# 4. CALCULATE SKILL MATCH
# =========================================================

def calculate_match(student_skills, required_skills):

    student_set = {
        normalize_skill(skill)
        for skill in student_skills
        if str(skill).strip()
    }

    required_set = {
        normalize_skill(skill)
        for skill in required_skills
        if str(skill).strip()
    }

    matched = student_set.intersection(required_set)

    missing = required_set - matched

    if len(required_set) == 0:

        percentage = 0

    else:

        percentage = (
            len(matched) / len(required_set)
        ) * 100

    return {
        "match_percentage": round(percentage, 2),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing)
    }


# =========================================================
# 5. CHECK ELIGIBILITY
# =========================================================

def check_eligibility(
    student_degree,
    student_year,
    experience_level,
    internship
):

    required_degree = internship.get(
        "eligible_degree", "Any"
    )

    required_year = internship.get(
        "eligible_year", "Any"
    )

    required_experience = internship.get(
        "experience_level", "Beginner"
    )

    # Degree check

    if str(required_degree).strip().lower() == "any":

        degree_match = True

    else:

        degree_match = (
            normalize_degree(student_degree)
            == normalize_degree(required_degree)
        )

    # Year check

    if str(required_year).strip().lower() == "any":

        year_match = True

    else:

        year_match = (
            str(student_year).strip().lower()
            == str(required_year).strip().lower()
        )

    # Experience check

    experience_ranks = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3
    }

    student_rank = experience_ranks.get(
        str(experience_level).strip().lower(),
        1
    )

    required_rank = experience_ranks.get(
        str(required_experience).strip().lower(),
        1
    )

    experience_match = student_rank >= required_rank

    eligible = (
        degree_match
        and year_match
        and experience_match
    )

    reasons = []

    if not degree_match:
        reasons.append("Degree requirement not met")

    if not year_match:
        reasons.append("Year requirement not met")

    if not experience_match:
        reasons.append("Experience requirement not met")

    if eligible:
        eligibility_reason = (
            "You meet all eligibility requirements."
        )

    else:
        eligibility_reason = "; ".join(reasons)

    return {
        "eligible": eligible,
        "degree_match": degree_match,
        "year_match": year_match,
        "experience_match": experience_match,
        "eligibility_reason": eligibility_reason
    }


# =========================================================
# 6. RANK INTERNSHIPS
# =========================================================

def rank_internships(
    student_skills,
    internships,
    preferred_domain,
    preferred_work_mode,
    student_degree,
    student_year,
    experience_level
):

    recommendations = []

    for internship in internships:

        required_skills = internship.get("skills", [])

        # Skill matching

        skill_result = calculate_match(
            student_skills,
            required_skills
        )

        skill_score = skill_result["match_percentage"]

        # Domain matching

        internship_domain = str(
            internship.get("domain", "")
        ).strip().lower()

        if isinstance(preferred_domain, str):

            preferred_domains = [preferred_domain]

        else:

            preferred_domains = preferred_domain or []

        preferred_domains = [
            str(domain).strip().lower()
            for domain in preferred_domains
        ]

        domain_match = (
    100
    if "any" in preferred_domains
    or internship_domain in preferred_domains
    else 0
)

        # Work mode matching

        internship_mode = str(
            internship.get("work_mode", "")
        ).strip().lower()

        student_mode = str(
            preferred_work_mode or "Any"
        ).strip().lower()

        work_mode_match = (
            100
            if student_mode == "any"
            or internship_mode == student_mode
            else 0
        )

        # Overall score

        combined_score = (
            skill_score * 0.80
            + domain_match * 0.10
            + work_mode_match * 0.10
        )

        # Eligibility

        eligibility = check_eligibility(
            student_degree,
            student_year,
            experience_level,
            internship
        )

        # Recommendation explanation

        matched_skills = skill_result["matched_skills"]

        if matched_skills:

            recommendation_reason = (
                "Your profile matches these required skills: "
                + ", ".join(matched_skills)
            )

        else:

            recommendation_reason = (
                "You can improve your match by learning "
                "the required technical skills."
            )

        # Store result

        result = {

            "title": internship.get("title", "Internship"),

            "company": internship.get("company", "Unknown"),

            "match_percentage": round(combined_score, 2),

            "skill_match": skill_score,

            "domain_match": domain_match,

            "work_mode_match": work_mode_match,

            "matched_skills": skill_result["matched_skills"],

            "missing_skills": skill_result["missing_skills"],

            "eligible": eligibility["eligible"],

            "degree_match": eligibility["degree_match"],

            "year_match": eligibility["year_match"],

            "experience_match": eligibility["experience_match"],

            "eligibility_reason": eligibility["eligibility_reason"],

            "recommendation_reason": recommendation_reason

        }

        recommendations.append(result)

    # Rank eligible internships first, then by match score

    recommendations.sort(
        key=lambda item: (
            item["eligible"],
            item["match_percentage"]
        ),
        reverse=True
    )

    return recommendations
