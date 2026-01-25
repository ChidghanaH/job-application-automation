import os
import json
from datetime import datetime

def save_applications_to_file():
    """Save job applications to a JSON file in the repo"""
    try:
        with open("data/ranked_jobs.json", "r") as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No ranked jobs found")
        return
    
    # Create applications tracking file
    applications = []
    
    for job in jobs:
        application = {
            "company": job.get('company', ''),
            "position": job.get('title', ''),
            "location": job.get('location', ''),
            "application_date": datetime.now().strftime('%Y-%m-%d'),
            "status": job.get('status', 'To Apply'),
            "match_score": f"{job.get('match_score', 0):.0f}%",
            "job_url": job.get('url', ''),
            "career_page": job.get('career_page', ''),
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "notes": job.get('notes', '')
        }
        applications.append(application)
    
    # Save to file
    os.makedirs("data", exist_ok=True)
    with open("data/applications_tracking.json", "w") as f:
        json.dump(applications, f, indent=2)
    
    print(f"✅ Saved {len(applications)} applications to data/applications_tracking.json")
    print("\n📋 You can view all applications at:")
    print("https://github.com/ChidghanaH/job-application-automation/blob/main/data/applications_tracking.json")
    
    # Also create a simple text summary
    with open("data/applications_summary.txt", "w") as f:
        f.write(f"Job Applications Summary\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"="*80 + "\n\n")
        
        for i, app in enumerate(applications, 1):
            f.write(f"{i}. {app['company']} - {app['position']}\n")
            f.write(f"   Location: {app['location']}\n")
            f.write(f"   Match Score: {app['match_score']}\n")
            f.write(f"   Status: {app['status']}\n")
            f.write(f"   Job URL: {app['job_url']}\n")
            if app['career_page']:
                f.write(f"   Career Page: {app['career_page']}\n")
            f.write(f"\n")
    
    print("✅ Summary saved to data/applications_summary.txt")

def update_status_from_email(email_data):
    """Update job status based on email content"""
    try:
        with open("data/applications_tracking.json", "r") as f:
            applications = json.load(f)
    except FileNotFoundError:
        print("❌ No applications file found")
        return False
    
    company = email_data.get('company')
    position = email_data.get('position')
    new_status = email_data.get('status')
    notes = email_data.get('notes', '')
    
    # Find matching application
    for app in applications:
        if (app.get('company', '').lower() == company.lower() and 
            app.get('position', '').lower() == position.lower()):
            
            # Update status and notes
            app['status'] = new_status
            app['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            if notes:
                existing_notes = app.get('notes', '')
                app['notes'] = f"{existing_notes}\n{notes}" if existing_notes else notes
            
            # Save updated file
            with open("data/applications_tracking.json", "w") as f:
                json.dump(applications, f, indent=2)
            
            print(f"✅ Updated {company} - {position}: {new_status}")
            return True
    
    print(f"⚠️ No matching job found for {company} - {position}")
    return False

if __name__ == "__main__":
    save_applications_to_file()
