"""
Flask Frontend - Dashboard Application
=======================================
CV/Resume Screener Dashboard

Run with:
    python -m frontend.app
"""
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from frontend.config import API_BASE_URL, SECRET_KEY, UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def call_api(endpoint, files=None, data=None):
    """
    Call the FastAPI backend.
    Returns (response_json, error_message)
    """
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if files and data:
            resp = requests.post(url, files=files, data=data, timeout=120)
        elif files:
            resp = requests.post(url, files=files, timeout=120)
        else:
            resp = requests.get(url, timeout=30)

        if resp.status_code == 200:
            return resp.json(), None
        else:
            error = resp.json().get("detail", "Unknown error")
            return None, f"API Error ({resp.status_code}): {error}"

    except requests.ConnectionError:
        return None, "Cannot connect to backend API. Make sure FastAPI is running on port 8000."
    except requests.Timeout:
        return None, "Request timed out. The file may be too large."
    except Exception as e:
        return None, f"Error: {str(e)}"


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Dashboard home page."""
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload resumes for classification."""
    if request.method == "POST":
        files = request.files.getlist("resumes")

        if not files or all(f.filename == '' for f in files):
            flash("Please select at least one file.", "error")
            return redirect(url_for("upload"))

        # Validate files
        valid_files = []
        for f in files:
            if f.filename and allowed_file(f.filename):
                valid_files.append(f)
            elif f.filename:
                flash(f"Skipped '{f.filename}' — unsupported format.", "warning")

        if not valid_files:
            flash("No valid files to process. Upload PDF or DOCX files.", "error")
            return redirect(url_for("upload"))

        # Prepare files for API call
        file_tuples = []
        for f in valid_files:
            file_tuples.append(("files", (f.filename, f.stream, f.content_type)))

        # Call FastAPI classify endpoint
        result, error = call_api("/api/classify", files=file_tuples)

        if error:
            flash(error, "error")
            return redirect(url_for("upload"))

        # Store results in session
        session["classify_results"] = result
        return redirect(url_for("results"))

    return render_template("upload.html")


@app.route("/results")
def results():
    """Display classification results."""
    data = session.get("classify_results")
    if not data:
        flash("No results to display. Please upload resumes first.", "info")
        return redirect(url_for("upload"))
    return render_template("results.html", data=data)


@app.route("/match", methods=["GET", "POST"])
def match():
    """Match resumes against a job description."""
    if request.method == "POST":
        job_description = request.form.get("job_description", "").strip()
        files = request.files.getlist("resumes")

        if not job_description:
            flash("Please enter a job description.", "error")
            return redirect(url_for("match"))

        if not files or all(f.filename == '' for f in files):
            flash("Please upload at least one resume.", "error")
            return redirect(url_for("match"))

        # Validate files
        valid_files = []
        for f in files:
            if f.filename and allowed_file(f.filename):
                valid_files.append(f)

        if not valid_files:
            flash("No valid files. Upload PDF or DOCX files.", "error")
            return redirect(url_for("match"))

        # Prepare for API
        file_tuples = []
        for f in valid_files:
            file_tuples.append(("files", (f.filename, f.stream, f.content_type)))

        form_data = {"job_description": job_description}

        # Call FastAPI match endpoint
        result, error = call_api("/api/match", files=file_tuples, data=form_data)

        if error:
            flash(error, "error")
            return redirect(url_for("match"))

        session["match_results"] = result
        session["job_description"] = job_description
        return render_template("match.html", data=result, job_description=job_description, show_results=True)

    return render_template("match.html", data=None, show_results=False)


# ─── Error Handlers ───────────────────────────────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    flash("File too large. Maximum size is 10 MB.", "error")
    return redirect(url_for("upload"))


@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


# ─── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
