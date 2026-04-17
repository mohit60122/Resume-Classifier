"""
FastAPI Backend - API routes for resume screening.
"""
import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from backend.utils.parser import extract_text
from backend.ml.classifier import classifier
from backend.ml.matcher import compute_similarity
from backend.ml.skill_extractor import extract_skills

router = APIRouter(prefix="/api", tags=["Resume Screening"])


def _save_upload(file: UploadFile) -> str:
    """Save uploaded file and return the path."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


def _cleanup_files(paths: list):
    """Remove temporary uploaded files."""
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CV Resume Screener API"}


@router.post("/classify")
async def classify_resumes(files: List[UploadFile] = File(...)):
    """
    Classify uploaded resumes into job categories.

    Accepts multiple PDF/DOCX files.
    Returns predicted category and confidence for each.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    saved_paths = []
    results = []

    try:
        for file in files:
            # Save file
            file_path = _save_upload(file)
            saved_paths.append(file_path)

            # Extract text
            text = extract_text(file_path)
            if not text.strip():
                results.append({
                    "filename": file.filename,
                    "category": "Unable to parse",
                    "confidence": 0.0,
                    "skills": {"technical": [], "soft_skills": [], "certifications": [], "total_count": 0}
                })
                continue

            # Classify
            prediction = classifier.predict_category(text)

            # Extract skills
            skills = extract_skills(text)

            results.append({
                "filename": file.filename,
                "category": prediction["category"],
                "confidence": prediction["confidence"],
                "skills": skills
            })

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        _cleanup_files(saved_paths)

    return {"results": results, "total": len(results)}


@router.post("/match")
async def match_resumes(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Match resumes against a job description.

    Accepts JD text and multiple resume files.
    Returns ranked list with match scores.
    """
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")

    if not files:
        raise HTTPException(status_code=400, detail="No resume files uploaded")

    saved_paths = []
    resume_texts = []
    filenames = []

    try:
        for file in files:
            file_path = _save_upload(file)
            saved_paths.append(file_path)

            text = extract_text(file_path)
            if text.strip():
                resume_texts.append(text)
                filenames.append(file.filename)

        if not resume_texts:
            raise HTTPException(status_code=400, detail="Could not extract text from any resume")

        # Compute similarity scores
        results = compute_similarity(job_description, resume_texts, filenames)

        # Also classify each resume and extract skills
        for result in results:
            idx = filenames.index(result["filename"])
            text = resume_texts[idx]

            prediction = classifier.predict_category(text)
            skills = extract_skills(text)

            result["category"] = prediction["category"]
            result["confidence"] = prediction["confidence"]
            result["skills"] = skills

    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        _cleanup_files(saved_paths)

    return {
        "job_description_preview": job_description[:200] + "..." if len(job_description) > 200 else job_description,
        "results": results,
        "total": len(results)
    }


@router.post("/extract-skills")
async def extract_skills_endpoint(file: UploadFile = File(...)):
    """
    Extract skills from a single resume.
    """
    saved_paths = []

    try:
        file_path = _save_upload(file)
        saved_paths.append(file_path)

        text = extract_text(file_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file")

        skills = extract_skills(text)

        # Also classify
        prediction = classifier.predict_category(text)

        return {
            "filename": file.filename,
            "category": prediction["category"],
            "confidence": prediction["confidence"],
            "skills": skills
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        _cleanup_files(saved_paths)
