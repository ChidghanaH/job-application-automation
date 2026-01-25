"""Configuration file for job application automation"""
import os
from dotenv import load_dotenv

load_dotenv()

# Target job criteria for Munich market
JOB_CRITERIA = {
    "locations": ["Munich", "München", "Bavaria", "Bayern", "Germany", "Remote"],
    "job_titles": [
        "Junior IT Project Manager",
        "IT Project Manager",
        "Junior Project Manager",
        "Data Analyst",
        "Junior Data Analyst",
        "Business Analyst",
        "Project Coordinator"
    ],
    "keywords": [
        "python", "sql", "data analysis", "etl", "project management",
        "agile", "scrum", "stakeholder", "waterfall", "confluence",
        "jira", "powerbi", "tableau", "excel"
    ],
    "exclude_keywords": ["senior", "lead", "principal", "director", "head of"],
    "min_match_score": 0.75,  # 75% match threshold
    "max_jobs_per_run": 50
}

# API Keys (from environment variables)
API_KEYS = {
    "linkedin_email": os.getenv("LINKEDIN_EMAIL"),
    "linkedin_password": os.getenv("LINKEDIN_PASSWORD"),
    "gmail_api_key": os.getenv("GMAIL_API_KEY"),
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "indeed_api_key": os.getenv("INDEED_API_KEY")
}

# Application settings
APP_CONFIG = {
    "application_delay": 2,  # seconds between applications
    "max_applications_per_day": 50,
    "auto_submit": False,
    "generate_cover_letter": True,
    "track_applications": True
}
