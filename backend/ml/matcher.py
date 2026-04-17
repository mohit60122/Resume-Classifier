"""
Resume Matcher - Match resumes against a Job Description using cosine similarity.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.ml.preprocessor import preprocess


def compute_similarity(job_description: str, resume_texts: list, filenames: list = None) -> list:
    """
    Compute cosine similarity between a job description and multiple resumes.

    Args:
        job_description: The job description text
        resume_texts: List of resume text strings
        filenames: Optional list of filenames corresponding to resumes

    Returns:
        List of dicts sorted by match_score (descending):
        [{"filename": str, "match_score": float, "rank": int}, ...]
    """
    if not job_description or not resume_texts:
        return []

    # Preprocess all texts
    processed_jd = preprocess(job_description)
    processed_resumes = [preprocess(text) for text in resume_texts]

    # Filter out empty resumes
    valid_indices = [i for i, text in enumerate(processed_resumes) if text.strip()]
    if not valid_indices:
        return []

    valid_resumes = [processed_resumes[i] for i in valid_indices]
    valid_filenames = [filenames[i] if filenames else f"Resume_{i+1}" for i in valid_indices]

    # Combine JD + resumes into one corpus for TF-IDF
    corpus = [processed_jd] + valid_resumes

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words='english',
        sublinear_tf=True
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Cosine similarity: JD vector vs all resume vectors
    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(jd_vector, resume_vectors)[0]

    # Build results
    results = []
    for i, score in enumerate(similarities):
        results.append({
            "filename": valid_filenames[i],
            "match_score": round(float(score) * 100, 1)
        })

    # Sort by match score (descending) and assign ranks
    results.sort(key=lambda x: x["match_score"], reverse=True)
    for rank, result in enumerate(results, 1):
        result["rank"] = rank

    return results
