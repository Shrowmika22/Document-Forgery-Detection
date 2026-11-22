from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import uuid

from utils.analyzer import analyze_document


app = Flask(__name__)

app.secret_key = "document-forgery-detection-secret-key"


# ==========================================
# FOLDERS
# ==========================================

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

# Maximum upload size = 20 MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# ==========================================
# ALLOWED FILE TYPES
# ==========================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg"
}


# ==========================================
# CREATE FOLDERS
# ==========================================

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# ==========================================
# CHECK FILE EXTENSION
# ==========================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# UPLOAD + ANALYSIS
# ==========================================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    # If user only opens upload page
    if request.method == "GET":

        return render_template("upload.html")


    # --------------------------------------
    # Check file
    # --------------------------------------

    if "document" not in request.files:

        flash("Please select a document.")

        return redirect(url_for("upload"))


    file = request.files["document"]


    # --------------------------------------
    # Empty file name
    # --------------------------------------

    if file.filename == "":

        flash("Please select a document.")

        return redirect(url_for("upload"))


    # --------------------------------------
    # Check file type
    # --------------------------------------

    if not allowed_file(file.filename):

        flash(
            "Only PDF, JPG, JPEG and PNG files are allowed."
        )

        return redirect(url_for("upload"))


    # --------------------------------------
    # Secure original filename
    # --------------------------------------

    original_filename = secure_filename(
        file.filename
    )


    # --------------------------------------
    # Get extension
    # --------------------------------------

    extension = original_filename.rsplit(
        ".",
        1
    )[1].lower()


    # --------------------------------------
    # Create unique filename
    # --------------------------------------

    unique_filename = (
        f"{uuid.uuid4().hex}.{extension}"
    )


    # --------------------------------------
    # Create complete file path
    # --------------------------------------

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )


    # --------------------------------------
    # Save uploaded file
    # --------------------------------------

    file.save(filepath)


    # ======================================
    # AI DOCUMENT ANALYSIS
    # ======================================

    try:

        result = analyze_document(
            filepath,
            app.config["PROCESSED_FOLDER"]
        )


    except Exception as e:

        result = {

            "label": "ANALYSIS ERROR",

            "confidence": 0,

            "score": 0,

            "reasons": [
                f"Document analysis could not be completed: {str(e)}"
            ]

        }


    # ======================================
    # SHOW RESULT PAGE
    # ======================================

    return render_template(

        "result.html",

        filename=original_filename,

        uploaded_file=unique_filename,

        result=result

    )


# ==========================================
# FILE TOO LARGE
# ==========================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "File is too large. Maximum allowed size is 20 MB."
    )

    return redirect(url_for("upload"))


# ==========================================
# START FLASK
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)