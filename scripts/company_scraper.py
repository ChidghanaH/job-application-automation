"""Company Career Pages Scraper"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import logging

from config import COMPANY_CAREERS, JOB_CRITERIA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_company_jobs() -> List[Dict]:
    """
    Fetch jobs from company career pages.
    
    Returns:
        List of job dictionaries
    """
    all_jobs = []
    
    for company in COMPANY_CAREERS:
        logger.info(f"Scraping {company['name']}...")
        
        try:
            jobs = scrape_company_page(company)
            all_jobs.extend(jobs)
            logger.info(f"Found {len(jobs)} jobs from {company['name']}")
            
            # Be polite - add delay between requests
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error scraping {company['name']}: {str(e)}")
            continue
    
    logger.info(f"Total jobs found from company pages: {len(all_jobs)}")
    return all_jobs


def scrape_company_page(company: Dict) -> List[Dict]:
    """
    Scrape a single company career page.
    
    Args:
        company: Company dictionary with name, url, and keywords
    
    Returns:
        List of job dictionaries
    """
    jobs = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(company['url'], headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Generic scraping - you'll need to customize selectors per company
        # This is a template that works for many career pages
        
        # Try common job listing selectors
        job_cards = (
            soup.select('.job-listing') or
            soup.select('.position') or
            soup.select('[class*="job"]') or
            soup.select('a[href*="/careers/"]') or
            soup.select('a[href*="/jobs/"]')
        )
        
        for card in job_cards[:50]:  # Limit to first 50 matches
            title = extract_title(card)
            link = extract_link(card, company['url'])
            location = extract_location(card)
            
            if not title or not link:
                continue
            
            # Filter by keywords and job titles
            if matches_criteria(title, company.get('keywords', [])):
                jobs.append({
                    'company': company['name'],
                    'title': title,
                    'location': location or 'Munich',  # Default to Munich
                    'link': link,
                    'source': 'company_careers',
                    'description': ''  # Could be fetched in a second pass
                })
        
    except Exception as e:
        logger.error(f"Error parsing {company['name']}: {str(e)}")
    
    return jobs


def extract_title(element) -> str:
    """
    Extract job title from an element.
    Tries multiple common patterns.
    """
    # Try different title extraction methods
    title = (
        element.get_text(strip=True) or
        element.get('title', '') or
        element.get('aria-label', '')
    )
    
    return title[:200] if title else ''  # Limit length


def extract_link(element, base_url: str) -> str:
    """
    Extract job link from an element.
    """
    link = element.get('href', '')
    
    if not link:
        # Try finding a link inside the element
        a_tag = element.find('a')
        if a_tag:
            link = a_tag.get('href', '')
    
    # Make absolute URL
    if link and not link.startswith('http'):
        base = base_url.rstrip('/')
        link = link.lstrip('/')
        link = f"{base}/{link}"
    
    return link


def extract_location(element) -> str:
    """
    Extract location from an element.
    """
    text = element.get_text()
    
    # Look for Munich/München in text
    for loc in ['Munich', 'München', 'Bavaria', 'Bayern', 'Germany']:
        if loc.lower() in text.lower():
            return loc
    
    return ''


def matches_criteria(title: str, keywords: List[str]) -> bool:
    """
    Check if job title matches search criteria.
    
    Args:
        title: Job title
        keywords: List of keywords to match
    
    Returns:
        True if matches, False otherwise
    """
    title_lower = title.lower()
    
    # Check against job titles from criteria
    for job_title in JOB_CRITERIA['job_titles']:
        if job_title.lower() in title_lower:
            return True
    
    # Check against company-specific keywords
    for keyword in keywords:
        if keyword.lower() in title_lower:
            return True
    
    # Check against general keywords from criteria
    matches = 0
    for keyword in JOB_CRITERIA['keywords']:
        if keyword.lower() in title_lower:
            matches += 1
    
    # Require at least 1 keyword match
    return matches >= 1


# Company-specific scrapers (optional - for better results)

def scrape_bmw(url: str) -> List[Dict]:
    """
    BMW-specific scraper.
    Customize based on BMW careers page structure.
    """
    # TODO: Implement BMW-specific logic
    pass


def scrape_siemens(url: str) -> List[Dict]:
    """
    Siemens-specific scraper.
    """
    # TODO: Implement Siemens-specific logic
    pass


if __name__ == '__main__':
    # Test the scraper
    jobs = fetch_company_jobs()
    print(f"Found {len(jobs)} jobs")
    
    for job in jobs[:5]:
        print(f"\n{job['company']}: {job['title']}")
        print(f"Link: {job['link']}")
