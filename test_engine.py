
from modules.recommendation_engine import calculate_match

# TEST 1: ML and Machine Learning

student_skills = ["Python", "ML", "SQL"]
required_skills = ["Python", "Machine Learning", "SQL"]

result = calculate_match(student_skills, required_skills)

print("TEST 1: ML Matching")
print("Match:", result["match_percentage"], "%")
print("Matched Skills:", result["matched_skills"])
print("Missing Skills:", result["missing_skills"])

print("-------------------------")

# TEST 2: NLP and Natural Language Processing

student_skills = ["Python", "NLP"]
required_skills = ["Python", "Natural Language Processing"]

result = calculate_match(student_skills, required_skills)

print("TEST 2: NLP Matching")
print("Match:", result["match_percentage"], "%")
print("Matched Skills:", result["matched_skills"])
print("Missing Skills:", result["missing_skills"])
