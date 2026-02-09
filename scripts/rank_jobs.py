"""Rank and filter jobs using AI-powered resume matching"""
import json
import os
import sys
import time
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Your resume profile
USER_RESUME = """
Master's student in Business Analytics with 3+ years of experience in market data management and competitive analysis. 

SKILLS:
- Data Analytics: SQL, Python, Excel (advanced), ETL processes
- Business Intelligence: Power BI, Google Data Studio
- Project Management: Agile, Scrum, Waterfall, stakeholder management
- Tools: Jira, Confluence, Git
- Languages: English (fluent), German (B1)

EXPERIENCE:
- 3+ years in market data management and competitive analysis
- Business development and process optimization
- Macroeconomic analysis and data-driven decision making
- Cross-functional team collaboration

EDUCATION:
- MSc Business Analytics (current)
- Project Management Foundations certification

SEEKING:
- Junior Project Manager or Data Analyst roles in Munich
- PMO positions
- Business Analyst roles
"""

def calculate_ai_match_score(job):
    """Use OpenAI to calculate match score between job and resume"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""You are an expert career advisor. Compare this job description with the candidate's resume and provide a match score.

JOB POSTING:
Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')}
Location: {job.get('location', 'N/A')}
Description: {job.get('description', 'N/A')}

CANDIDATE RESUME:
{USER_RESUME}

INSTRUCTIONS:
1. Analyze how well the candidate's skills, experience, and background match the job requirements
2. Consider: required skills, years of experience, education, location fit
3. Provide a match score from 0-100%
4. Be realistic and honest in your assessment

RESPONSE FORMAT:
Return ONLY a JSON object with this exact structure:
{{
    "match_score": <number between 0-100>,
    "reasoning": "<brief explanation of the match>",
    "key_matches": ["<skill/experience 1>", "<skill/experience 2>"],
    "gaps": ["<missing requirement 1>", "<missing requirement 2>"]
}}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert career advisor and recruiter who evaluates job-candidate fit."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error calculating AI match for {job.get('title')}: {e}")
        return {
            "match_score": 0,
            "reasoning": "Error in analysis",
            "key_matches": [],
            "gaps": []
        }

def main():
    print("\n" + "="*50)
    print("AI-Powered Job Matcher")
    print("="*50 + "\n")
    
    try:
        with open("data/raw_jobs.json", "r", encoding="utf-8") as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print("Error: Run fetch_jobs.py first")
        return
    
    print(f"Total jobs to analyze: {len(jobs)}")
    print("Using OpenAI to calculate match scores...\n")
    
    scored_jobs = []
    for i, job in enumerate(jobs, 1):
        print(f"Analyzing {i}/{len(jobs)}: {job.get('title')} at {job.get('company')}...")
        
        ai_result = calculate_ai_match_score(job)
        
        job["match_score"] = ai_result["match_score"] / 100  # Convert to 0-1 scale
        job["match_reasoning"] = ai_result["reasoning"]
        job["key_matches"] = ai_result["key_matches"]
        job["gaps"] = ai_result["gaps"]
        
        print(f"   Match: {ai_result['match_score']}%")
        
        # Only keep jobs with 80%+ match
        if ai_result["match_score"] >= 80:
            scored_jobs.append(job)
            print(f"   ✓ QUALIFIED - Adding to pipeline")
        else:
            print(f"   ✗ Below threshold (need 80%+)")
        
        # Rate limiting
        time.sleep(1)
        print()
    
    # Sort by match score
    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Save results
    with open("data/ranked_jobs.json", "w", encoding="utf-8") as f:
        json.dump(scored_jobs, f, indent=2, ensure_ascii=False)
    
    print("="*50)
    print(f"RESULTS: {len(scored_jobs)} jobs qualified (80%+ match)")
    print("="*50 + "\n")
    
    if scored_jobs:
        print("Top qualified positions:")
        for i, job in enumerate(scored_jobs[:5], 1):
            print(f"\n{i}. {job['title']} at {job['company']}")
            print(f"   Match: {job['match_score']*100:.0f}%")
            print(f"   Reason: {job['match_reasoning']}")
            print(f"   Strengths: {', '.join(job['key_matches'][:3])}")
    else:
        print("No jobs met the 80% match threshold.")

if __name__ == "__main__":
    main()
