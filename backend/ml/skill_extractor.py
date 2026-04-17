"""
Skill Extractor - Extract technical and soft skills from resume text.
Uses dictionary-based matching against a curated skills taxonomy.
"""
import re


# ─── Skills Taxonomy ───────────────────────────────────────────────────────────

TECHNICAL_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php",
    "swift", "kotlin", "go", "rust", "scala", "r", "matlab", "perl", "dart",
    "objective-c", "lua", "haskell", "sql", "html", "css",

    # Web Frameworks
    "react", "angular", "vue", "django", "flask", "fastapi", "express",
    "spring", "spring boot", "node.js", "next.js", "nuxt.js", "svelte",
    "ruby on rails", "laravel", "asp.net", "blazor",

    # Data Science / ML
    "machine learning", "deep learning", "neural network", "tensorflow",
    "pytorch", "keras", "scikit-learn", "pandas", "numpy", "scipy",
    "matplotlib", "seaborn", "nltk", "spacy", "opencv", "hugging face",
    "transformers", "bert", "gpt", "llm", "natural language processing",
    "computer vision", "data mining", "data analysis", "statistics",
    "regression", "classification", "clustering", "random forest",
    "xgboost", "lightgbm", "feature engineering",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "terraform", "ansible", "jenkins", "ci/cd", "github actions",
    "circleci", "travis ci", "nginx", "apache", "linux", "unix",
    "bash", "shell scripting", "microservices",

    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "sqlite", "oracle", "sql server",
    "firebase", "neo4j", "graphql",

    # Tools & Platforms
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "slack", "figma", "postman", "swagger", "vs code", "intellij",
    "jupyter", "tableau", "power bi", "excel", "spark", "hadoop",
    "kafka", "rabbitmq", "airflow",

    # Mobile
    "android", "ios", "react native", "flutter", "xamarin",

    # Other Technical
    "rest api", "api", "websocket", "grpc", "oauth", "jwt",
    "agile", "scrum", "devops", "testing", "unit testing",
    "selenium", "cypress", "automation", "blockchain", "iot",
    "embedded systems", "fpga", "verilog",
}

SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "time management", "project management",
    "adaptability", "creativity", "collaboration", "mentoring",
    "decision making", "strategic planning", "negotiation",
    "conflict resolution", "presentation", "public speaking",
    "analytical thinking", "attention to detail", "work ethic",
    "self motivated", "interpersonal skills", "multitasking",
    "stakeholder management", "client relations", "customer service",
}

CERTIFICATIONS = {
    "aws certified", "azure certified", "google certified",
    "pmp", "scrum master", "cissp", "ceh", "comptia",
    "cisco certified", "ccna", "ccnp", "rhce",
    "itil", "six sigma", "togaf", "cfa", "cpa",
    "data engineer", "solutions architect", "machine learning specialty",
}


def extract_skills(text: str) -> dict:
    """
    Extract skills from resume text using dictionary matching.

    Args:
        text: Raw or cleaned resume text

    Returns:
        dict with keys: 'technical', 'soft_skills', 'certifications', 'total_count'
    """
    if not text:
        return {"technical": [], "soft_skills": [], "certifications": [], "total_count": 0}

    text_lower = text.lower()

    # Remove special chars for better matching but keep spaces
    text_clean = re.sub(r'[^a-zA-Z0-9\s\+\#\./]', ' ', text_lower)
    text_clean = re.sub(r'\s+', ' ', text_clean)

    # Match technical skills
    found_technical = []
    for skill in TECHNICAL_SKILLS:
        # Use word boundary matching for short skills to avoid false positives
        if len(skill) <= 2:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_clean):
                found_technical.append(skill.upper() if len(skill) <= 3 else skill.title())
        else:
            if skill in text_clean:
                found_technical.append(skill.title())

    # Match soft skills
    found_soft = []
    for skill in SOFT_SKILLS:
        if skill in text_clean:
            found_soft.append(skill.title())

    # Match certifications
    found_certs = []
    for cert in CERTIFICATIONS:
        if cert in text_clean:
            found_certs.append(cert.title())

    # Deduplicate and sort
    found_technical = sorted(set(found_technical))
    found_soft = sorted(set(found_soft))
    found_certs = sorted(set(found_certs))

    return {
        "technical": found_technical,
        "soft_skills": found_soft,
        "certifications": found_certs,
        "total_count": len(found_technical) + len(found_soft) + len(found_certs)
    }
