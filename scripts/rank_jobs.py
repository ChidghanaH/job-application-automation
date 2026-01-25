"""Rank and filter jobs by match score"""
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import JOB_CRITERIA

def calculate_match_score(job):
    """Calculate 0-1 match score based on keywords"""
    text = (job.get("description", "") + " " + job.get("title", "")).lower()
    
    matches = sum(1 for kw in JOB_CRITERIA["keywords"] if kw.lower() in text)
    total = len(JOB_CRITERIA["keywords"])
    
    has_excluded = any(exc.lower() in text for exc in JOB_CRITERIA["exclude_keywords"])
    if has_excluded:
        return 0.0
    
    return matches / total

def main():
    print("\n" + "="*50)
    print("🎯 JOB RANKER")
    print("="*50 + "\n")
    
    try:
        with open("data/raw_jobs.json", "r", encoding="utf-8") as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print("❌ Error: Run fetch_jobs.py first")
        return
    
    print(f"📊 Total: {len(jobs)} jobs")
    
    scored_jobs = []
    for job in jobs:
        score = calculate_match_score(job)
        if score >= JOB_CRITERIA["min_match_score"]:
            job["match_score"] = round(score, 2)
            scored_jobs.append(job)
    
    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    with open("data/ranked_jobs.json", "w", encoding="utf-8") as f:
        json.dump(scored_jobs, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Kept {len(scored_jobs)} jobs above {JOB_CRITERIA['min_match_score']*100}% match\n")
    
    if scored_jobs:
        print("🏆 Top 5:")
        for i, job in enumerate(scored_jobs[:5], 1):
            print(f"{i}. {job['title']} - {job['company']} ({job['match_score']*100:.0f}%)")

if __name__ == "__main__":
    main()
