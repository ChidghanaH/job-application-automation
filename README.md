# Job Application Automation Workflow

This is an automated job application workflow I built to help with my job hunt in Munich. It's designed specifically for Junior PM and Data Analyst roles. The system reads job listings from Google Sheets, generates tailored resumes and cover letters using AI, and tracks everything automatically. It runs every day via GitHub Actions.

## What It Does

- **Job Management**: Reads job listings from Google Sheets where you can manually add positions you're interested in
- **AI Resume Tailoring**: Uses OpenAI GPT-4 to customize resumes and cover letters for each specific job
- **Application Tracking**: Automatically logs job details and status in Google Sheets
- **Daily Automation**: Runs automatically every morning at 7 AM CET
- **Resume Storage**: Saves all generated resumes as downloadable artifacts

## How It Works

The workflow follows this simple process:

```
GitHub Actions (runs daily at 7 AM)
  ↓
process_applications.py → Reads jobs from Google Sheets
  ↓
  → Uses OpenAI GPT-4 to tailor CV and cover letter for each job
  ↓
  → Saves documents to output/resumes/ folder
  ↓
  → Updates Google Sheets with processing status
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
OPENAI_API_KEY=your_openai_key
GOOGLE_SHEETS_CREDENTIALS='{...}' # Your service account JSON
SHEET_ID=your_google_sheet_id
```

### 3. Configure GitHub Secrets

Go to your repository's **Settings → Secrets → Actions** and add these secrets:

- `OPENAI_API_KEY`
- `GOOGLE_SHEETS_CREDENTIALS`
- `SHEET_ID`

### 4. Set Up Your Google Sheet

Create a Google Sheet with a worksheet named "Jobs" containing these columns:

- Title: Job title
- Company: Company name
- Location: Job location
- Description: Job description
- Status: Set to "New" for jobs to process
- URL: Application link (optional)

### 5. Get API Keys

**OpenAI API**: Sign up at https://platform.openai.com and create an API key

**Google Sheets**: 
1. Go to Google Cloud Console
2. Create a new project
3. Enable Google Sheets API
4. Create a service account and download JSON credentials
5. Share your Google Sheet with the service account email

### 6. Run Locally (Optional)

```bash
pip install -r requirements.txt
python scripts/process_applications.py
```

### 7. Let GitHub Actions Do Its Thing

Once you've set up your secrets, the workflow will run automatically every day at 7 AM CET. You can also trigger it manually from the Actions tab.

## Project Structure

```
.
├── .github/workflows/
│   └── job-automation.yml    # GitHub Actions workflow
├── scripts/
│   └── process_applications.py  # Main automation script
├── output/
│   └── resumes/              # Generated resumes and cover letters
├── requirements.txt          # Python dependencies
└── README.md
```

## Tech Stack

- **Python**: Core automation logic
- **OpenAI GPT-4**: AI-powered resume and cover letter generation
- **Google Sheets API**: Job tracking and status updates
- **GitHub Actions**: Daily automation and scheduling

## Customization

You can customize the automation by editing `process_applications.py`:

- Update the `user_profile` variable with your own background and experience
- Modify the OpenAI prompts to match your writing style
- Adjust the temperature and max_tokens parameters for different creativity levels
- Change the schedule in `.github/workflows/job-automation.yml`

## Why I Built This

Job hunting can be exhausting, especially when you're applying to dozens of positions. I wanted a system that would help me:

- Stay organized with all my applications in one place
- Generate tailored application materials for each job
- Save time on repetitive tasks
- Never miss following up on interesting opportunities

This automation handles the tedious parts so I can focus on networking and preparing for interviews.

## License

This project is open source and available under the MIT License.
