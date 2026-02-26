import fitz
import pytesseract
import cv2
import os
import re


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    return full_text


def extract_text_using_ocr_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        pix = page.get_pixmap()
        img_path = "temp_page.png"
        pix.save(img_path)

        img = cv2.imread(img_path)
        text = pytesseract.image_to_string(img)
        full_text += text

        os.remove(img_path)

    return full_text


def extract_text_from_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Invalid image path.")

    # 1️⃣ Resize (optional but helpful)
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # 2️⃣ Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3️⃣ Noise removal
    gray = cv2.medianBlur(gray, 3)

    # 4️⃣ Adaptive threshold (better than normal threshold)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    # 5️⃣ Optional: Morphological opening (removes small noise)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    text = pytesseract.image_to_string(processed)

    return text


def get_text_from_file(file_path):

    if file_path.lower().endswith(".pdf"):

        text = extract_text_from_pdf(file_path)

        # If digital extraction fails → fallback to OCR
        if len(text.strip()) < 50:
            text = extract_text_using_ocr_from_pdf(file_path)

    else:
        text = extract_text_from_image(file_path)

    return text


def extract_subjects_and_marks(text):

    subjects = []

    """
    Pattern explanation:
    - Subject code must:
        Start with B
        Have 2–4 uppercase letters
        Have exactly 3 continuous digits
        Optional ending letter
    - Then capture 3 numbers (IA, External, Total)
    - End with P or F
    """

    pattern = r'\b(B[A-Z]{2,4}\d{3}[A-Z]?)\b.*?(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})\s+[PF]'

    matches = re.findall(pattern, text, re.DOTALL)

    for match in matches:
        subjects.append({
            "code": match[0],      # Subject Code
            "marks": int(match[3]) # Total Marks (3rd captured number)
        })

    return subjects