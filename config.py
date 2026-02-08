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
    "max_jobs_per_run": 20
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

# Target companies for direct career page scraping
COMPANY_CAREERS = [
    {
        "name": "BMW Group",
        "url": "https://www.bmwgroup.jobs/de/de/jobfinder.html?location=Munich",
        "keywords": ["Project Manager", "Data Analyst", "Business Analyst"]
    },
    {
        "name": "Siemens",
        "url": "https://jobs.siemens.com/careers?location=Munich",
        "keywords": ["IT Project Manager", "Data Analyst", "Project Coordinator"]
    },
    {
        "name": "Allianz",
        "url": "https://careers.allianz.com/en_EN/jobs.html?location=Munich",
        "keywords": ["Project Manager", "Data Analyst", "Business Intelligence"]
    },
    {
        "name": "Munich Re",
        "url": "https://www.munichre.com/en/careers/jobs.html?location=Munich",
        "keywords": ["Data Analyst", "Project Manager", "Analytics"]
    },
    {
        "name": "Infineon Technologies",
        "url": "https://www.infineon.com/cms/en/careers/jobsearch/?location=Munich",
        "keywords": ["Project Manager", "Data Analyst", "IT Manager"]
    },
    {
        "name": "Celonis",
        "url": "https://www.celonis.com/careers/jobs/?location=Munich",
        "keywords": ["Project Manager", "Data Analyst", "Process Mining"]
    },
    {
        "name": "SAP",
        "url": "https://jobs.sap.com/search/?location=Munich",
        "keywords": ["Project Manager", "Data Analyst", "Consultant"]
    },
    {
        "name": "Microsoft",
        "url": "https://careers.microsoft.com/professionals/us/en/search-results?location=Munich",
        "keywords": ["Project Manager", "Data Analyst", "Program Manager"]
    }
]
