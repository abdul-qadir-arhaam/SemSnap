import json
import os


# ---------------------------------------
# Load Scheme Data
# ---------------------------------------
def load_scheme_data(scheme):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        base_dir,
        "data",
        "schemes",
        f"{scheme}.json"
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Scheme file not found: {file_path}")

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get("subjects", {})
    except json.JSONDecodeError:
        raise Exception("Scheme JSON file is corrupted.")


# ---------------------------------------
# Convert Marks to Grade Points
# ---------------------------------------
def marks_to_grade_point(marks):

    try:
        marks = float(marks)
    except (ValueError, TypeError):
        return 0

    if marks >= 90:
        return 10
    elif marks >= 80:
        return 9
    elif marks >= 70:
        return 8
    elif marks >= 60:
        return 7
    elif marks >= 55:
        return 6
    elif marks >= 50:
        return 5
    elif marks >= 40:
        return 4
    else:
        return 0


# ---------------------------------------
# Reusable GPA Calculator (Core Logic)
# ---------------------------------------
def _calculate_gpa(subjects, credits_map):

    total_credits = 0
    total_weighted_points = 0
    missing_subjects = []

    for subject in subjects:
        code = subject.get("code")
        marks = subject.get("marks")

        if code not in credits_map:
            missing_subjects.append(code)
            continue

        credit = credits_map[code]
        grade_point = marks_to_grade_point(marks)

        total_credits += credit
        total_weighted_points += credit * grade_point

    if total_credits == 0:
        return 0, missing_subjects

    gpa = round(total_weighted_points / total_credits, 2)
    return gpa, missing_subjects


# ---------------------------------------
# SGPA (Semester GPA)
# ---------------------------------------
def calculate_sgpa(subjects, credits_map):
    return _calculate_gpa(subjects, credits_map)


# ---------------------------------------
# Final CGPA (Weighted Across All Semesters)
# ---------------------------------------
def calculate_cgpa(all_subjects, credits_map):
    return _calculate_gpa(all_subjects, credits_map)