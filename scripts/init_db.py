"""
Database initialization script for SkillNavigator
This script creates the database tables and optionally loads sample data
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = PROJECT_ROOT / "skillnavigator.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"

def create_database():
    """Create the database and tables from schema.sql"""
    print("Creating database and tables...")
    
    # Read the schema file
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Execute the schema SQL
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ Database and tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
    finally:
        conn.close()

def load_sample_users():
    """Load sample user data into the database"""
    print("Loading sample users...")
    
    with open(DATA_DIR / "user_profiles.json", 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        for user in users:
            cursor.execute("""
                INSERT OR REPLACE INTO users (
                    id, email, name, created_at, updated_at, resume_path,
                    skills, preferences, location, experience_years,
                    phone, linkedin_url, github_url, portfolio_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user["id"],
                user["email"],
                user["name"],
                user["created_at"],
                user["updated_at"],
                user.get("resume_path"),
                json.dumps(user["skills"]),
                json.dumps(user["preferences"]),
                user["location"],
                user["experience_years"],
                user.get("phone"),
                user.get("linkedin_url"),
                user.get("github_url"),
                user.get("portfolio_url")
            ))
        
        conn.commit()
        print(f"✅ Loaded {len(users)} sample users!")
    except Exception as e:
        print(f"❌ Error loading users: {e}")
        conn.rollback()
    finally:
        conn.close()

def load_sample_jobs():
    """Load sample job data into the database"""
    print("Loading sample jobs...")
    
    with open(DATA_DIR / "job_listings.json", 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        for job in jobs:
            cursor.execute("""
                INSERT OR REPLACE INTO jobs (
                    id, title, company, location, remote, salary_min, salary_max,
                    job_type, experience_level, description, requirements,
                    skills, benefits, posted_date, application_deadline,
                    status, portal, url, company_size, industry, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job["id"],
                job["title"],
                job["company"],
                job["location"],
                job["remote"],
                job.get("salary_min"),
                job.get("salary_max"),
                job["job_type"],
                job["experience_level"],
                job["description"],
                json.dumps(job["requirements"]),
                json.dumps(job["skills"]),
                json.dumps(job["benefits"]),
                job["posted_date"],
                job.get("application_deadline"),
                job["status"],
                job["portal"],
                job["url"],
                job.get("company_size"),
                job.get("industry"),
                job["scraped_at"]
            ))
        
        conn.commit()
        print(f"✅ Loaded {len(jobs)} sample jobs!")
    except Exception as e:
        print(f"❌ Error loading jobs: {e}")
        conn.rollback()
    finally:
        conn.close()

def load_sample_applications():
    """Load sample application data into the database"""
    print("Loading sample applications...")
    
    with open(DATA_DIR / "applications.json", 'r', encoding='utf-8') as f:
        applications = json.load(f)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        for app in applications:
            cursor.execute("""
                INSERT OR REPLACE INTO job_applications (
                    id, user_id, job_id, status, applied_at, updated_at,
                    cover_letter, follow_up_date, score, portal_response,
                    auto_applied, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                app["id"],
                app["user_id"],
                app["job_id"],
                app["status"],
                app.get("applied_at"),
                app["updated_at"],
                app.get("cover_letter"),
                app.get("follow_up_date"),
                app.get("score"),
                app.get("portal_response"),
                app["auto_applied"],
                app.get("notes")
            ))
        
        conn.commit()
        print(f"✅ Loaded {len(applications)} sample applications!")
    except Exception as e:
        print(f"❌ Error loading applications: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_sample_logs():
    """Create some sample system and scraping logs"""
    print("Creating sample logs...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Sample scraping logs
        scraping_logs = [
            {
                "portal": "linkedin",
                "started_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "completed_at": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
                "status": "completed",
                "jobs_found": 25,
                "jobs_saved": 22,
                "errors_count": 0,
                "duration_seconds": 900
            },
            {
                "portal": "indeed",
                "started_at": (datetime.now() - timedelta(hours=4)).isoformat(),
                "completed_at": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
                "status": "completed",
                "jobs_found": 18,
                "jobs_saved": 16,
                "errors_count": 1,
                "error_details": json.dumps(["Timeout on page 3"]),
                "duration_seconds": 1800
            },
            {
                "portal": "internshala",
                "started_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "status": "running",
                "jobs_found": 8,
                "jobs_saved": 8,
                "errors_count": 0
            }
        ]
        
        for log in scraping_logs:
            cursor.execute("""
                INSERT INTO scraping_logs (
                    portal, started_at, completed_at, status, jobs_found,
                    jobs_saved, errors_count, error_details, duration_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log["portal"],
                log["started_at"],
                log.get("completed_at"),
                log["status"],
                log["jobs_found"],
                log["jobs_saved"],
                log["errors_count"],
                log.get("error_details"),
                log.get("duration_seconds")
            ))
        
        # Sample system logs
        system_logs = [
            {
                "level": "INFO",
                "component": "supervisor_agent",
                "message": "Auto-mode workflow started",
                "details": json.dumps({"workflow_id": "auto_001", "user_count": 5}),
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                "level": "INFO",
                "component": "scoring_agent",
                "message": "Job scoring completed",
                "details": json.dumps({"jobs_scored": 43, "average_time": 2.3}),
                "user_id": 1,
                "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat()
            },
            {
                "level": "WARNING",
                "component": "autoapply_agent",
                "message": "Rate limit approached for user",
                "details": json.dumps({"applications_today": 4, "limit": 5}),
                "user_id": 2,
                "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat()
            },
            {
                "level": "ERROR",
                "component": "scraper_agent",
                "message": "Failed to load page",
                "details": json.dumps({"url": "https://example.com/jobs", "error": "Timeout"}),
                "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat()
            }
        ]
        
        for log in system_logs:
            cursor.execute("""
                INSERT INTO system_logs (
                    level, component, message, details, user_id, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                log["level"],
                log["component"],
                log["message"],
                log["details"],
                log.get("user_id"),
                log["timestamp"]
            ))
        
        conn.commit()
        print(f"✅ Created {len(scraping_logs)} scraping logs and {len(system_logs)} system logs!")
    except Exception as e:
        print(f"❌ Error creating logs: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_data():
    """Verify that data was loaded correctly"""
    print("\nVerifying loaded data...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Count records in each table
        tables = [
            "users", "jobs", "job_applications", 
            "scraping_logs", "system_logs"
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")
        
        # Test a view
        cursor.execute("SELECT COUNT(*) FROM user_application_summary")
        view_count = cursor.fetchone()[0]
        print(f"  user_application_summary view: {view_count} records")
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
    finally:
        conn.close()

def main():
    """Main initialization function"""
    print("🚀 Initializing SkillNavigator Database")
    print("=" * 50)
    
    # Check if data files exist
    required_files = [
        DATA_DIR / "user_profiles.json",
        DATA_DIR / "job_listings.json", 
        DATA_DIR / "applications.json",
        SCHEMA_PATH
    ]
    
    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return
    
    # Create database and load data
    try:
        create_database()
        load_sample_users()
        load_sample_jobs()
        load_sample_applications()
        create_sample_logs()
        verify_data()
        
        print("\n🎉 Database initialization completed successfully!")
        print(f"Database created at: {DATABASE_PATH}")
        print("\nYou can now start the SkillNavigator application.")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")

if __name__ == "__main__":
    main()
