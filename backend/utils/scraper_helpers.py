"""
Scraper Helper Utilities
Common functions for web scraping across different job portals
"""

import re
import random
import asyncio
from datetime import datetime, timedelta
from typing import Tuple, Optional
import string


def clean_text(text: str) -> str:
    """Clean and normalize scraped text"""
    if not text:
        return ""
    
    # Remove extra whitespace and special characters
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s\-\.,()&]', '', text)
    
    return text


def extract_salary(salary_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract minimum and maximum salary from salary text
    
    Examples:
        "$60,000 - $80,000" -> (60000.0, 80000.0)
        "$75K per year" -> (75000.0, 75000.0)
        "₹5,00,000 - ₹8,00,000" -> (500000.0, 800000.0)
    """
    if not salary_text:
        return None, None
    
    # Remove currency symbols and normalize
    text = salary_text.replace(',', '').replace('₹', '').replace('$', '')
    text = re.sub(r'[^\d\s\-\.]', '', text)
    
    # Pattern for salary ranges
    range_pattern = r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)'
    range_match = re.search(range_pattern, text)
    
    if range_match:
        min_sal = float(range_match.group(1))
        max_sal = float(range_match.group(2))
        
        # Handle K notation (thousands)
        if 'k' in salary_text.lower() or 'thousand' in salary_text.lower():
            min_sal *= 1000
            max_sal *= 1000
        
        # Handle L notation (lakhs - Indian currency)
        if 'l' in salary_text.lower() or 'lakh' in salary_text.lower():
            min_sal *= 100000
            max_sal *= 100000
        
        return min_sal, max_sal
    
    # Pattern for single salary value
    single_pattern = r'(\d+(?:\.\d+)?)'
    single_match = re.search(single_pattern, text)
    
    if single_match:
        salary = float(single_match.group(1))
        
        # Handle K notation
        if 'k' in salary_text.lower() or 'thousand' in salary_text.lower():
            salary *= 1000
        
        # Handle L notation
        if 'l' in salary_text.lower() or 'lakh' in salary_text.lower():
            salary *= 100000
        
        return salary, salary
    
    return None, None


def parse_job_date(date_text: str) -> Optional[datetime]:
    """
    Parse job posting date from various text formats
    
    Examples:
        "2 days ago" -> datetime 2 days ago
        "1 week ago" -> datetime 1 week ago
        "Posted today" -> today's datetime
        "Jan 15, 2025" -> parsed datetime
    """
    if not date_text:
        return None
    
    date_text = date_text.lower().strip()
    now = datetime.utcnow()
    
    # Handle relative dates
    if 'today' in date_text or 'just posted' in date_text:
        return now
    
    if 'yesterday' in date_text:
        return now - timedelta(days=1)
    
    # Handle "X days ago" format
    days_match = re.search(r'(\d+)\s*days?\s*ago', date_text)
    if days_match:
        days = int(days_match.group(1))
        return now - timedelta(days=days)
    
    # Handle "X weeks ago" format
    weeks_match = re.search(r'(\d+)\s*weeks?\s*ago', date_text)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        return now - timedelta(weeks=weeks)
    
    # Handle "X months ago" format
    months_match = re.search(r'(\d+)\s*months?\s*ago', date_text)
    if months_match:
        months = int(months_match.group(1))
        return now - timedelta(days=months * 30)  # Approximate
    
    # Handle specific date formats
    try:
        # Try parsing common date formats
        for date_format in ['%b %d, %Y', '%B %d, %Y', '%Y-%m-%d', '%m/%d/%Y']:
            try:
                return datetime.strptime(date_text, date_format)
            except ValueError:
                continue
    except Exception:
        pass
    
    # Default to current time if parsing fails
    return now


def generate_user_agent() -> str:
    """Generate a random user agent string"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return random.choice(user_agents)


async def wait_random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Wait for a random delay between min and max seconds"""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


def extract_job_type(text: str) -> str:
    """Extract job type from job text"""
    if not text:
        return "full-time"
    
    text = text.lower()
    
    if any(term in text for term in ['part-time', 'part time', 'parttime']):
        return "part-time"
    elif any(term in text for term in ['contract', 'freelance', 'consultant']):
        return "contract"
    elif any(term in text for term in ['intern', 'internship']):
        return "internship"
    elif any(term in text for term in ['temporary', 'temp', 'seasonal']):
        return "temporary"
    else:
        return "full-time"


def extract_experience_level(text: str) -> str:
    """Extract experience level from job text"""
    if not text:
        return "entry"
    
    text = text.lower()
    
    if any(term in text for term in ['senior', 'lead', 'principal', 'architect', '5+ years', '6+ years', '7+ years']):
        return "senior"
    elif any(term in text for term in ['mid', 'intermediate', '2-5 years', '3-5 years', '2+ years', '3+ years']):
        return "mid"
    else:
        return "entry"


def extract_skills_from_text(text: str) -> list:
    """Extract technical skills from job description text"""
    if not text:
        return []
    
    # Common technical skills to look for
    skill_patterns = {
        'python': r'\bpython\b',
        'javascript': r'\bjavascript\b|\bjs\b',
        'java': r'\bjava\b(?!\s*script)',
        'react': r'\breact\b|\breactjs\b',
        'angular': r'\bangular\b',
        'vue': r'\bvue\.?js\b',
        'node': r'\bnode\.?js\b|\bnode\b',
        'sql': r'\bsql\b|\bmysql\b|\bpostgresql\b',
        'aws': r'\baws\b|\bamazon web services\b',
        'docker': r'\bdocker\b',
        'kubernetes': r'\bkubernetes\b|\bk8s\b',
        'git': r'\bgit\b|\bgithub\b|\bgitlab\b',
        'machine learning': r'\bmachine learning\b|\bml\b|\bai\b',
        'data science': r'\bdata science\b|\bdata scientist\b',
        'html': r'\bhtml\b',
        'css': r'\bcss\b',
        'mongodb': r'\bmongodb\b|\bmongo\b',
        'redis': r'\bredis\b',
        'django': r'\bdjango\b',
        'flask': r'\bflask\b',
        'fastapi': r'\bfastapi\b',
        'tensorflow': r'\btensorflow\b',
        'pytorch': r'\bpytorch\b',
        'pandas': r'\bpandas\b',
        'numpy': r'\bnumpy\b',
        'scikit-learn': r'\bscikit.learn\b|\bsklearn\b'
    }
    
    found_skills = []
    text_lower = text.lower()
    
    for skill, pattern in skill_patterns.items():
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return found_skills


def is_remote_job(text: str) -> bool:
    """Check if job allows remote work"""
    if not text:
        return False
    
    text = text.lower()
    remote_indicators = [
        'remote', 'work from home', 'wfh', 'telecommute', 
        'distributed', 'anywhere', 'home office'
    ]
    
    return any(indicator in text for indicator in remote_indicators)


def normalize_location(location: str) -> str:
    """Normalize location string"""
    if not location:
        return ""
    
    # Remove extra whitespace
    location = re.sub(r'\s+', ' ', location.strip())
    
    # Handle common location patterns
    location = re.sub(r'\+\d+\s*more', '', location)  # Remove "+2 more" type text
    location = re.sub(r'\(.*?\)', '', location)  # Remove parenthetical info
    
    return location.strip()


def generate_job_id(title: str, company: str, source: str) -> str:
    """Generate a unique job ID"""
    # Create a normalized string
    normalized = f"{title}_{company}_{source}".lower()
    normalized = re.sub(r'[^\w]', '_', normalized)
    
    # Generate hash
    import hashlib
    hash_object = hashlib.md5(normalized.encode())
    return f"{source}_{hash_object.hexdigest()[:8]}"


def validate_job_data(job_data: dict) -> bool:
    """Validate if job data contains required fields"""
    required_fields = ['title', 'company', 'source']
    
    for field in required_fields:
        if not job_data.get(field):
            return False
    
    # Additional validation
    if len(job_data.get('title', '')) < 3:
        return False
    
    if len(job_data.get('company', '')) < 2:
        return False
    
    return True


def clean_job_description(description: str) -> str:
    """Clean and format job description text"""
    if not description:
        return ""
    
    # Remove HTML tags
    description = re.sub(r'<[^>]+>', '', description)
    
    # Remove extra whitespace
    description = re.sub(r'\s+', ' ', description)
    
    # Remove common unwanted phrases
    unwanted_phrases = [
        r'apply now.*?$',
        r'click here.*?$',
        r'visit our website.*?$'
    ]
    
    for phrase in unwanted_phrases:
        description = re.sub(phrase, '', description, flags=re.IGNORECASE)
    
    return description.strip()


def extract_company_size(text: str) -> Optional[str]:
    """Extract company size information"""
    if not text:
        return None
    
    text = text.lower()
    
    if any(term in text for term in ['startup', 'early stage', '1-10', '< 10']):
        return "startup"
    elif any(term in text for term in ['small', '11-50', '10-50']):
        return "small"
    elif any(term in text for term in ['medium', '51-200', '50-200']):
        return "medium"
    elif any(term in text for term in ['large', '201-1000', '200-1000']):
        return "large"
    elif any(term in text for term in ['enterprise', '1000+', '> 1000']):
        return "enterprise"
    
    return None
