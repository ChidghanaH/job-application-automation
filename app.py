"""Streamlit UI for Job Application Automation"""
import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# Import your existing scripts
from scripts.fetch_jobs import fetch_jobs
from scripts.rank_jobs import rank_jobs
from scripts.generate_docs import generate_documents
from scripts.update_sheet import update_google_sheet
from scripts.company_scraper import fetch_company_jobs
from config import JOB_CRITERIA, COMPANY_CAREERS

# Page config
st.set_page_config(
    page_title="Job Application Automation",
    page_icon="💼",
    layout="wide"
)

# Title
st.title("Job Application Automation Dashboard")
st.markdown("Personal automation tool for Munich-based PM & Data Analyst job search")

# Sidebar - Settings
with st.sidebar:
    st.header("Settings")
    
    # Job source selection
    mode = st.radio(
        "Job Source",
        ["Job Boards (LinkedIn/Indeed)", "Company Career Pages"],
        index=0,
        help="Choose where to search for jobs"
    )
    
    st.markdown("---")
    
    # Location filters
    st.subheader("Location")
    location = st.text_input("Primary location", "Munich")
    
    # Match score filter
    st.subheader("Match Criteria")
    min_score = st.slider(
        "Minimum match score", 
        0.0, 1.0, 
        JOB_CRITERIA["min_match_score"],
        0.05,
        help="Jobs below this score will be filtered out"
    )
    
    # Max jobs
    max_jobs = st.number_input(
        "Max jobs to process",
        min_value=5,
        max_value=100,
        value=20,
        step=5
    )
    
    st.markdown("---")
    
    # Actions
    generate_docs = st.checkbox("Generate tailored resumes", value=True)
    update_sheets = st.checkbox("Update Google Sheets", value=True)
    
    st.markdown("---")
    
    # Run button
    run_button = st.button("Run Search", type="primary", use_container_width=True)

# Main content area
if run_button:
    # Create columns for status updates
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    with col2:
        st.subheader("Statistics")
        stats_container = st.empty()
    
    try:
        # Step 1: Fetch jobs
        status_text.info("Fetching jobs...")
        progress_bar.progress(20)
        
        if mode == "Job Boards (LinkedIn/Indeed)":
            jobs = fetch_jobs(location=location)
            source = "job_boards"
        else:
            jobs = fetch_company_jobs()
            source = "company_careers"
        
        raw_jobs_count = len(jobs)
        status_text.success(f"Found {raw_jobs_count} jobs from {source}")
        
        # Step 2: Rank jobs
        status_text.info("Ranking jobs by match score...")
        progress_bar.progress(40)
        
        ranked = rank_jobs(jobs, min_score=min_score, max_jobs=max_jobs)
        ranked_count = len(ranked)
        
        status_text.success(f"{ranked_count} jobs passed filters")
        progress_bar.progress(60)
        
        # Step 3: Generate documents (optional)
        if generate_docs and ranked_count > 0:
            status_text.info("Generating tailored resumes...")
            docs_generated = generate_documents(ranked)
            status_text.success(f"Generated {len(docs_generated)} documents")
        
        progress_bar.progress(80)
        
        # Step 4: Update Google Sheets (optional)
        if update_sheets and ranked_count > 0:
            status_text.info("Updating Google Sheets...")
            update_google_sheet(ranked)
            status_text.success("Google Sheets updated")
        
        progress_bar.progress(100)
        
        # Display statistics
        with stats_container:
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("Jobs Found", raw_jobs_count)
            with metric_col2:
                st.metric("Qualified Jobs", ranked_count)
            with metric_col3:
                match_rate = (ranked_count / raw_jobs_count * 100) if raw_jobs_count > 0 else 0
                st.metric("Match Rate", f"{match_rate:.1f}%")
        
        st.success("Pipeline completed successfully!")
        
        # Display results
        if ranked_count > 0:
            st.markdown("---")
            st.subheader("Top Matching Jobs")
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["Table View", "Detailed View"])
            
            with tab1:
                # Table view
                display_data = []
                for job in ranked:
                    display_data.append({
                        "Company": job.get("company", "N/A"),
                        "Title": job.get("title", "N/A"),
                        "Location": job.get("location", "N/A"),
                        "Score": f"{job.get('match_score', 0):.2f}",
                        "Link": job.get("link", "#")
                    })
                
                st.dataframe(display_data, use_container_width=True)
            
            with tab2:
                # Detailed cards view
                for idx, job in enumerate(ranked[:10]):  # Show top 10 in detail
                    with st.expander(f"{job.get('company', 'Unknown')} - {job.get('title', 'Unknown')}"):
                        col_a, col_b = st.columns([2, 1])
                        
                        with col_a:
                            st.markdown(f"**Company:** {job.get('company', 'N/A')}")
                            st.markdown(f"**Location:** {job.get('location', 'N/A')}")
                            st.markdown(f"**Source:** {job.get('source', 'N/A')}")
                            if job.get('description'):
                                st.markdown(f"**Description:** {job.get('description', '')[:200]}...")
                        
                        with col_b:
                            st.metric("Match Score", f"{job.get('match_score', 0):.2f}")
                            st.link_button("View Job", job.get('link', '#'))
        
        else:
            st.warning("No jobs matched your criteria. Try adjusting the filters.")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

else:
    # Welcome screen
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Job Boards")
        st.markdown("""
        Search LinkedIn, Indeed, and StepStone for jobs matching your criteria.
        - Automated scraping via Apify
        - Filter by location and keywords
        - Get fresh daily results
        """)
    
    with col2:
        st.subheader("Company Careers")
        st.markdown("""
        Visit specific company career pages directly.
        - Target companies you want to work for
        - Get jobs before they hit job boards
        - Customize company list
        """)
        
        if st.checkbox("Show target companies"):
            for company in COMPANY_CAREERS:
                st.markdown(f"- **{company['name']}**: {company['url']}")
    
    with col3:
        st.subheader("Automation")
        st.markdown("""
        Let the system do the heavy lifting.
        - AI-powered resume tailoring
        - Auto-track in Google Sheets
        - Daily GitHub Actions workflow
        """)
    
    st.markdown("---")
    
    # Recent runs (if data exists)
    if os.path.exists("data/ranked_jobs.json"):
        st.subheader("Last Run Results")
        
        try:
            with open("data/ranked_jobs.json", "r") as f:
                last_jobs = json.load(f)
            
            if last_jobs:
                st.info(f"Found {len(last_jobs)} jobs from last run")
                
                # Show top 5
                st.markdown("**Top 5 matches:**")
                for i, job in enumerate(last_jobs[:5], 1):
                    st.markdown(f"{i}. **{job.get('title')}** at {job.get('company')} - Score: {job.get('match_score', 0):.2f}")
        except:
            pass

# Footer
st.markdown("---")
st.caption("Made for Munich-based Junior PM & Data Analyst job search")
