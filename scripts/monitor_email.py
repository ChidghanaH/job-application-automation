import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import re
from datetime import datetime
from config import EMAIL_KEYWORDS
from update_sheet import update_status_from_email

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Authenticate and return Gmail API service"""
    creds = None
    token_json = os.getenv("GMAIL_TOKEN_JSON")
    
    if token_json:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write(token_json)
            token_file = f.name
        
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        os.unlink(token_file)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise ValueError("Gmail authentication required. Run locally first to generate token.")
    
    return build('gmail', 'v1', credentials=creds)

def extract_email_body(payload):
    """Extract text from email body"""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
    else:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')
    
    return body

def classify_email(subject, body):
    """Classify email type based on keywords"""
    subject_lower = subject.lower()
    body_lower = body.lower()
    text = f"{subject_lower} {body_lower}"
    
    # Check for interview invitation
    if any(keyword in text for keyword in EMAIL_KEYWORDS['interview']):
        return 'Interview Scheduled'
    
    # Check for rejection
    if any(keyword in text for keyword in EMAIL_KEYWORDS['rejection']):
        return 'Rejected'
    
    # Check for offer
    if any(keyword in text for keyword in EMAIL_KEYWORDS['offer']):
        return 'Offer Received'
    
    # Check for application received
    if any(keyword in text for keyword in EMAIL_KEYWORDS['received']):
        return 'Application Received'
    
    return None

def extract_company_position(subject, body):
    """Try to extract company name and position from email"""
    # Common patterns in job emails
    patterns = [
        r'(position|role|opportunity)\s+(?:of|as|for)?\s+([\w\s]+)\s+at\s+([\w\s]+)',
        r'([\w\s]+)\s+-\s+([\w\s]+)\s+position',
        r'application\s+for\s+([\w\s]+)\s+at\s+([\w\s]+)',
    ]
    
    text = f"{subject} {body}"
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                return {
                    'position': groups[-2].strip(),
                    'company': groups[-1].strip()
                }
    
    return None

def monitor_emails():
    """Monitor Gmail for job application responses"""
    service = get_gmail_service()
    
    # Get unread messages from last 7 days
    query = 'is:unread newer_than:7d (from:noreply OR from:recruiting OR from:hr OR subject:application OR subject:interview OR subject:opportunity)'
    
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("✅ No new job-related emails found")
            return
        
        print(f"📧 Found {len(messages)} potential job emails...\n")
        
        updates = []
        
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            body = extract_email_body(msg_data['payload'])
            
            # Classify email
            status = classify_email(subject, body)
            
            if status:
                print(f"✅ {status}: {subject[:60]}...")
                print(f"   From: {sender}")
                
                # Extract company and position
                info = extract_company_position(subject, body)
                
                if info:
                    email_data = {
                        'company': info['company'],
                        'position': info['position'],
                        'status': status,
                        'notes': f"Email received: {datetime.now().strftime('%Y-%m-%d')}\nSubject: {subject}"
                    }
                    
                    updates.append(email_data)
                    
                    # Mark as read
                    service.users().messages().modify(
                        userId='me',
                        id=msg['id'],
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                else:
                    print(f"   ⚠️ Could not extract company/position details")
                
                print()
        
        # Update spreadsheet
        if updates:
            print(f"\n📄 Updating {len(updates)} jobs in spreadsheet...")
            for update in updates:
                update_status_from_email(update)
        
        print(f"\n✅ Email monitoring complete!")
        
    except Exception as e:
        print(f"❌ Error monitoring emails: {e}")

if __name__ == "__main__":
    monitor_emails()
