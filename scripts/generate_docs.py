import os
import json
from openai import OpenAI
import PyPDF2
import requests

# Get API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FLOWCV_API_KEY = os.getenv("FLOWCV_API_KEY")

# Resume formats
RESUME_FORMATS = {
    "US": "1-page resume, no photo, concise bullet points",
    "DE": "Lebenslauf format with professional photo, detailed work history",
    "UK": "2-page CV, no photo, detailed achievements"
}
import os
def extract_text_from_pdf(pdf_path):
    """Extract text from PDF resume"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_flowcv_resume():
    """Fetch resume from FlowCV API"""
    headers = {"Authorization": f"Bearer {FLOWCV_API_KEY}"}
    response = requests.get("https://api.flowcv.com/v1/resumes", headers=headers)
    if response.status_code == 200:
        return response.json()["data"][0]["content"]
    return None

def tailor_resume(resume_text, job_description, country="US"):
    """Use OpenAI to tailor resume to job description"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    format_instructions = RESUME_FORMATS.get(country, RESUME_FORMATS["US"])
    
    prompt = f"""
    You are an expert resume writer. Tailor this resume to match the job description below.
    
    Resume Format Requirements ({country}):
    {format_instructions}
    
    Current Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Create a tailored resume that:
    1. Highlights relevant skills and experiences
    2. Uses keywords from the job description
    3. Follows the {country} resume format
    4. Maintains truthfulness (don't add fake experience)
    5. Is ATS-friendly
    
    Return only the tailored resume text.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def generate_cover_letter(resume_text, job_description, company_name, country="US"):
    """Generate a cover letter using OpenAI"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""
    You are an expert career coach. Write a compelling cover letter for this job application.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Company: {company_name}
    Country: {country}
    
    Create a cover letter that:
    1. Is specific to the role and company
    2. Highlights relevant achievements
    3. Shows enthusiasm and cultural fit
    4. Follows {country} business writing conventions
    5. Is concise (max 350 words)
    
    Return only the cover letter text.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def process_jobs():
    """Process ranked jobs and generate documents"""
    try:
        with open("data/ranked_jobs.json", "r") as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print("❌ Error: Run rank_jobs.py first")
        return
    
    # Get resume
    resume_path = os.getenv("RESUME_PDF_PATH")
    if resume_path and os.path.exists(resume_path):
        resume_text = extract_text_from_pdf(resume_path)
    else:
        resume_text = get_flowcv_resume()
    
    if not resume_text:
        print("❌ Error: No resume found")
        return
    
    print(f"📄 Processing {len(jobs[:10])} top jobs...")
    
    for i, job in enumerate(jobs[:10], 1):
        country = job.get("location", "US").split(",")[-1].strip()
        country_code = "DE" if "Germany" in country else "UK" if "United Kingdom" in country else "US"
        
        # Generate tailored resume
        tailored_resume = tailor_resume(resume_text, job["description"], country_code)
        
        # Generate cover letter
        cover_letter = generate_cover_letter(
            resume_text, 
            job["description"], 
            job["company"],
            country_code
        )
        
        # Save documents
        job_id = f"{job['company'].replace(' ', '_')}_{i}"
        os.makedirs(f"output/{job_id}", exist_ok=True)
        
        with open(f"output/{job_id}/resume.txt", "w") as f:
            f.write(tailored_resume)
        
        with open(f"output/{job_id}/cover_letter.txt", "w") as f:
            f.write(cover_letter)
        
        job["documents_generated"] = True
        
        print(f"✅ {i}. {job['title']} at {job['company']}")
    
    # Update jobs file
    with open("data/ranked_jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)
    
    print(f"\n✅ Generated documents for {len(jobs[:10])} jobs")

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    process_jobs()
