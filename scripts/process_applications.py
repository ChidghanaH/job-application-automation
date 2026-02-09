import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from openai import OpenAI
from datetime import datetime
import time

def connect_to_sheets():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds_dict = eval(os.environ['GOOGLE_SHEETS_CREDENTIALS'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    sheet_id = os.environ['SHEET_ID']
    return client.open_by_key(sheet_id)

def get_job_listings(sheet):
    worksheet = sheet.worksheet('Jobs')
    records = worksheet.get_all_records()
    return [r for r in records if r.get('Status') == 'New']

def generate_resume_with_openai(job, user_profile):
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    prompt = f"""Create a tailored resume for the following job posting:

Job Title: {job.get('Title', 'N/A')}
Company: {job.get('Company', 'N/A')}
Location: {job.get('Location', 'N/A')}
Description: {job.get('Description', 'N/A')}

Candidate Profile:
{user_profile}

Generate a professional resume in markdown format that highlights relevant experience and skills for this position."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional resume writer who creates ATS-friendly, tailored resumes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def generate_cover_letter(job, user_profile):
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    prompt = f"""Create a compelling cover letter for the following job:

Job Title: {job.get('Title', 'N/A')}
Company: {job.get('Company', 'N/A')}
Location: {job.get('Location', 'N/A')}
Description: {job.get('Description', 'N/A')}

Candidate Profile:
{user_profile}

Write a professional cover letter that demonstrates enthusiasm and fit for this role."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional career coach who writes compelling cover letters."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def save_documents(resume, cover_letter, job_title, company):
    os.makedirs('output/resumes', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_company = company.replace(' ', '_').replace('/', '_')
    safe_title = job_title.replace(' ', '_').replace('/', '_')
    
    resume_path = f'output/resumes/{safe_company}_{safe_title}_{timestamp}_resume.md'
    cover_path = f'output/resumes/{safe_company}_{safe_title}_{timestamp}_cover.md'
    
    with open(resume_path, 'w', encoding='utf-8') as f:
        f.write(resume)
    
    with open(cover_path, 'w', encoding='utf-8') as f:
        f.write(cover_letter)
    
    print(f"Documents saved for {company} - {job_title}")

def update_job_status(sheet, row_number, status):
    worksheet = sheet.worksheet('Jobs')
    worksheet.update_cell(row_number + 2, worksheet.find('Status').col, status)

def main():
    print("Connecting to Google Sheets...")
    sheet = connect_to_sheets()
    
    user_profile = """Master's student in Business Analytics with 3+ years of experience in market data management and competitive analysis. Strong background in data analytics, ETL processes, business intelligence (Power BI, Google Data Studio), and project management. Proficient in SQL and Python. Seeking project management and PMO roles in Munich."""
    
    print("Fetching job listings...")
    jobs = get_job_listings(sheet)
    print(f"Found {len(jobs)} new job listings")
    
    for idx, job in enumerate(jobs, 1):
        print(f"\nProcessing job {idx}/{len(jobs)}: {job.get('Title')} at {job.get('Company')}")
        
        try:
            resume = generate_resume_with_openai(job, user_profile)
            time.sleep(1)
            
            cover_letter = generate_cover_letter(job, user_profile)
            time.sleep(1)
            
            save_documents(
                resume, 
                cover_letter, 
                job.get('Title', 'Unknown'), 
                job.get('Company', 'Unknown')
            )
            
            update_job_status(sheet, idx - 1, 'Processed')
            print(f"Successfully processed: {job.get('Title')} at {job.get('Company')}")
            
        except Exception as e:
            print(f"Error processing job: {str(e)}")
            update_job_status(sheet, idx - 1, 'Error')
    
    print("\nJob processing complete!")

if __name__ == '__main__':
    main()
