#!/usr/bin/env python3
"""
Add Mock Application Data for Dashboard
Adds realistic job application data to populate dashboard statistics
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Database connection
DB_PATH = "skillnavigator.db"

def add_mock_applications():
    """Add realistic application data for dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📊 Adding mock application data for dashboard...")
    
    # Get the existing user ID
    cursor.execute("SELECT id FROM users LIMIT 1")
    result = cursor.fetchone()
    if not result:
        print("❌ No user found in database!")
        return
    
    user_id = result[0]
    
    # Get some job IDs to apply to
    cursor.execute("SELECT id, title, company FROM jobs ORDER BY RANDOM() LIMIT 35")
    jobs = cursor.fetchall()
    
    if not jobs:
        print("❌ No jobs found in database!")
        return
    
    # Delete existing applications first
    cursor.execute("DELETE FROM job_applications WHERE user_id = ?", (user_id,))
    
    application_statuses = {
        'applied': 15,      # 15 applications still pending
        'interview': 6,     # 6 interviews scheduled
        'rejected': 8,      # 8 rejections
        'accepted': 2,      # 2 job offers!
        'pending': 4        # 4 pending reviews
    }
    
    applications_created = 0
    
    for status, count in application_statuses.items():
        for i in range(count):
            if applications_created >= len(jobs):
                break
                
            job_id, job_title, company = jobs[applications_created]
            
            # Create realistic application dates (last 60 days)
            applied_date = fake.date_time_between(start_date='-60d', end_date='now')
            
            # Set interview/follow-up dates based on status
            interview_date = None
            follow_up_date = None
            last_updated = applied_date
            
            if status == 'interview':
                interview_date = applied_date + timedelta(days=random.randint(5, 15))
                last_updated = interview_date - timedelta(days=random.randint(1, 3))
            elif status in ['rejected', 'accepted']:
                last_updated = applied_date + timedelta(days=random.randint(7, 25))
            elif status == 'pending':
                follow_up_date = applied_date + timedelta(days=random.randint(7, 14))
            
            # Create cover letter
            cover_letter = f"""Dear {company} Hiring Team,

I am excited to apply for the {job_title} position at {company}. With my background in software development and passion for technology, I believe I would be a valuable addition to your team.

My experience with modern development frameworks and collaborative work environments aligns well with your requirements. I am particularly drawn to {company}'s innovative approach and would love to contribute to your continued success.

I have attached my resume and would welcome the opportunity to discuss how my skills can benefit your team.

Best regards,
Alex Johnson"""
            
            notes = random.choice([
                f"Applied through company website. Really excited about {company}!",
                f"Found this role through LinkedIn. Great match for my skills.",
                f"Referred by a friend who works at {company}.",
                f"Company culture looks amazing. Perfect remote setup.",
                f"Competitive salary and benefits package.",
                f"Love the tech stack they're using.",
                f"Growth opportunities look excellent here."
            ])
            
            cursor.execute("""
                INSERT INTO job_applications 
                (user_id, job_id, applied_at, status, cover_letter, notes, auto_applied, 
                 application_method, last_updated, follow_up_date, interview_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, job_id, applied_date.isoformat(), status, cover_letter, notes,
                random.choice([True, False]), random.choice(['form', 'email', 'api']),
                last_updated.isoformat(),
                follow_up_date.isoformat() if follow_up_date else None,
                interview_date.isoformat() if interview_date else None
            ))
            
            applications_created += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {applications_created} mock applications!")
    print(f"📊 Dashboard will now show:")
    for status, count in application_statuses.items():
        if status == 'applied':
            print(f"   • {count} Total Applications")
        elif status == 'pending':
            print(f"   • {count} Pending Reviews")
        elif status == 'interview':
            print(f"   • {count} Interviews Scheduled")
        elif status == 'accepted':
            success_rate = round((count / sum(application_statuses.values())) * 100, 1)
            print(f"   • {success_rate}% Success Rate ({count} offers)")

if __name__ == "__main__":
    add_mock_applications()
