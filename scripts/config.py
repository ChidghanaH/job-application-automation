"""Configuration for job search automation"""

# Job search criteria
JOB_CRITERIA = {
    'job_titles': [
        'Project Manager',
        'Junior Project Manager',
        'Project Coordinator',
        'PMO Analyst',
        'Data Analyst',
        'Junior Data Analyst',
        'Business Analyst',
        'Market Intelligence Analyst'
    ],
    'keywords': [
        'project management',
        'data analysis',
        'analytics',
        'business intelligence',
        'PMO',
        'agile',
        'scrum',
        'SQL',
        'Python',
        'Power BI',
        'Excel',
        'market research'
    ],
    'location': 'Munich, Germany',
    'experience_level': ['entry', 'junior', '0-2 years']
}

# Company career pages to scrape
COMPANY_CAREERS = [
    {
        'name': 'BMW Group',
        'url': 'https://www.bmwgroup.jobs/de/de/opportunities.html',
        'keywords': ['project', 'data', 'analyst']
    },
    {
        'name': 'Siemens',
        'url': 'https://jobs.siemens.com/careers',
        'keywords': ['project', 'data', 'analyst', 'PMO']
    },
    {
        'name': 'Allianz',
        'url': 'https://careers.allianz.com/en/jobs',
        'keywords': ['project', 'data', 'analyst']
    },
    {
        'name': 'Munich RE',
        'url': 'https://www.munichre.com/en/careers/job-search.html',
        'keywords': ['project', 'data', 'analyst']
    },
    {
        'name': 'SAP',
        'url': 'https://jobs.sap.com/',
        'keywords': ['project', 'data', 'analyst']
    }
]
