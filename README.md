# Job Application Automation Workflow

This is an automated job search and application workflow I built to help with my job hunt in Munich. It's designed specifically for Junior PM and Data Analyst roles. The system fetches jobs from various sources, generates tailored resumes and cover letters using AI, and tracks everything in Google Sheets. It runs automatically every day via GitHub Actions.

## What It Does

- **Automated Job Scraping**: Searches LinkedIn, Indeed, and StepStone for relevant IT jobs in Munich using Apify
- **Smart Filtering**: Ranks each job based on how well it matches my skills, preferred location, and role type
- **AI Resume Tailoring**: Uses OpenAI GPT-4 to customize my resume and cover letter for each specific job
- **Application Tracking**: Automatically logs job details, match scores, and application links in Google Sheets
- **Daily Automation**: Runs automatically every morning at 7 AM CET
- **Resume Storage**: Saves all generated resumes as downloadable artifacts

## How It Works

The workflow follows this process:

```
GitHub Actions (runs daily at 7 AM)
  ↓
fetch_jobs.py → Scrapes jobs from LinkedIn and Indeed via Apify
  ↓
rank_jobs.py → Filters by location, keywords, and calculates match score
  ↓
generate_docs.py → Uses OpenAI GPT-4 to tailor my CV and cover letter
  ↓
update_sheet.py → Updates Google Sheets with tracking info
  ↓
Artifacts → Downloads the tailored resumes
```

## Getting Started

### 1. Fork and Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/job-application-automation.git
cd job-application-automation
```

### 2. Set Up Local Environment

Create a `.env` file for local testing:

```bash
APIFY_API_KEY=your_apify_key
OPENAI_API_KEY=your_openai_key
GOOGLE_SHEETS_CREDENTIALS='{...}' # Your service account JSON
SHEET_ID=your_google_sheet_id
```

### 3. Configure GitHub Secrets

Go to your repository's **Settings → Secrets → Actions** and add these secrets:

- `APIFY_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_SHEETS_CREDENTIALS`
- `SHEET_ID`

### 4. Customize Job Criteria

Edit `config.py` to match your preferences:

```python
JOB_CRITERIA = {
    "locations": ["Munich", "München", "Bavaria"],
    "job_titles": ["Junior IT Project Manager", "Data Analyst"],
    "keywords": ["python", "sql", "agile", "scrum"],
    "min_match_score": 0.75
}
```

## Implementation Details

The project uses several Python scripts in the `scripts/` folder:

### scripts/fetch_jobs.py

This script connects to Apify's LinkedIn and Indeed scrapers, searches for jobs matching my criteria in Munich, and saves the raw results to `data/raw_jobs.json`.

### scripts/rank_jobs.py

Loads the raw jobs, calculates a match score for each one based on keywords and requirements, filters out anything below my minimum threshold, and saves the top candidates to `data/ranked_jobs.json`.

### scripts/generate_docs.py

Takes the ranked jobs and uses OpenAI's GPT-4 API to generate customized versions of my resume and cover letter for each position. The prompts include both my base resume template and the specific job description. Results are saved as PDFs in `output/resumes/`.

### scripts/update_sheet.py

Connects to Google Sheets using the gspread library and adds new rows for each job with details like date, company, role, location, match score, link, and application status.

## Running the System

### Manual Execution

You can run it manually on your local machine:

```bash
pip install -r requirements.txt
python scripts/fetch_jobs.py
python scripts/rank_jobs.py
python scripts/generate_docs.py
python scripts/update_sheet.py
```

### Automatic Daily Runs

The GitHub Actions workflow automatically runs every day at 7 AM CET. You can also trigger it manually:

1. Go to the **Actions** tab in your repository
2. Select **Job Search Automation**
3. Click **Run workflow**
4. Download generated resumes from the **Artifacts** section

## Setting Up Google Sheets

1. Create a new Google Sheet with these columns:
   - Date | Company | Role | Location | Match Score | Link | Status | Notes
2. Share the sheet with your service account email (found in your credentials JSON)
3. Copy the Sheet ID from the URL and add it to your GitHub secrets

## Important Considerations

### Legal and Ethical Usage

Please note that this tool is designed to assist with job searching, not to spam applications:

- Never use it to automatically click "Apply" buttons - that violates LinkedIn and Indeed terms of service
- This system finds opportunities and prepares materials - you still need to manually review and apply
- Always review the tailored resumes before submitting to ensure quality
- Be respectful of rate limits on job boards

### Cost Considerations

Running this system does have some costs:

- Apify: Approximately $5 per month for scraping 50 jobs daily
- OpenAI GPT-4: Around $10 per month for resume generation
- GitHub Actions: Free within GitHub's standard limits

## Customization Options

### Changing the Schedule

Edit `.github/workflows/job-automation.yml` to adjust when it runs:

```yaml
schedule:
  - cron: '0 7 * * *'  # Adjust this time (uses UTC)
```

### Adding More Job Boards

You can extend `fetch_jobs.py` to include other sources like StepStone or XING, or integrate with n8n webhooks.

## Helpful Resources

- [Apify Job Scraping Actors](https://apify.com/store)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [gspread Python Library](https://docs.gspread.org/)
- [GitHub Actions Secrets Guide](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## Contributing

If you find this useful and want to contribute, pull requests are welcome! Areas that could use improvement:

- Support for additional job boards
- Better scoring algorithms
- Cover letter template variations
- n8n workflow examples

## License

MIT License - Feel free to use this for your own job search. If it helps you land a job, I'd love to hear about it!

---

Built by someone who got tired of manually searching job boards every day. I hope it helps you too!
