from flask import Flask, render_template, request, redirect
import os
import hashlib

from parser import get_text_from_file, extract_subjects_and_marks
from cgpa_utils import load_scheme_data, calculate_sgpa, calculate_cgpa
from config import UPLOAD_FOLDER

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------------------------------
# 1️⃣ Index Page
# ---------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        scheme = request.form["scheme"]
        sem_count = request.form["sem_count"]
        return redirect(f"/upload?scheme={scheme}&sem_count={sem_count}")

    return render_template("index.html")


# ---------------------------------------
# 2️⃣ Upload Page
# ---------------------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():

    scheme = request.args.get("scheme")
    sem_count = int(request.args.get("sem_count"))

    if request.method == "POST":

        # Safe scheme loading
        try:
            credits_map = load_scheme_data(scheme)
        except Exception:
            return render_template(
                "upload.html",
                scheme=scheme,
                sem_count=sem_count,
                error="Scheme data missing or corrupted."
            )

        semester_data = {}       # Store subjects per semester
        all_subjects = []        # For final CGPA
        seen_subjects = set()
        seen_file_hashes = set()

        # Loop through selected semesters
        for i in range(1, sem_count + 1):
            file = request.files.get(f"sem{i}")

            if not file or file.filename == "":
                return render_template(
                    "upload.html",
                    scheme=scheme,
                    sem_count=sem_count,
                    error=f"Semester {i} PDF not uploaded."
                )

            # -------- File Hash Validation --------
            file_bytes = file.read()
            file_hash = hashlib.sha256(file_bytes).hexdigest()

            if file_hash in seen_file_hashes:
                return render_template(
                    "upload.html",
                    scheme=scheme,
                    sem_count=sem_count,
                    error="Duplicate semester PDF detected."
                )

            seen_file_hashes.add(file_hash)
            file.seek(0)

            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

            # -------- Extract Subjects --------
            try:
                text = get_text_from_file(file_path)
                subjects = extract_subjects_and_marks(text)
            except Exception:
                return render_template(
                    "upload.html",
                    scheme=scheme,
                    sem_count=sem_count,
                    error=f"Invalid or corrupted PDF for Semester {i}."
                )

            if not subjects:
                return render_template(
                    "upload.html",
                    scheme=scheme,
                    sem_count=sem_count,
                    error=f"No valid subjects found in Semester {i}."
                )

            filtered_subjects = []

            # Prevent duplicate subject codes
            for subject in subjects:
                code = subject.get("code")

                if code in seen_subjects:
                    continue

                seen_subjects.add(code)
                filtered_subjects.append(subject)
                all_subjects.append(subject)

            semester_data[i] = filtered_subjects

        if not all_subjects:
            return render_template(
                "upload.html",
                scheme=scheme,
                sem_count=sem_count,
                error="No valid subjects detected."
            )

        # -------- Calculate SGPA per Semester --------
        semester_sgpas = {}
        semester_missing = {}

        for sem, subjects in semester_data.items():
            sgpa, missing = calculate_sgpa(subjects, credits_map)
            semester_sgpas[sem] = sgpa
            semester_missing[sem] = missing

        # -------- Final Weighted CGPA --------
        cgpa, total_missing = calculate_cgpa(all_subjects, credits_map)

        return render_template(
            "result.html",
            semester_sgpas=semester_sgpas,
            semester_missing=semester_missing,
            cgpa=cgpa,
            total_missing=total_missing
        )

    return render_template("upload.html", scheme=scheme, sem_count=sem_count)


if __name__ == "__main__":
    app.run(debug=True)