"""Streamlit UI for Job Application Automation"""
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Import your existing scripts
from scripts.fetch_jobs import fetch_jobs
from scripts.rank_jobs import rank_jobs
from scripts.generate_docs import generate_documents
from scripts.update_sheet import update_google_sheet
from scripts.company_scraper import fetch_company_jobs
from config import JOB_CRITERIA, COMPANY_CAREERS

st.set_page_config(
    page_title="Job Automation Dashboard",
    page_icon="💼",
    layout="wide"
)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Run Automation", "Job Criteria", "Settings"])

if page == "Dashboard":
    st.title("💼 Job Application Dashboard")
    st.markdown("Monitor your job search progress and recent matches.")
    
    col1, col2, col3 = st.columns(3)
    
    # Load last run data
    if os.path.exists("data/ranked_jobs.json"):
        with open("data/ranked_jobs.json", "r") as f:
            last_jobs = json.load(f)
        
        with col1:
            st.metric("Jobs in Pipeline", len(last_jobs))
        with col2:
            avg_score = sum(j.get('match_score', 0) for j in last_jobs) / len(last_jobs) if last_jobs else 0
            st.metric("Avg. Match Score", f"{avg_score:.2f}")
        with col3:
            st.metric("Latest Run", datetime.now().strftime("%Y-%m-%d"))

        st.subheader("Top Matches")
        df = pd.DataFrame(last_jobs)
        if not df.empty:
            st.dataframe(df[['title', 'company', 'location', 'match_score', 'link']], use_container_width=True)
    else:
        st.info("No run data found. Head to 'Run Automation' to start.")

elif page == "Run Automation":
    st.title("🚀 Run Application Pipeline")
    
    with st.expander("Pipeline Settings", expanded=True):
        mode = st.radio("Search Mode", ["Job Boards", "Target Companies"])
        gen_docs = st.checkbox("Generate Tailored Documents", value=True)
        update_gsheet = st.checkbox("Update Google Sheet", value=True)
        limit = st.slider("Max jobs to process", 5, 50, 20)

    if st.button("Start Automation Pipeline", type="primary"):
        status = st.empty()
        progress = st.progress(0)
        
        try:
            status.info("🔍 Fetching jobs...")
            if mode == "Job Boards":
                jobs = fetch_jobs()
            else:
                jobs = fetch_company_jobs()
            progress.progress(25)
            
            status.info(f"📊 Ranking {len(jobs)} jobs...")
            ranked = rank_jobs(jobs, max_jobs=limit)
            progress.progress(50)
            
            if gen_docs:
                status.info("📝 Tailoring resumes and cover letters...")
                generate_documents(ranked)
                progress.progress(75)
                
            if update_gsheet:
                status.info("📝 Updating tracking sheet...")
                update_google_sheet(ranked)
                progress.progress(100)
                
            status.success(f"✅ Successfully processed {len(ranked)} jobs!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Pipeline failed: {str(e)}")

elif page == "Job Criteria":
    st.title("🎯 Matching Criteria")
    st.json(JOB_CRITERIA)

elif page == "Settings":
    st.title("⚙️ Configuration")
    st.write("Current environment variables status:")
    keys = ["OPENAI_API_KEY", "GOOGLE_SHEETS_CREDENTIALS", "SHEET_ID", "APIFY_API_TOKEN"]
    for key in keys:
        exists = "✅ Set" if os.getenv(key) else "❌ Missing"
        st.write(f"- **{key}**: {exists}")
