import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import GOOGLE_SHEET_ID

def setup_gspread():
    """Setup Google Sheets authentication"""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Use service account credentials from environment
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set")
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write(creds_json)
        creds_file = f.name
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    
    os.unlink(creds_file)  # Clean up temp file
    return client

def initialize_sheet(sheet):
    """Initialize sheet with headers if empty"""
    try:
        headers = sheet.row_values(1)
        if not headers:
            raise Exception("Empty sheet")
    except:
        # Create headers
        headers = [
            "Company",
            "Position",
            "Location",
            "Application Date",
            "Status",
            "Match Score",
            "Job URL",
            "Career Page",
            "Last Updated",
            "Notes"
        ]
        sheet.insert_row(headers, 1)
        sheet.format('1', {'textFormat': {'bold': True}})

def update_applications():
    """Update Google Sheets with job applications"""
    try:
        with open("data/ranked_jobs.json", "r") as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No ranked jobs found")
        return
    
    client = setup_gspread()
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    initialize_sheet(sheet)
    
    print(f"📊 Updating spreadsheet with {len(jobs)} jobs...")
    
    # Get existing rows to avoid duplicates
    existing_jobs = sheet.get_all_records()
    existing_urls = {job.get('Job URL', ''): i+2 for i, job in enumerate(existing_jobs)}
    
    for job in jobs:
        row_data = [
            job.get('company', ''),
            job.get('title', ''),
            job.get('location', ''),
            datetime.now().strftime('%Y-%m-%d'),
            job.get('status', 'To Apply'),
            f"{job.get('match_score', 0):.0f}%",
            job.get('url', ''),
            job.get('career_page', ''),
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            job.get('notes', '')
        ]
        
        job_url = job.get('url', '')
        
        if job_url in existing_urls:
            # Update existing row
            row_num = existing_urls[job_url]
            sheet.update(f'A{row_num}:J{row_num}', [row_data])
            print(f"➡️ Updated: {job.get('company')} - {job.get('title')}")
        else:
            # Append new row
            sheet.append_row(row_data)
            print(f"✅ Added: {job.get('company')} - {job.get('title')}")
    
    print(f"\n✅ Spreadsheet updated successfully!")
    print(f"🔗 View at: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")

def update_status_from_email(email_data):
    """Update job status based on email content"""
    client = setup_gspread()
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    
    company = email_data.get('company')
    position = email_data.get('position')
    new_status = email_data.get('status')
    notes = email_data.get('notes', '')
    
    # Find matching row
    all_records = sheet.get_all_records()
    for i, record in enumerate(all_records, start=2):
        if (record.get('Company', '').lower() == company.lower() and 
            record.get('Position', '').lower() == position.lower()):
            
            # Update status and notes
            sheet.update(f'E{i}', new_status)  # Status column
            sheet.update(f'I{i}', datetime.now().strftime('%Y-%m-%d %H:%M'))  # Last Updated
            
            if notes:
                existing_notes = record.get('Notes', '')
                updated_notes = f"{existing_notes}\n{notes}" if existing_notes else notes
                sheet.update(f'J{i}', updated_notes)
            
            print(f"✅ Updated {company} - {position}: {new_status}")
            return True
    
    print(f"⚠️ No matching job found for {company} - {position}")
    return False

if __name__ == "__main__":
    update_applications()
