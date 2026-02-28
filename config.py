import os
import pytesseract

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

# Correct Tesseract path
