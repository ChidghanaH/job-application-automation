"""Fetch jobs from Apify LinkedIn/Indeed scrapers"""
import os
import json
from apify_client import ApifyClient
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import APIFY_API_KEY, JOB_CRITERIA

def fetch_linkedin_jobs():
    """Fetch jobs from LinkedIn via Apify"""
    print("🔍 Connecting to Apify...")
    client = ApifyClient(APIFY_API_KEY)
    
    # Using LinkedIn Jobs Scraper actor (misceres/linkedin-jobs-scraper)
    # Find more actors at: https://apify.com/store
    run_input = {
        "keywords": " OR ".join(JOB_CRITERIA["job_titles"][:3]),  # First 3 titles
        "locations": JOB_CRITERIA["locations"][:2],  # Munich, München
        "maxItems": JOB_CRITERIA["max_jobs_per_run"]
    }
    
    print(f"📍 Searching for: {run_input['keywords']}")
    print(f"📍 Locations: {run_input['locations']}")
    
    try:
        # Run the Apify actor
        run = client.actor("misceres/linkedin-jobs-scraper").call(run_input=run_input)
        
        # Fetch results
        jobs = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            jobs.append({
                "title": item.get("title"),
                "company": item.get("company"),
                "location": item.get("location"),
                "description": item.get("description", "")[:500],
                "url": item.get("url"),
                "source": "linkedin",
                "posted_date": item.get("postedDate")
            })
        
        return jobs
    except Exception as e:
        print(f"❌ Error fetching jobs: {e}")
        return []

def main():
    print("\n" + "="*50)
    print("🤖 JOB FETCHER STARTING")
    print("="*50 + "\n")
    
    jobs = fetch_linkedin_jobs()
    
    # Save to data/raw_jobs.json
    os.makedirs("data", exist_ok=True)
    with open("data/raw_jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ SUCCESS: Fetched {len(jobs)} jobs")
    print(f"📁 Saved to: data/raw_jobs.json\n")

if __name__ == "__main__":
    main()
