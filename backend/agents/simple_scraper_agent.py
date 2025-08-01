"""
Simple Scraper Agent - Windows Compatible Version
Uses requests + BeautifulSoup instead of Playwright for better compatibility
"""

import requests
import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import re
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    """Data class for job listings"""
    title: str
    company: str
    location: str
    description: str
    url: str
    salary: Optional[str] = None
    date_posted: Optional[str] = None
    job_type: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[List[str]] = None

class SimpleScraperAgent:
    """
    A simplified web scraper that uses HTTP requests instead of browser automation.
    More reliable on Windows and doesn't require subprocess functionality.
    """
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Job site configurations - using scraping-friendly sites
        self.job_sites = {
            'remoteok': {
                'base_url': 'https://remoteok.io/remote-{keywords}-jobs',
                'search_params': {},
                'parser': self._parse_remoteok_jobs,
                'enabled': True
            },
            'weworkremotely': {
                'base_url': 'https://weworkremotely.com/remote-jobs/search',
                'search_params': {
                    'term': '{keywords}'
                },
                'parser': self._parse_weworkremotely_jobs,
                'enabled': True
            },
            'jobsdb': {
                'base_url': 'https://www.jobsdb.com/jobs',
                'search_params': {
                    'keywords': '{keywords}',
                    'location': '{location}'
                },
                'parser': self._parse_jobsdb_jobs,
                'enabled': True
            },
            'glassdoor': {
                'base_url': 'https://www.glassdoor.com/Job/jobs.htm',
                'search_params': {
                    'sc.keyword': '{keywords}',
                    'locT': 'C',
                    'locId': '1'
                },
                'parser': self._parse_glassdoor_jobs,
                'enabled': True
            },
            'flexjobs': {
                'base_url': 'https://www.flexjobs.com/jobs',
                'search_params': {
                    'search': '{keywords}',
                    'location': '{location}'
                },
                'parser': self._parse_flexjobs_jobs,
                'enabled': True
            },
            'workingnomads': {
                'base_url': 'https://www.workingnomads.co',
                'search_params': {
                    'category': 'development'
                },
                'parser': self._parse_workingnomads_jobs,
                'enabled': True
            },
            'angel': {
                'base_url': 'https://wellfound.com/jobs',
                'search_params': {
                    'role': '{keywords}',
                    'location': '{location}'
                },
                'parser': self._parse_angel_jobs,
                'enabled': True
            },
            # Disabled sites with strict anti-bot protection
            'indeed': {
                'base_url': 'https://in.indeed.com/jobs',
                'search_params': {
                    'q': '{keywords}',
                    'l': '{location}',
                    'sort': 'date'
                },
                'parser': self._parse_indeed_jobs,
                'enabled': False  # Disabled due to 403 errors
            },
            'naukri': {
                'base_url': 'https://www.naukri.com/jobs-in-{location}',
                'search_params': {
                    'k': '{keywords}'
                },
                'parser': self._parse_naukri_jobs,
                'enabled': False  # Disabled due to 403 errors
            },
            'linkedin': {
                'base_url': 'https://www.linkedin.com/jobs/search',
                'search_params': {
                    'keywords': '{keywords}',
                    'location': '{location}'
                },
                'parser': self._parse_linkedin_jobs,
                'enabled': False  # Disabled due to 403 errors
            }
        }
    
    async def initialize(self):
        """Initialize the scraper agent with requests session"""
        try:
            # Create requests session
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            logger.info("Simple scraper agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize simple scraper agent: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            self.session.close()
        logger.info("Simple scraper agent cleaned up")
    
    async def scrape_jobs(self, search_params: Dict) -> List[JobListing]:
        """
        Scrape jobs from multiple job sites
        
        Args:
            search_params: Dict with 'keywords', 'location', 'job_type', etc.
        
        Returns:
            List of JobListing objects
        """
        if not self.session:
            await self.initialize()
        
        all_jobs = []
        keywords = search_params.get('keywords', '')
        location = search_params.get('location', 'India')
        max_results = search_params.get('max_results', 50)
        
        # Search on enabled job sites only
        enabled_sites = {name: config for name, config in self.job_sites.items() if config.get('enabled', True)}
        
        logger.info(f"Scraping jobs from {len(enabled_sites)} enabled sites: {list(enabled_sites.keys())}")
        
        for site_name, site_config in enabled_sites.items():
            try:
                logger.info(f"Scraping jobs from {site_name}")
                jobs = await self._scrape_site(site_name, site_config, keywords, location)
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs from {site_name}")
                
                # Add small delay between sites to be respectful
                await asyncio.sleep(2)
                
            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {site_name} - skipping")
                else:
                    logger.error(f"HTTP error scraping {site_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error scraping {site_name}: {e}")
                continue
        
        # Limit results and remove duplicates
        unique_jobs = self._remove_duplicates(all_jobs)
        return unique_jobs[:max_results]
    
    async def _scrape_site(self, site_name: str, site_config: Dict, keywords: str, location: str) -> List[JobListing]:
        """Scrape jobs from a specific site"""
        try:
            # Build search URL
            if '{keywords}' in site_config['base_url']:
                base_url = site_config['base_url'].format(
                    keywords=keywords.lower().replace(' ', '-'),
                    location=location.lower().replace(' ', '-')
                )
            else:
                base_url = site_config['base_url']
            
            # Build search parameters
            params = {}
            for param_key, param_template in site_config['search_params'].items():
                params[param_key] = param_template.format(
                    keywords=keywords,
                    location=location
                )
            
            logger.info(f"Making request to {base_url} with params: {params}")
            
            # Make request with error handling
            response = self.session.get(base_url, params=params, allow_redirects=True, timeout=30)
            
            if response.status_code == 403:
                logger.warning(f"Access forbidden (403) for {site_name} - this site blocks scraping")
                return []
            elif response.status_code == 429:
                logger.warning(f"Rate limited (429) for {site_name} - too many requests")
                return []
            elif response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} from {site_name}")
                return []
            
            response.raise_for_status()  # Raise exception for bad status codes
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Parse jobs using site-specific parser
            parser = site_config['parser']
            jobs = parser(soup, site_name)
            
            logger.info(f"Successfully parsed {len(jobs)} jobs from {site_name}")
            return jobs
                
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 403:
                logger.warning(f"Site {site_name} returned 403 Forbidden - disabling this source")
            else:
                logger.error(f"HTTP error for {site_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error scraping {site_name}: {e}")
            return []
    
    def _parse_indeed_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from Indeed (disabled but kept for reference)"""
        return []  # Disabled due to 403 errors
    
    def _parse_remoteok_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from RemoteOK"""
        jobs = []
        
        try:
            # RemoteOK job containers
            job_containers = soup.find_all(['tr'], class_='job')
            
            for container in job_containers[:10]:  # Limit to 10 jobs per site
                try:
                    # Extract job ID for URL construction
                    job_id = container.get('data-id') or container.get('id', '')
                    
                    # Extract job details with multiple selector attempts
                    title_elem = (container.find(['h2']) or 
                                container.find(['a'], class_='preventLink') or
                                container.find(['td'], class_='company position company_and_position'))
                    
                    company_elem = (container.find(['h3']) or 
                                  container.find(['td'], class_='company') or
                                  container.find(['span'], class_='company'))
                    
                    location_elem = (container.find(['div'], class_='location') or
                                   container.find(['td'], class_='location'))
                    
                    # Try to extract actual job URL from links
                    link_elem = container.find('a', href=True)
                    job_url = "https://remoteok.io"
                    if link_elem and link_elem.get('href'):
                        href = link_elem['href']
                        if href.startswith('/'):
                            job_url = f"https://remoteok.io{href}"
                        elif href.startswith('http'):
                            job_url = href
                    elif job_id:
                        job_url = f"https://remoteok.io/remote-jobs/{job_id}"
                    
                    # Get job title with fallback
                    title = "Remote Job Opportunity"
                    if title_elem:
                        title_text = title_elem.get_text(strip=True)
                        if title_text and len(title_text) > 2:
                            title = title_text
                    
                    # Get company with fallback
                    company = "Remote Company"
                    if company_elem:
                        company_text = company_elem.get_text(strip=True)
                        if company_text and len(company_text) > 1:
                            company = company_text
                    
                    # Get location with fallback
                    location = "Remote"
                    if location_elem:
                        location_text = location_elem.get_text(strip=True)
                        if location_text:
                            location = location_text
                    
                    # Extract description from multiple possible sources
                    desc_elem = (container.find(['div'], class_='description') or
                               container.find(['td'], class_='tags') or
                               container.find(['span'], class_='tags'))
                    
                    description = f"Remote position at {company}: {title}"
                    if desc_elem:
                        desc_text = desc_elem.get_text(strip=True)
                        if desc_text:
                            description = desc_text[:200] + "..." if len(desc_text) > 200 else desc_text
                    
                    # Create job listing with real URL
                    job = JobListing(
                        title=title,
                        company=company,
                        location=location,
                        description=description,
                        url=job_url,
                        job_type="Remote",
                        experience="Not specified"
                    )
                    jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing job from {site_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing {site_name}: {e}")
            
        return jobs
    
    def _parse_weworkremotely_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from WeWorkRemotely"""
        jobs = []
        
        try:
            # WeWorkRemotely job containers
            job_containers = soup.find_all(['li'], class_=re.compile('feature|jobs'))
            
            for container in job_containers[:10]:
                try:
                    title_elem = container.find(['span'], class_='title')
                    company_elem = container.find(['span'], class_='company')
                    
                    if title_elem and company_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        
                        job = JobListing(
                            title=title,
                            company=company,
                            location="Remote",
                            description=f"Remote job at {company}: {title}",
                            url=f"https://weworkremotely.com/remote-jobs/{title.lower().replace(' ', '-')}",
                            job_type="Remote",
                            experience="Not specified"
                        )
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing job from {site_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing {site_name}: {e}")
            
        return jobs
    
    def _parse_jobsdb_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from JobsDB"""
        jobs = []
        
        try:
            # JobsDB job containers
            job_containers = soup.find_all(['div'], class_=re.compile('job-item|position'))
            
            for container in job_containers[:10]:
                try:
                    title_elem = container.find(['h3', 'a'], class_=re.compile('job-title|title'))
                    company_elem = container.find(['span', 'div'], class_=re.compile('company|employer'))
                    location_elem = container.find(['span', 'div'], class_=re.compile('location|city'))
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        location = location_elem.get_text(strip=True) if location_elem else "Location not specified"
                        
                        job = JobListing(
                            title=title,
                            company=company,
                            location=location,
                            description=f"Job opportunity at {company}: {title}",
                            url=f"https://www.jobsdb.com/job/{title.lower().replace(' ', '-')}",
                            job_type="Full-time",
                            experience="Not specified"
                        )
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing job from {site_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing {site_name}: {e}")
            
        return jobs
    
    def _parse_glassdoor_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from Glassdoor"""
        jobs = []
        
        try:
            # Glassdoor job containers
            job_containers = soup.find_all(['div'], class_=re.compile('job|react-job-listing'))
            
            for container in job_containers[:10]:
                try:
                    title_elem = container.find(['a'], class_=re.compile('jobTitle|job-title'))
                    company_elem = container.find(['span'], class_=re.compile('employer|company'))
                    location_elem = container.find(['span'], class_=re.compile('location|loc'))
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        location = location_elem.get_text(strip=True) if location_elem else "Location not specified"
                        
                        job = JobListing(
                            title=title,
                            company=company,
                            location=location,
                            description=f"Position at {company}: {title}",
                            url=f"https://www.glassdoor.com/job/{title.lower().replace(' ', '-')}",
                            job_type="Full-time",
                            experience="Not specified"
                        )
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing job from {site_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing {site_name}: {e}")
            
        return jobs
    
    def _parse_angel_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from Wellfound (AngelList)"""
        jobs = []
        
        try:
            # Wellfound job containers
            job_containers = soup.find_all(['div'], class_=re.compile('job|startup|listing'))
            
            for container in job_containers[:10]:
                try:
                    title_elem = container.find(['h3', 'a'], class_=re.compile('title|job-title'))
                    company_elem = container.find(['div', 'span'], class_=re.compile('company|startup'))
                    link_elem = container.find('a', href=True)
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Startup"
                        
                        # Extract real URL if available
                        job_url = "https://wellfound.com"
                        if link_elem and link_elem.get('href'):
                            href = link_elem['href']
                            if href.startswith('/'):
                                job_url = f"https://wellfound.com{href}"
                            elif href.startswith('http'):
                                job_url = href
                        
                        job = JobListing(
                            title=title,
                            company=company,
                            location="Startup Location",
                            description=f"Startup opportunity at {company}: {title}",
                            url=job_url,
                            job_type="Full-time",
                            experience="Startup experience"
                        )
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing job from {site_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing {site_name}: {e}")
            
        return jobs
    
    def _parse_flexjobs_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from FlexJobs"""
        jobs = []
        
        try:
            # FlexJobs job containers
            job_containers = soup.find_all(['div', 'li'], class_=re.compile('job|listing|position'))
            
            for container in job_containers[:10]:
                try:
                    title_elem = container.find(['h3', 'h4', 'a'], class_=re.compile('title|job'))
                    company_elem = container.find(['span', 'div'], class_=re.compile('company|employer'))
                    link_elem = container.find('a', href=True)
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "FlexJobs Company"
                        
                        # Extract real URL if available
                        job_url = "https://www.flexjobs.com"
                        if link_elem and link_elem.get('href'):
                            href = link_elem['href']
                            if href.startswith('/'):
                                job_url = f"https://www.flexjobs.com{href}"
                            elif href.startswith('http'):
                                job_url = href
                        
                        job = JobListing(
                            title=title,
                            company=company,
                            location="Flexible Location",
                            description=f"Flexible job at {company}: {title}",
                            url=job_url,
                            job_type="Flexible",
                            experience="Flexible"
                        )
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing job from {site_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing {site_name}: {e}")
            
        return jobs
    
    def _parse_workingnomads_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from Working Nomads"""
        jobs = []
        
        try:
            # Working Nomads job containers
            job_containers = soup.find_all(['div', 'li'], class_=re.compile('job|listing'))
            
            for container in job_containers[:10]:
                try:
                    title_elem = container.find(['h3', 'h4', 'a'])
                    company_elem = container.find(['span', 'div'], class_=re.compile('company'))
                    link_elem = container.find('a', href=True)
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Remote Company"
                        
                        # Extract real URL if available
                        job_url = "https://www.workingnomads.co"
                        if link_elem and link_elem.get('href'):
                            href = link_elem['href']
                            if href.startswith('/'):
                                job_url = f"https://www.workingnomads.co{href}"
                            elif href.startswith('http'):
                                job_url = href
                        
                        job = JobListing(
                            title=title,
                            company=company,
                            location="Remote",
                            description=f"Remote nomad job at {company}: {title}",
                            url=job_url,
                            job_type="Remote",
                            experience="Remote work"
                        )
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing job from {site_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing {site_name}: {e}")
            
        return jobs
    
    def _parse_naukri_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from Naukri (disabled)"""
        return []  # Disabled due to 403 errors
    
    def _parse_linkedin_jobs(self, soup: BeautifulSoup, site_name: str) -> List[JobListing]:
        """Parse job listings from LinkedIn (disabled)"""
        return []  # Disabled due to 403 errors
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from job text using keyword matching"""
        skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'angular', 'vue.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'git', 'jenkins', 'ci/cd', 'devops',
            'machine learning', 'data science', 'ai', 'tensorflow', 'pytorch',
            'html', 'css', 'bootstrap', 'tailwind',
            'django', 'flask', 'fastapi', 'express.js',
            'php', 'laravel', 'symfony',
            'c++', 'c#', 'go', 'rust', 'scala'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def _remove_duplicates(self, jobs: List[JobListing]) -> List[JobListing]:
        """Remove duplicate job listings based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a key based on title and company (normalized)
            key = f"{job.title.lower().strip()}|{job.company.lower().strip()}"
            
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    async def test_connection(self) -> bool:
        """Test if the scraper can connect to job sites"""
        try:
            if not self.session:
                await self.initialize()
            
            # Test connection to one of the enabled sites
            test_url = 'https://remoteok.io'
            response = self.session.get(test_url, timeout=10)
            success = response.status_code == 200
            logger.info(f"Test connection to {test_url} result: {success}")
            return success
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """Check if the scraper is healthy"""
        return self.session is not None and not self.session.closed
