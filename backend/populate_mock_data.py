#!/usr/bin/env python3
"""
Mock Data Population Script for SkillNavigator
Populates the database with realistic job application data for demo purposes
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Database connection
DB_PATH = "skillnavigator.db"

# Mock data constants
TECH_COMPANIES = [
    "Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix", "Tesla", "Uber",
    "Airbnb", "Spotify", "Slack", "Zoom", "Shopify", "Stripe", "Square", "PayPal",
    "Adobe", "Salesforce", "Oracle", "IBM", "Intel", "NVIDIA", "AMD", "Cisco",
    "VMware", "Red Hat", "MongoDB", "Atlassian", "GitLab", "GitHub", "Docker",
    "Kubernetes Inc", "Databricks", "Snowflake", "Palantir", "Twilio", "SendGrid",
    "Cloudflare", "DigitalOcean", "Linode", "Heroku", "Vercel", "Netlify"
]

JOB_TITLES = [
    "Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "DevOps Engineer", "Site Reliability Engineer", "Data Scientist", "Data Engineer",
    "Machine Learning Engineer", "AI Engineer", "Product Manager", "Technical Lead",
    "Senior Software Engineer", "Principal Engineer", "Engineering Manager", "CTO",
    "QA Engineer", "Test Automation Engineer", "Security Engineer", "Cloud Engineer",
    "Mobile Developer", "iOS Developer", "Android Developer", "React Developer",
    "Python Developer", "Java Developer", "Node.js Developer", "Go Developer",
    "Rust Developer", "C++ Developer", "JavaScript Developer", "TypeScript Developer",
    "UI/UX Designer", "Product Designer", "Technical Writer", "Solutions Architect",
    "Database Administrator", "Network Engineer", "System Administrator", "Platform Engineer"
]

SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Django", "Flask",
    "Express.js", "Vue.js", "Angular", "Svelte", "Next.js", "Nuxt.js", "Gatsby",
    "Java", "Spring Boot", "Go", "Rust", "C++", "C#", ".NET", "PHP", "Laravel",
    "Ruby", "Ruby on Rails", "Swift", "Kotlin", "Dart", "Flutter", "React Native",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "Ansible", "Jenkins",
    "GitLab CI", "GitHub Actions", "CircleCI", "PostgreSQL", "MySQL", "MongoDB",
    "Redis", "Elasticsearch", "Kafka", "RabbitMQ", "GraphQL", "REST APIs", "gRPC",
    "Microservices", "Machine Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy",
    "Scikit-learn", "Git", "Linux", "Bash", "PowerShell", "Nginx", "Apache",
    "Prometheus", "Grafana", "ELK Stack", "Splunk", "Figma", "Adobe XD", "Sketch"
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA",
    "Los Angeles, CA", "Chicago, IL", "Denver, CO", "Atlanta, GA", "Miami, FL",
    "Portland, OR", "San Diego, CA", "Phoenix, AZ", "Dallas, TX", "Houston, TX",
    "Remote", "Remote (US)", "Remote (Global)", "Hybrid - San Francisco",
    "Hybrid - New York", "Hybrid - Seattle", "Hybrid - Austin", "Hybrid - Boston"
]

EXPERIENCE_LEVELS = ["entry", "mid", "senior", "staff", "principal"]
JOB_TYPES = ["full-time", "part-time", "contract", "internship"]
APPLICATION_STATUSES = ["applied", "interview", "rejected", "accepted", "pending"]
SOURCES = ["linkedin", "indeed", "glassdoor", "stackoverflow", "angel.co", "hired.com"]

def create_user_data():
    """Create a realistic user profile"""
    user_skills = random.sample(SKILLS, random.randint(8, 15))
    preferences = {
        "remote_work": random.choice([True, False]),
        "salary_min": random.randint(80000, 120000),
        "preferred_locations": random.sample(LOCATIONS[:15], random.randint(3, 6)),
        "job_types": random.sample(JOB_TYPES, random.randint(1, 3)),
        "company_size": random.choice(["startup", "mid-size", "large", "any"])
    }
    
    return {
        "email": "demo@skillnavigator.com",
        "name": "Alex Johnson",
        "skills": json.dumps(user_skills),
        "preferences": json.dumps(preferences),
        "location": "San Francisco, CA",
        "experience_years": random.randint(3, 8),
        "resume_path": "/uploads/alex_johnson_resume.pdf"
    }

def create_job_data():
    """Create realistic job listing data"""
    title = random.choice(JOB_TITLES)
    company = random.choice(TECH_COMPANIES)
    location = random.choice(LOCATIONS)
    
    # Create realistic salary ranges based on role level
    base_salary = 70000
    if "Senior" in title or "Lead" in title:
        base_salary = 120000
    elif "Principal" in title or "Staff" in title:
        base_salary = 160000
    elif "Manager" in title or "CTO" in title:
        base_salary = 180000
    
    salary_min = base_salary + random.randint(-20000, 10000)
    salary_max = salary_min + random.randint(20000, 60000)
    
    # Create job description
    job_skills = random.sample(SKILLS, random.randint(5, 12))
    requirements = f"Required: {', '.join(job_skills[:5])}\nPreferred: {', '.join(job_skills[5:])}"
    
    description = f"""
We are seeking a talented {title} to join our {company} team. This role offers an exciting opportunity to work with cutting-edge technology and contribute to innovative projects.

Key Responsibilities:
• Develop and maintain high-quality software applications
• Collaborate with cross-functional teams to deliver exceptional products
• Participate in code reviews and maintain coding standards
• Contribute to architectural decisions and technical strategy

Requirements:
{requirements}

We offer competitive compensation, comprehensive benefits, and a collaborative work environment.
    """.strip()
    
    posted_date = fake.date_time_between(start_date='-30d', end_date='now')
    
    return {
        "external_id": f"{company.lower().replace(' ', '')}-{fake.uuid4()[:8]}",
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "requirements": requirements,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "job_type": random.choice(JOB_TYPES),
        "experience_level": random.choice(EXPERIENCE_LEVELS),
        "remote_allowed": "Remote" in location or random.choice([True, False]),
        "apply_url": f"https://{company.lower().replace(' ', '')}.com/careers/{fake.uuid4()[:8]}",
        "posted_date": posted_date.isoformat(),
        "source": random.choice(SOURCES),
        "relevance_score": round(random.uniform(0.6, 0.95), 2),
        "skills_match": json.dumps(random.sample(job_skills, min(random.randint(3, 7), len(job_skills))))
    }

def create_application_data(user_id, job_id, job_title, company):
    """Create job application data"""
    status = random.choice(APPLICATION_STATUSES)
    applied_date = fake.date_time_between(start_date='-60d', end_date='now')
    
    # Create a realistic cover letter
    cover_letter = f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. With my background in software development and passion for technology, I am excited about the opportunity to contribute to your team.

My experience includes working with modern technologies and frameworks, and I have successfully delivered several projects that demonstrate my technical skills and problem-solving abilities. I am particularly drawn to {company}'s innovative approach and would love to be part of your mission.

I have attached my resume for your review and would welcome the opportunity to discuss how my skills and enthusiasm can contribute to your team's success.

Thank you for your consideration.

Best regards,
Alex Johnson
    """.strip()
    
    # Set follow-up and interview dates based on status
    follow_up_date = None
    interview_date = None
    last_updated = applied_date
    
    if status == "interview":
        interview_date = applied_date + timedelta(days=random.randint(7, 21))
        last_updated = interview_date - timedelta(days=random.randint(1, 5))
    elif status in ["rejected", "accepted"]:
        last_updated = applied_date + timedelta(days=random.randint(7, 30))
    elif status == "applied":
        if random.choice([True, False]):
            follow_up_date = applied_date + timedelta(days=random.randint(10, 20))
    
    return {
        "user_id": user_id,
        "job_id": job_id,
        "applied_at": applied_date.isoformat(),
        "status": status,
        "cover_letter": cover_letter,
        "notes": f"Applied through {random.choice(SOURCES)}. {random.choice(['Good fit for my skills', 'Interesting company culture', 'Great growth opportunity', 'Competitive salary', 'Remote work available'])}",
        "auto_applied": random.choice([True, False]),
        "application_method": random.choice(["form", "email", "api"]),
        "last_updated": last_updated.isoformat() if last_updated else None,
        "follow_up_date": follow_up_date.isoformat() if follow_up_date else None,
        "interview_date": interview_date.isoformat() if interview_date else None
    }

def create_scraping_log():
    """Create scraping log entry"""
    started = fake.date_time_between(start_date='-7d', end_date='now')
    completed = started + timedelta(minutes=random.randint(5, 45))
    jobs_found = random.randint(50, 500)
    jobs_saved = random.randint(int(jobs_found * 0.3), int(jobs_found * 0.8))
    
    return {
        "source": random.choice(SOURCES),
        "search_query": f"{random.choice(JOB_TITLES)} {random.choice(LOCATIONS[:10])}",
        "jobs_found": jobs_found,
        "jobs_saved": jobs_saved,
        "started_at": started.isoformat(),
        "completed_at": completed.isoformat(),
        "status": "completed"
    }

def create_system_log():
    """Create system log entry"""
    agents = ["scraper", "autoapply", "analyzer", "matcher", "notifier"]
    actions = ["job_scrape", "application_submit", "skill_analysis", "job_match", "email_sent"]
    levels = ["info", "warning", "error", "debug"]
    
    return {
        "agent_name": random.choice(agents),
        "action": random.choice(actions),
        "message": fake.sentence(),
        "level": random.choice(levels),
        "timestamp": fake.date_time_between(start_date='-7d', end_date='now').isoformat(),
        "metadata": json.dumps({"request_id": fake.uuid4(), "duration_ms": random.randint(100, 5000)})
    }

def populate_database():
    """Main function to populate database with mock data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🗄️ Starting database population with mock data...")
    
    # Clear existing data
    print("🧹 Clearing existing data...")
    cursor.execute("DELETE FROM system_logs")
    cursor.execute("DELETE FROM scraping_logs")
    cursor.execute("DELETE FROM job_applications")
    cursor.execute("DELETE FROM jobs")
    cursor.execute("DELETE FROM users")
    
    # Create user
    print("👤 Creating user profile...")
    user_data = create_user_data()
    cursor.execute("""
        INSERT INTO users (email, name, skills, preferences, location, experience_years, resume_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_data["email"], user_data["name"], user_data["skills"], 
          user_data["preferences"], user_data["location"], 
          user_data["experience_years"], user_data["resume_path"]))
    
    user_id = cursor.lastrowid
    
    # Create jobs
    print("💼 Creating job listings...")
    job_ids = []
    for i in range(150):  # Create 150 jobs
        job_data = create_job_data()
        cursor.execute("""
            INSERT INTO jobs (external_id, title, company, location, description, requirements,
                            salary_min, salary_max, job_type, experience_level, remote_allowed,
                            apply_url, posted_date, source, relevance_score, skills_match)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (job_data["external_id"], job_data["title"], job_data["company"],
              job_data["location"], job_data["description"], job_data["requirements"],
              job_data["salary_min"], job_data["salary_max"], job_data["job_type"],
              job_data["experience_level"], job_data["remote_allowed"],
              job_data["apply_url"], job_data["posted_date"], job_data["source"],
              job_data["relevance_score"], job_data["skills_match"]))
        
        job_ids.append(cursor.lastrowid)
    
    # Create applications for a subset of jobs
    print("📝 Creating job applications...")
    applied_jobs = random.sample(job_ids, 25)  # Apply to 25 jobs
    
    for job_id in applied_jobs:
        # Get job details for realistic application
        cursor.execute("SELECT title, company FROM jobs WHERE id = ?", (job_id,))
        job_title, company = cursor.fetchone()
        
        app_data = create_application_data(user_id, job_id, job_title, company)
        cursor.execute("""
            INSERT INTO job_applications (user_id, job_id, applied_at, status, cover_letter,
                                        notes, auto_applied, application_method, last_updated,
                                        follow_up_date, interview_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (app_data["user_id"], app_data["job_id"], app_data["applied_at"],
              app_data["status"], app_data["cover_letter"], app_data["notes"],
              app_data["auto_applied"], app_data["application_method"],
              app_data["last_updated"], app_data["follow_up_date"], app_data["interview_date"]))
    
    # Create scraping logs
    print("🕷️ Creating scraping logs...")
    for i in range(20):
        log_data = create_scraping_log()
        cursor.execute("""
            INSERT INTO scraping_logs (source, search_query, jobs_found, jobs_saved,
                                     started_at, completed_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (log_data["source"], log_data["search_query"], log_data["jobs_found"],
              log_data["jobs_saved"], log_data["started_at"], log_data["completed_at"],
              log_data["status"]))
    
    # Create system logs
    print("📋 Creating system logs...")
    for i in range(100):
        log_data = create_system_log()
        cursor.execute("""
            INSERT INTO system_logs (agent_name, action, message, level, timestamp, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (log_data["agent_name"], log_data["action"], log_data["message"],
              log_data["level"], log_data["timestamp"], log_data["metadata"]))
    
    conn.commit()
    conn.close()
    
    print("✅ Database populated successfully!")
    print(f"📊 Created:")
    print(f"   • 1 user profile")
    print(f"   • 150 job listings")
    print(f"   • 25 job applications")
    print(f"   • 20 scraping logs")
    print(f"   • 100 system logs")
    print("\n🎉 Your SkillNavigator dashboard is now ready with realistic demo data!")

if __name__ == "__main__":
    # Install faker if not already installed
    try:
        from faker import Faker
    except ImportError:
        print("Installing faker library...")
        import subprocess
        subprocess.check_call(["pip", "install", "faker"])
        from faker import Faker
    
    populate_database()
