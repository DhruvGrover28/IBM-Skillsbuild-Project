"""
Scraper Agent - Job Portal Scraping
Scrapes job listings from LinkedIn, Indeed, Internshala, and other job portals
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import json

from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import requests

from backend.database.db_connection import database
from backend.utils.scraper_helpers import (
    clean_text, 
    extract_salary, 
    parse_job_date, 
    generate_user_agent,
    wait_random_delay
)

logger = logging.getLogger(__name__)


class ScraperAgent:
    """Autonomous agent for scraping job listings from multiple portals"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.scraped_jobs: List[Dict] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': generate_user_agent()
        })
        
        # Portal configurations
        self.portals = {
            'linkedin': {
                'base_url': 'https://www.linkedin.com/jobs/search',
                'scraper': self._scrape_linkedin
            },
            'indeed': {
                'base_url': 'https://www.indeed.com/jobs',
                'scraper': self._scrape_indeed
            },
            'internshala': {
                'base_url': 'https://internshala.com/jobs',
                'scraper': self._scrape_internshala
            }
        }
    
    async def initialize(self):
        """Initialize the scraper agent"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            logger.info("Scraper agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize scraper agent: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        self.session.close()
    
    async def scrape_jobs(self, search_params: Dict) -> List[Dict]:
        """
        Main method to scrape jobs from all portals
        
        Args:
            search_params: {
                'keywords': 'python developer',
                'location': 'San Francisco',
                'experience_level': 'entry',
                'job_type': 'full-time',
                'remote_ok': True,
                'max_jobs': 50
            }
        """
        self.scraped_jobs = []
        total_jobs = 0
        max_jobs = search_params.get('max_jobs', 50)
        
        # Log scraping start
        await database.log_system_activity(
            agent_name="scraper_agent",
            action="scrape_start",
            message=f"Starting job search with params: {search_params}"
        )
        
        for portal_name, portal_config in self.portals.items():
            try:
                logger.info(f"Scraping {portal_name}...")
                
                # Create scraping log entry
                scraping_log_id = await self._create_scraping_log(
                    portal_name, search_params
                )
                
                # Scrape jobs from this portal
                portal_jobs = await portal_config['scraper'](search_params)
                
                # Add portal metadata to jobs
                for job in portal_jobs:
                    job['source'] = portal_name
                    job['scraped_at'] = datetime.utcnow().isoformat()
                
                self.scraped_jobs.extend(portal_jobs)
                total_jobs += len(portal_jobs)
                
                # Update scraping log
                await self._update_scraping_log(
                    scraping_log_id, len(portal_jobs), "completed"
                )
                
                logger.info(f"Scraped {len(portal_jobs)} jobs from {portal_name}")
                
                # Stop if we've reached max jobs
                if total_jobs >= max_jobs:
                    break
                
                # Random delay between portals
                await wait_random_delay(2, 5)
                
            except Exception as e:
                logger.error(f"Error scraping {portal_name}: {e}")
                await self._update_scraping_log(
                    scraping_log_id, 0, "failed", str(e)
                )
                continue
        
        # Remove duplicates and save to database
        unique_jobs = self._remove_duplicates(self.scraped_jobs)
        saved_jobs = await database.save_jobs(unique_jobs[:max_jobs])
        
        await database.log_system_activity(
            agent_name="scraper_agent",
            action="scrape_complete",
            message=f"Scraping completed. Found {total_jobs} jobs, saved {len(saved_jobs)} unique jobs",
            metadata={"total_found": total_jobs, "unique_saved": len(saved_jobs)}
        )
        
        return saved_jobs
    
    async def _scrape_linkedin(self, search_params: Dict) -> List[Dict]:
        """Scrape jobs from LinkedIn"""
        jobs = []
        
        try:
            if not self.page:
                self.page = await self.browser.new_page()
            
            # Build LinkedIn search URL
            keywords = search_params.get('keywords', '')
            location = search_params.get('location', '')
            
            params = {
                'keywords': keywords,
                'location': location,
                'f_TP': '1',  # Past 24 hours
                'f_E': '1,2' if search_params.get('experience_level') == 'entry' else '3,4'
            }
            
            url = f"https://www.linkedin.com/jobs/search?"
            url += "&".join([f"{k}={v}" for k, v in params.items()])
            
            await self.page.goto(url, wait_until='networkidle')
            await wait_random_delay(3, 6)
            
            # Extract job cards
            job_cards = await self.page.query_selector_all('.job-search-card')
            
            for card in job_cards[:20]:  # Limit to 20 jobs per portal
                try:
                    job_data = await self._extract_linkedin_job(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Error extracting LinkedIn job: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
        
        return jobs
    
    async def _extract_linkedin_job(self, card) -> Optional[Dict]:
        """Extract job data from LinkedIn job card"""
        try:
            # Extract basic info
            title_elem = await card.query_selector('.job-search-card__title')
            title = await title_elem.inner_text() if title_elem else "Unknown"
            
            company_elem = await card.query_selector('.job-search-card__subtitle-link')
            company = await company_elem.inner_text() if company_elem else "Unknown"
            
            location_elem = await card.query_selector('.job-search-card__location')
            location = await location_elem.inner_text() if location_elem else "Unknown"
            
            # Extract job URL
            link_elem = await card.query_selector('.job-search-card__title a')
            job_url = await link_elem.get_attribute('href') if link_elem else ""
            if job_url and not job_url.startswith('http'):
                job_url = f"https://www.linkedin.com{job_url}"
            
            # Generate external ID
            external_id = f"linkedin_{hash(f'{title}_{company}_{location}')}"
            
            return {
                'external_id': external_id,
                'title': clean_text(title),
                'company': clean_text(company),
                'location': clean_text(location),
                'apply_url': job_url,
                'posted_date': datetime.utcnow() - timedelta(days=1),  # Approximate
                'job_type': 'full-time',  # Default
                'experience_level': 'entry',  # Default
                'remote_allowed': 'remote' in location.lower()
            }
            
        except Exception as e:
            logger.warning(f"Error extracting LinkedIn job data: {e}")
            return None
    
    async def _scrape_indeed(self, search_params: Dict) -> List[Dict]:
        """Scrape jobs from Indeed"""
        jobs = []
        
        try:
            # Use requests for Indeed (simpler structure)
            keywords = search_params.get('keywords', '')
            location = search_params.get('location', '')
            
            params = {
                'q': keywords,
                'l': location,
                'fromage': '1',  # Last 24 hours
                'limit': '20'
            }
            
            url = "https://www.indeed.com/jobs"
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards[:20]:
                    try:
                        job_data = self._extract_indeed_job(card)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        logger.warning(f"Error extracting Indeed job: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
        
        return jobs
    
    def _extract_indeed_job(self, card) -> Optional[Dict]:
        """Extract job data from Indeed job card"""
        try:
            # Extract title
            title_elem = card.find('h2', class_='jobTitle')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract company
            company_elem = card.find('span', class_='companyName')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('div', class_='companyLocation')
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            # Extract salary if available
            salary_elem = card.find('span', class_='salaryText')
            salary_text = salary_elem.get_text(strip=True) if salary_elem else ""
            salary_min, salary_max = extract_salary(salary_text)
            
            # Extract job URL
            link_elem = title_elem.find('a') if title_elem else None
            job_url = link_elem.get('href') if link_elem else ""
            if job_url and not job_url.startswith('http'):
                job_url = f"https://www.indeed.com{job_url}"
            
            # Generate external ID
            external_id = f"indeed_{hash(f'{title}_{company}_{location}')}"
            
            return {
                'external_id': external_id,
                'title': clean_text(title),
                'company': clean_text(company),
                'location': clean_text(location),
                'salary_min': salary_min,
                'salary_max': salary_max,
                'apply_url': job_url,
                'posted_date': datetime.utcnow() - timedelta(days=1),
                'job_type': 'full-time',
                'experience_level': 'entry',
                'remote_allowed': 'remote' in location.lower()
            }
            
        except Exception as e:
            logger.warning(f"Error extracting Indeed job data: {e}")
            return None
    
    async def _scrape_internshala(self, search_params: Dict) -> List[Dict]:
        """Scrape jobs from Internshala"""
        jobs = []
        
        try:
            if not self.page:
                self.page = await self.browser.new_page()
            
            # Build Internshala search URL
            keywords = search_params.get('keywords', '')
            location = search_params.get('location', '')
            
            url = f"https://internshala.com/jobs/{keywords.replace(' ', '-')}-jobs"
            if location:
                url += f"-in-{location.replace(' ', '-').replace(',', '')}"
            
            await self.page.goto(url, wait_until='networkidle')
            await wait_random_delay(2, 4)
            
            # Extract job cards
            job_cards = await self.page.query_selector_all('.individual_internship')
            
            for card in job_cards[:15]:  # Limit to 15 jobs
                try:
                    job_data = await self._extract_internshala_job(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Error extracting Internshala job: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Internshala scraping error: {e}")
        
        return jobs
    
    async def _extract_internshala_job(self, card) -> Optional[Dict]:
        """Extract job data from Internshala job card"""
        try:
            # Extract title
            title_elem = await card.query_selector('.job-title')
            title = await title_elem.inner_text() if title_elem else "Unknown"
            
            # Extract company
            company_elem = await card.query_selector('.company-name')
            company = await company_elem.inner_text() if company_elem else "Unknown"
            
            # Extract location
            location_elem = await card.query_selector('.location-names')
            location = await location_elem.inner_text() if location_elem else "Unknown"
            
            # Extract salary
            salary_elem = await card.query_selector('.salary')
            salary_text = await salary_elem.inner_text() if salary_elem else ""
            salary_min, salary_max = extract_salary(salary_text)
            
            # Extract job URL
            link_elem = await card.query_selector('a')
            job_url = await link_elem.get_attribute('href') if link_elem else ""
            if job_url and not job_url.startswith('http'):
                job_url = f"https://internshala.com{job_url}"
            
            # Generate external ID
            external_id = f"internshala_{hash(f'{title}_{company}_{location}')}"
            
            return {
                'external_id': external_id,
                'title': clean_text(title),
                'company': clean_text(company),
                'location': clean_text(location),
                'salary_min': salary_min,
                'salary_max': salary_max,
                'apply_url': job_url,
                'posted_date': datetime.utcnow() - timedelta(days=1),
                'job_type': 'full-time',
                'experience_level': 'entry',
                'remote_allowed': 'remote' in location.lower() or 'work from home' in location.lower()
            }
            
        except Exception as e:
            logger.warning(f"Error extracting Internshala job data: {e}")
            return None
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    async def _create_scraping_log(self, source: str, search_params: Dict) -> int:
        """Create a scraping log entry"""
        # This would integrate with the database to create a log entry
        # For now, return a dummy ID
        return hash(f"{source}_{datetime.utcnow()}")
    
    async def _update_scraping_log(self, log_id: int, jobs_found: int, 
                                 status: str, error_message: str = None):
        """Update scraping log entry"""
        # This would update the database log entry
        pass
    
    async def get_recent_jobs(self, hours: int = 24) -> List[Dict]:
        """Get jobs scraped in the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [job for job in self.scraped_jobs 
                if datetime.fromisoformat(job.get('scraped_at', '')) > cutoff_time]
    
    def is_healthy(self) -> bool:
        """Check if the scraper agent is healthy"""
        return self.browser is not None
