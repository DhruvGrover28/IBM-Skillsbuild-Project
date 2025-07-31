"""
Matching Utilities
Functions for feature extraction and matching algorithms
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


def extract_features_from_job(job) -> Dict:
    """Extract features from a job object for matching"""
    
    # Handle both SQLAlchemy objects and dictionaries
    if hasattr(job, '__dict__'):
        # SQLAlchemy object
        job_data = {
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'description': job.description,
            'requirements': job.requirements,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'job_type': job.job_type,
            'experience_level': job.experience_level,
            'remote_allowed': job.remote_allowed
        }
    else:
        # Dictionary
        job_data = job
    
    # Extract required skills from description and requirements
    required_skills = extract_skills_from_job_text(
        f"{job_data.get('description', '')} {job_data.get('requirements', '')}"
    )
    
    # Extract benefits and perks
    benefits = extract_benefits_from_text(job_data.get('description', ''))
    
    # Extract company size indicators
    company_size = extract_company_size_from_text(job_data.get('description', ''))
    
    return {
        'title': job_data.get('title', ''),
        'company': job_data.get('company', ''),
        'location': job_data.get('location', ''),
        'description': job_data.get('description', ''),
        'requirements': job_data.get('requirements', ''),
        'salary_min': job_data.get('salary_min', 0),
        'salary_max': job_data.get('salary_max', 0),
        'job_type': job_data.get('job_type', 'full-time'),
        'experience_level': job_data.get('experience_level', 'entry'),
        'remote_allowed': job_data.get('remote_allowed', False),
        'required_skills': required_skills,
        'benefits': benefits,
        'company_size': company_size
    }


def extract_features_from_profile(profile: Dict) -> Dict:
    """Extract features from user profile for matching"""
    
    # Get skills from profile
    skills = profile.get('skills', [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',')]
    
    # Extract preferences
    preferences = profile.get('preferences', {})
    if isinstance(preferences, str):
        import json
        try:
            preferences = json.loads(preferences)
        except:
            preferences = {}
    
    return {
        'skills': skills,
        'experience_years': profile.get('experience_years', 0),
        'location': profile.get('location', ''),
        'preferred_locations': preferences.get('preferred_locations', []),
        'job_types': preferences.get('job_types', ['full-time']),
        'experience_levels': preferences.get('experience_levels', ['entry']),
        'salary_min': preferences.get('salary_min', 0),
        'salary_max': preferences.get('salary_max', float('inf')),
        'preferred_companies': preferences.get('preferred_companies', []),
        'avoided_companies': preferences.get('avoided_companies', []),
        'remote_preference': preferences.get('remote_preference', False),
        'interests': preferences.get('interests', []),
        'experience_summary': profile.get('experience_summary', '')
    }


def extract_skills_from_job_text(text: str) -> List[str]:
    """Extract technical skills from job description/requirements text"""
    if not text:
        return []
    
    text = text.lower()
    
    # Comprehensive skill patterns with variations
    skill_patterns = {
        # Programming Languages
        'python': [r'\bpython\b', r'\bpy\b(?!\s*test)'],
        'javascript': [r'\bjavascript\b', r'\bjs\b(?!\s*\w)', r'\bnode\.?js\b'],
        'java': [r'\bjava\b(?!\s*script)', r'\bjdk\b', r'\bjre\b'],
        'typescript': [r'\btypescript\b', r'\bts\b(?!\s*\w)'],
        'c++': [r'\bc\+\+\b', r'\bcpp\b'],
        'c#': [r'\bc#\b', r'\bc sharp\b', r'\b\.net\b'],
        'go': [r'\bgolang\b', r'\bgo\b(?:\s+language|\s+programming)'],
        'rust': [r'\brust\b(?:\s+language|\s+programming)'],
        'php': [r'\bphp\b'],
        'ruby': [r'\bruby\b(?:\s+on\s+rails|\s+programming)'],
        'swift': [r'\bswift\b(?:\s+programming|\s+language)'],
        'kotlin': [r'\bkotlin\b'],
        'scala': [r'\bscala\b'],
        'r': [r'\br\s+programming\b', r'\br\s+language\b'],
        
        # Web Technologies
        'html': [r'\bhtml\b', r'\bhtml5\b'],
        'css': [r'\bcss\b', r'\bcss3\b'],
        'react': [r'\breact\b', r'\breactjs\b', r'\breact\.js\b'],
        'angular': [r'\bangular\b', r'\bangularjs\b'],
        'vue': [r'\bvue\b', r'\bvue\.js\b', r'\bvuejs\b'],
        'svelte': [r'\bsvelte\b'],
        'jquery': [r'\bjquery\b'],
        'bootstrap': [r'\bbootstrap\b'],
        'tailwind': [r'\btailwind\b', r'\btailwindcss\b'],
        
        # Backend Frameworks
        'django': [r'\bdjango\b'],
        'flask': [r'\bflask\b'],
        'fastapi': [r'\bfastapi\b'],
        'express': [r'\bexpress\b', r'\bexpress\.js\b'],
        'spring': [r'\bspring\b(?:\s+boot|\s+framework)'],
        'laravel': [r'\blaravel\b'],
        'rails': [r'\bruby\s+on\s+rails\b', r'\brails\b'],
        
        # Databases
        'sql': [r'\bsql\b', r'\bstructured\s+query\s+language\b'],
        'mysql': [r'\bmysql\b'],
        'postgresql': [r'\bpostgresql\b', r'\bpostgres\b'],
        'mongodb': [r'\bmongodb\b', r'\bmongo\b'],
        'redis': [r'\bredis\b'],
        'elasticsearch': [r'\belasticsearch\b'],
        'sqlite': [r'\bsqlite\b'],
        'oracle': [r'\boracle\b(?:\s+database)'],
        'cassandra': [r'\bcassandra\b'],
        
        # Cloud & DevOps
        'aws': [r'\baws\b', r'\bamazon\s+web\s+services\b'],
        'azure': [r'\bazure\b', r'\bmicrosoft\s+azure\b'],
        'gcp': [r'\bgcp\b', r'\bgoogle\s+cloud\b'],
        'docker': [r'\bdocker\b'],
        'kubernetes': [r'\bkubernetes\b', r'\bk8s\b'],
        'jenkins': [r'\bjenkins\b'],
        'gitlab': [r'\bgitlab\b'],
        'github': [r'\bgithub\b'],
        'git': [r'\bgit\b(?!\s*hub)'],
        'terraform': [r'\bterraform\b'],
        'ansible': [r'\bansible\b'],
        
        # Data Science & ML
        'machine learning': [r'\bmachine\s+learning\b', r'\bml\b(?:\s+engineer|\s+models)'],
        'deep learning': [r'\bdeep\s+learning\b', r'\bdl\b(?:\s+models)'],
        'artificial intelligence': [r'\bartificial\s+intelligence\b', r'\bai\b(?:\s+engineer|\s+models)'],
        'data science': [r'\bdata\s+science\b', r'\bdata\s+scientist\b'],
        'pandas': [r'\bpandas\b'],
        'numpy': [r'\bnumpy\b'],
        'scikit-learn': [r'\bscikit.learn\b', r'\bsklearn\b'],
        'tensorflow': [r'\btensorflow\b'],
        'pytorch': [r'\bpytorch\b'],
        'keras': [r'\bkeras\b'],
        'matplotlib': [r'\bmatplotlib\b'],
        'seaborn': [r'\bseaborn\b'],
        'jupyter': [r'\bjupyter\b'],
        
        # Testing
        'pytest': [r'\bpytest\b'],
        'jest': [r'\bjest\b'],
        'selenium': [r'\bselenium\b'],
        'cypress': [r'\bcypress\b'],
        'unit testing': [r'\bunit\s+test\b', r'\bunittest\b'],
        
        # Other Technologies
        'graphql': [r'\bgraphql\b'],
        'rest api': [r'\brest\b', r'\brestful\b', r'\brest\s+api\b'],
        'microservices': [r'\bmicroservices\b'],
        'linux': [r'\blinux\b', r'\bunix\b'],
        'bash': [r'\bbash\b', r'\bshell\s+script\b'],
        'agile': [r'\bagile\b', r'\bscrum\b'],
        'jira': [r'\bjira\b'],
        'confluence': [r'\bconfluence\b']
    }
    
    found_skills = []
    
    for skill, patterns in skill_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text):
                found_skills.append(skill)
                break  # Found this skill, move to next
    
    return list(set(found_skills))  # Remove duplicates


def extract_benefits_from_text(text: str) -> List[str]:
    """Extract benefits and perks from job description"""
    if not text:
        return []
    
    text = text.lower()
    
    benefit_patterns = {
        'health insurance': [r'\bhealth\s+insurance\b', r'\bmedical\s+coverage\b'],
        'dental insurance': [r'\bdental\s+insurance\b', r'\bdental\s+coverage\b'],
        'vision insurance': [r'\bvision\s+insurance\b', r'\bvision\s+coverage\b'],
        'retirement plan': [r'\b401k\b', r'\bretirement\s+plan\b', r'\bpension\b'],
        'paid time off': [r'\bpto\b', r'\bpaid\s+time\s+off\b', r'\bvacation\s+days\b'],
        'flexible hours': [r'\bflexible\s+hours\b', r'\bflexible\s+schedule\b'],
        'remote work': [r'\bremote\s+work\b', r'\bwork\s+from\s+home\b', r'\bwfh\b'],
        'stock options': [r'\bstock\s+options\b', r'\bequity\b', r'\brsus\b'],
        'bonus': [r'\bbonus\b', r'\bperformance\s+bonus\b'],
        'gym membership': [r'\bgym\s+membership\b', r'\bfitness\s+center\b'],
        'food allowance': [r'\bfree\s+food\b', r'\bmeals\s+provided\b', r'\bfood\s+allowance\b'],
        'learning budget': [r'\blearning\s+budget\b', r'\btraining\s+budget\b', r'\bprofessional\s+development\b'],
        'conference attendance': [r'\bconference\s+attendance\b', r'\btech\s+conferences\b']
    }
    
    found_benefits = []
    
    for benefit, patterns in benefit_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text):
                found_benefits.append(benefit)
                break
    
    return found_benefits


def extract_company_size_from_text(text: str) -> Optional[str]:
    """Extract company size information from job description"""
    if not text:
        return None
    
    text = text.lower()
    
    size_patterns = {
        'startup': [r'\bstartup\b', r'\bearly\s+stage\b', r'\b1-10\s+employees\b'],
        'small': [r'\bsmall\s+company\b', r'\b11-50\s+employees\b', r'\b10-50\s+employees\b'],
        'medium': [r'\bmedium\s+company\b', r'\b51-200\s+employees\b', r'\b50-200\s+employees\b'],
        'large': [r'\blarge\s+company\b', r'\b201-1000\s+employees\b', r'\b200-1000\s+employees\b'],
        'enterprise': [r'\benterprise\b', r'\b1000\+\s+employees\b', r'\bfortune\s+500\b']
    }
    
    for size, patterns in size_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return size
    
    return None


def calculate_skill_match(user_skills: List[str], required_skills: List[str]) -> Dict:
    """Calculate detailed skill match information"""
    user_skills_lower = [skill.lower() for skill in user_skills]
    required_skills_lower = [skill.lower() for skill in required_skills]
    
    exact_matches = []
    partial_matches = []
    missing_skills = []
    
    # Find exact matches
    for req_skill in required_skills:
        req_skill_lower = req_skill.lower()
        if req_skill_lower in user_skills_lower:
            exact_matches.append(req_skill)
        else:
            # Check for partial matches
            partial_match = find_partial_skill_match(req_skill_lower, user_skills_lower)
            if partial_match:
                partial_matches.append({
                    'required_skill': req_skill,
                    'user_skill': partial_match,
                    'confidence': 0.7
                })
            else:
                missing_skills.append(req_skill)
    
    # Calculate match percentage
    total_required = len(required_skills) if required_skills else 1
    exact_weight = 1.0
    partial_weight = 0.5
    
    match_score = (len(exact_matches) * exact_weight + len(partial_matches) * partial_weight) / total_required
    match_percentage = min(100, match_score * 100)
    
    return {
        'exact_matches': exact_matches,
        'partial_matches': partial_matches,
        'missing_skills': missing_skills,
        'match_percentage': match_percentage,
        'total_required': total_required
    }


def find_partial_skill_match(required_skill: str, user_skills: List[str]) -> Optional[str]:
    """Find partial matches between required skill and user skills"""
    
    # Skill relationship mappings
    skill_relationships = {
        'javascript': ['js', 'node.js', 'nodejs', 'react', 'angular', 'vue'],
        'python': ['django', 'flask', 'fastapi', 'pandas', 'numpy'],
        'java': ['spring', 'hibernate', 'maven', 'gradle'],
        'react': ['javascript', 'js', 'jsx', 'redux'],
        'angular': ['javascript', 'typescript', 'rxjs'],
        'vue': ['javascript', 'vuex', 'nuxt'],
        'sql': ['mysql', 'postgresql', 'sqlite', 'oracle'],
        'aws': ['ec2', 's3', 'lambda', 'cloudformation'],
        'machine learning': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'pandas', 'numpy'],
        'data science': ['python', 'r', 'pandas', 'numpy', 'matplotlib', 'jupyter']
    }
    
    # Check if required skill is related to any user skill
    for user_skill in user_skills:
        user_skill_lower = user_skill.lower()
        
        # Direct relationship check
        if required_skill in skill_relationships.get(user_skill_lower, []):
            return user_skill
        
        if user_skill_lower in skill_relationships.get(required_skill, []):
            return user_skill
        
        # Substring matching for similar technologies
        if len(required_skill) > 3 and len(user_skill_lower) > 3:
            if required_skill in user_skill_lower or user_skill_lower in required_skill:
                return user_skill
    
    return None


def normalize_score(score: float) -> float:
    """Normalize score to 0-1 range with smoothing"""
    if score < 0:
        return 0.0
    elif score > 1:
        return 1.0
    else:
        # Apply slight smoothing to avoid extreme scores
        return round(score, 3)


def calculate_location_similarity(location1: str, location2: str) -> float:
    """Calculate similarity between two location strings"""
    if not location1 or not location2:
        return 0.0
    
    loc1 = location1.lower().strip()
    loc2 = location2.lower().strip()
    
    # Exact match
    if loc1 == loc2:
        return 1.0
    
    # Check if one contains the other
    if loc1 in loc2 or loc2 in loc1:
        return 0.8
    
    # Split by common separators and check parts
    separators = [',', '-', '/', '|']
    for sep in separators:
        if sep in loc1 and sep in loc2:
            parts1 = [part.strip() for part in loc1.split(sep)]
            parts2 = [part.strip() for part in loc2.split(sep)]
            
            # Check for any matching parts
            for part1 in parts1:
                for part2 in parts2:
                    if part1 == part2 and len(part1) > 2:
                        return 0.6
    
    return 0.0


def extract_education_requirements(text: str) -> List[str]:
    """Extract education requirements from job description"""
    if not text:
        return []
    
    text = text.lower()
    
    education_patterns = {
        "bachelor's degree": [r"\bbachelor'?s?\s+degree\b", r"\bb\.?s\.?\b", r"\bundergraduate\s+degree\b"],
        "master's degree": [r"\bmaster'?s?\s+degree\b", r"\bm\.?s\.?\b", r"\bgraduate\s+degree\b"],
        "phd": [r"\bphd\b", r"\bdoctorate\b", r"\bdoctoral\s+degree\b"],
        "computer science": [r"\bcomputer\s+science\b", r"\bcs\s+degree\b"],
        "engineering": [r"\bengineering\s+degree\b", r"\bengineering\b"],
        "mathematics": [r"\bmathematics\b", r"\bmath\s+degree\b"],
        "statistics": [r"\bstatistics\b", r"\bstats\s+degree\b"]
    }
    
    found_requirements = []
    
    for requirement, patterns in education_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text):
                found_requirements.append(requirement)
                break
    
    return found_requirements


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate basic text similarity using word overlap"""
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0
