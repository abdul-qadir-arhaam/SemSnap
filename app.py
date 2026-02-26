from flask import Flask, render_template, request, redirect
import os

from parser import get_text_from_file, extract_subjects_and_marks
from cgpa_utils import load_scheme_data, calculate_cgpa
from config import UPLOAD_FOLDER

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------------------------------
# 1️⃣ Index Page (Scheme + Sem Count)
# ---------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        scheme = request.form["scheme"]
        sem_count = request.form["sem_count"]

        return redirect(f"/upload?scheme={scheme}&sem_count={sem_count}")

    return render_template("index.html")


# ---------------------------------------
# 2️⃣ Upload Page (Dynamic Semester Upload)
# ---------------------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():

    scheme = request.args.get("scheme")
    sem_count = int(request.args.get("sem_count"))

    if request.method == "POST":

        # 🔴 Safe scheme loading
        try:
            credits_map = load_scheme_data(scheme)
        except Exception:
            return "Error: Scheme data missing or corrupted."

        all_subjects = []
        seen_subjects = set()

        # Loop through selected semesters
        for i in range(1, sem_count + 1):
            file = request.files.get(f"sem{i}")

            # 🔴 Error 1: File not uploaded
            if not file or file.filename == "":
                return f"Error: Semester {i} PDF not uploaded."

            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

            # 🔴 Error 3: Corrupted / invalid PDF
            try:
                text = get_text_from_file(file_path)
                subjects = extract_subjects_and_marks(text)
            except Exception:
                return f"Error: Invalid or corrupted PDF for Semester {i}."

            # 🔴 Error 4: Duplicate subject prevention
            for subject in subjects:
                code = subject.get("code")

                if code in seen_subjects:
                    continue

                seen_subjects.add(code)
                all_subjects.append(subject)

        # 🔴 No valid subjects extracted
        if not all_subjects:
            return "Error: No valid subjects detected in uploaded PDFs."

        # Calculate CGPA (expects missing_subjects return)
        cgpa, missing_subjects = calculate_cgpa(all_subjects, credits_map)

        return render_template(
            "result.html",
            cgpa=cgpa,
            missing_subjects=missing_subjects
        )

    return render_template("upload.html", scheme=scheme, sem_count=sem_count)


# ---------------------------------------
if __name__ == "__main__":
    app.run(debug=True)