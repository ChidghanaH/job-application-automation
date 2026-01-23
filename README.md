# 🤖 Job Application Automation Workflow

Automated job search & application workflow for **Munich-based Junior PM & Data Analyst roles**. Fetches jobs from APIs, generates tailored resumes/cover letters via AI, and tracks applications in Google Sheets. Runs daily via GitHub Actions.

## ✨ Features

- **🔍 Automated Job Scraping**: Uses Apify actors to scrape LinkedIn, Indeed, StepStone for Munich IT jobs
- **🎯 Smart Filtering**: Ranks jobs by match score (keywords, location, role type)
- **✍️ AI Resume Tailoring**: Generates custom resume & cover letter per job using OpenAI GPT-4
- **📊 Application Tracking**: Auto-updates Google Sheets with job details, match scores, and links
- **⏰ Daily Automation**: GitHub Actions runs every morning at 7 AM CET
- **📦 Artifact Storage**: Saves generated resumes as downloadable artifacts

## 🏗️ Architecture

```
GitHub Actions (daily 7 AM)
  ↓
fetch_jobs.py → Apify LinkedIn/Indeed scrapers
  ↓
rank_jobs.py → Filter by location/keywords/score
  ↓
generate_docs.py → OpenAI GPT-4 tailors CV/cover letter
  ↓
update_sheet.py → Google Sheets tracking
  ↓
Artifacts → Download tailored resumes
```

## 🚀 Setup

### 1. Fork & Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/job-application-automation.git
cd job-application-automation
```

### 2. Create `.env` File (Local Testing)
```bash
APIFY_API_KEY=your_apify_key
OPENAI_API_KEY=your_openai_key
GOOGLE_SHEETS_CREDENTIALS='{...}'  # Service account JSON
SHEET_ID=your_google_sheet_id
```

### 3. Add GitHub Secrets
Go to **Settings → Secrets → Actions** and add:
- `APIFY_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_SHEETS_CREDENTIALS`
- `SHEET_ID`

### 4. Edit `config.py`
Customize job criteria:
```python
JOB_CRITERIA = {
    "locations": ["Munich", "München", "Bavaria"],
    "job_titles": ["Junior IT Project Manager", "Data Analyst"],
    "keywords": ["python", "sql", "agile", "scrum"],
    "min_match_score": 0.75
}
```

## 📝 Implementation Guide

### Create Missing Scripts

You need to implement these Python scripts in a `scripts/` folder:

#### `scripts/fetch_jobs.py`
- Use Apify's LinkedIn/Indeed actors
- Query jobs matching Munich + role keywords
- Save to `data/raw_jobs.json`

#### `scripts/rank_jobs.py`
- Load `data/raw_jobs.json`
- Calculate match score based on keywords
- Filter by `min_match_score`
- Save top 50 to `data/ranked_jobs.json`

#### `scripts/generate_docs.py`
- Load `data/ranked_jobs.json`
- For each job, call OpenAI API with:
  - Base resume template
  - Job description
  - Prompt: "Tailor this resume for this role"
- Save PDFs to `output/resumes/`

#### `scripts/update_sheet.py`
- Load `data/ranked_jobs.json`
- Use gspread library
- Append rows: [Date, Company, Role, Location, Match Score, Link, Status]

## 🎯 Usage

### Manual Run (Local)
```bash
pip install -r requirements.txt
python scripts/fetch_jobs.py
python scripts/rank_jobs.py
python scripts/generate_docs.py
python scripts/update_sheet.py
```

### Automated (GitHub Actions)
- Workflow runs **daily at 7 AM CET**
- Or trigger manually: **Actions → Job Search Automation → Run workflow**
- Download resumes from **Artifacts**

## 📊 Google Sheets Setup

1. Create a Google Sheet with columns:
   `Date | Company | Role | Location | Match Score | Link | Status | Notes`
2. Share with service account email from credentials JSON
3. Copy Sheet ID from URL and add to secrets

## ⚠️ Important Notes

### Legal & Ethical
- **Do NOT auto-click "Apply"** - violates LinkedIn/Indeed TOS
- This tool **finds & prepares** - YOU manually apply
- Review each tailored resume before submitting
- Respect rate limits on job boards

### Cost Estimates
- Apify: ~$5/month for 50 jobs/day
- OpenAI GPT-4: ~$10/month for resume generation
- GitHub Actions: Free (within limits)

## 🛠️ Customization

### Change Schedule
Edit `.github/workflows/job-automation.yml`:
```yaml
schedule:
  - cron: '0 7 * * *'  # Change time here (UTC)
```

### Add More Job Boards
Extend `fetch_jobs.py` to scrape StepStone, XING, or use n8n webhooks.

## 📚 Resources

- [Apify Actors for Job Scraping](https://apify.com/store)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [gspread Python Library](https://docs.gspread.org/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## 🤝 Contributing

PRs welcome! Focus areas:
- Additional job board scrapers
- Better match scoring algorithms
- Cover letter templates
- n8n workflow examples

## 📄 License

MIT License - Use freely, but please star ⭐ if helpful!

---

**Made for junior devs/analysts job hunting in Munich** 🇩🇪
