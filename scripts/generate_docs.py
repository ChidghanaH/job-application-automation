import os
import json
from openai import OpenAI
import PyPDF2
from docx import Document

# Get API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Resume formats by country
RESUME_FORMATS = {
    "US": "1-page resume, no photo, concise bullet points",
    "DE": "Lebenslauf format with professional photo, detailed work history",
    "UK": "2-page CV, no photo, detailed achievements"
}

def extract_text_from_file(file_path):
    """Extract text from PDF or DOCX file"""
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    else:
        raise ValueError("Unsupported file format. Use .pdf or .docx")

def tailor_resume(resume_text, job_description, country="DE"):
    """Use OpenAI to tailor resume to job description"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    format_instructions = RESUME_FORMATS.get(country, RESUME_FORMATS["DE"])
    
    prompt = f"""You are an expert resume writer. Tailor this resume to match the job description.

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
4. Maintains truthfulness
5. Is ATS-friendly

Return only the tailored resume text."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_cover_letter(resume_text, job_description, company_name, country="DE"):
    """Generate cover letter using OpenAI"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""Write a compelling cover letter for this job application.

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

Return only the cover letter text."""
    
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
    
    # Try to find resume file (supports .pdf or .docx)
    resume_file = None
    for filename in os.listdir("."):
        if filename.endswith(('.pdf', '.docx')):
            resume_file = filename
            break
    
    if not resume_file:
        print("❌ Error: No resume file found (PDF or DOCX)")
        return
    
    print(f"📄 Loading resume from {resume_file}")
    resume_text = extract_text_from_file(resume_file)
    
    if not resume_text or len(resume_text) < 100:
        print("❌ Error: Resume text is too short or empty")
        return
    
    print(f"✅ Resume loaded successfully ({len(resume_text)} characters)")
    print(f"📄 Processing {len(jobs[:20])} top jobs...\n")
    
    os.makedirs("output", exist_ok=True)
    
    for i, job in enumerate(jobs[:20], 1):
        country = job.get("location", "DE").split(",")[-1].strip()
        country_code = "DE" if "Germany" in country or "Deutschland" in country else "UK" if "United Kingdom" in country else "US"
        
        print(f"{i}. {job['title']} at {job['company']} ({country_code})")
        
        try:
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
            
            with open(f"output/{job_id}/resume.txt", "w", encoding="utf-8") as f:
                f.write(tailored_resume)
            
            with open(f"output/{job_id}/cover_letter.txt", "w", encoding="utf-8") as f:
                f.write(cover_letter)
            
            job["documents_generated"] = True
            print(f"   ✅ Documents generated")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            job["documents_generated"] = False
    
    # Update jobs file
    with open("data/ranked_jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)
    
    print(f"\n✅ Completed! Generated documents for {len(jobs[:20])} jobs")

if __name__ == "__main__":
    process_jobs()
