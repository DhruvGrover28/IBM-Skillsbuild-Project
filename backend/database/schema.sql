-- SkillNavigator Database Schema
-- SQLite database structure for the AI-powered job application platform

-- Users table - stores user profiles and preferences
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Profile data
    resume_path VARCHAR(500),
    skills TEXT, -- JSON string of skills array
    preferences TEXT, -- JSON string of user preferences
    location VARCHAR(255),
    experience_years INTEGER DEFAULT 0
);

-- Jobs table - stores scraped job listings
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id VARCHAR(255) UNIQUE, -- ID from job portal
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    requirements TEXT,
    salary_min REAL,
    salary_max REAL,
    job_type VARCHAR(50), -- full-time, part-time, contract
    experience_level VARCHAR(50), -- entry, mid, senior
    remote_allowed BOOLEAN DEFAULT 0,
    apply_url VARCHAR(1000),
    posted_date DATETIME,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) NOT NULL, -- linkedin, indeed, etc.
    
    -- AI scoring
    relevance_score REAL,
    skills_match TEXT -- JSON string of matched skills
);

-- Job applications table - tracks application status
CREATE TABLE IF NOT EXISTS job_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    
    -- Application details
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'applied', -- applied, interview, rejected, accepted
    cover_letter TEXT,
    notes TEXT,
    
    -- Auto-application details
    auto_applied BOOLEAN DEFAULT 0,
    application_method VARCHAR(50), -- email, form, api
    
    -- Follow-up tracking
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    follow_up_date DATETIME,
    interview_date DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Scraping logs table - tracks scraping activities
CREATE TABLE IF NOT EXISTS scraping_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(50) NOT NULL, -- linkedin, indeed, etc.
    search_query VARCHAR(500) NOT NULL,
    jobs_found INTEGER DEFAULT 0,
    jobs_saved INTEGER DEFAULT 0,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    status VARCHAR(50) DEFAULT 'running', -- running, completed, failed
    error_message TEXT
);

-- System logs table - tracks agent activities
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    message TEXT,
    level VARCHAR(20) DEFAULT 'info', -- debug, info, warning, error
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT -- JSON string for additional data
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX IF NOT EXISTS idx_jobs_relevance_score ON jobs(relevance_score);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON job_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON job_applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_applied_at ON job_applications(applied_at);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_source ON scraping_logs(source);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_started_at ON scraping_logs(started_at);
CREATE INDEX IF NOT EXISTS idx_system_logs_agent ON system_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);

-- Insert default demo user for testing
INSERT OR IGNORE INTO users (
    email, 
    name, 
    skills, 
    preferences, 
    location, 
    experience_years
) VALUES (
    'demo@skillnavigator.com',
    'Demo User',
    '["Python", "JavaScript", "React", "Machine Learning", "FastAPI", "SQL"]',
    '{"preferred_locations": ["Remote", "San Francisco", "New York"], "job_types": ["full-time", "contract"], "experience_levels": ["entry", "mid"], "salary_min": 60000, "auto_apply": false, "max_applications_per_day": 5}',
    'San Francisco, CA',
    2
);

-- Insert sample job data for testing
INSERT OR IGNORE INTO jobs (
    external_id,
    title,
    company,
    location,
    description,
    requirements,
    salary_min,
    salary_max,
    job_type,
    experience_level,
    remote_allowed,
    apply_url,
    posted_date,
    source,
    relevance_score
) VALUES 
(
    'linkedin_001',
    'Junior Software Engineer',
    'TechCorp Inc.',
    'San Francisco, CA',
    'We are looking for a passionate junior software engineer to join our growing team. You will work on building scalable web applications using modern technologies.',
    'Bachelor''s degree in Computer Science or related field. Experience with Python, JavaScript, and React. Understanding of databases and API development.',
    75000,
    95000,
    'full-time',
    'entry',
    1,
    'https://linkedin.com/jobs/view/001',
    '2025-01-01 10:00:00',
    'linkedin',
    0.85
),
(
    'indeed_002',
    'Machine Learning Intern',
    'AI Innovations LLC',
    'Remote',
    'Join our ML team to work on cutting-edge AI projects. This internship offers hands-on experience with machine learning models and data analysis.',
    'Currently pursuing degree in Computer Science, Data Science, or related field. Knowledge of Python, pandas, scikit-learn. Experience with ML algorithms preferred.',
    25000,
    35000,
    'internship',
    'entry',
    1,
    'https://indeed.com/jobs/view/002',
    '2025-01-01 14:30:00',
    'indeed',
    0.92
),
(
    'internshala_003',
    'Full Stack Developer',
    'StartupXYZ',
    'New York, NY',
    'We need a full stack developer to build our next-generation platform. You''ll work with React, Node.js, and cloud technologies.',
    '1-3 years experience in web development. Proficiency in React, Node.js, JavaScript, HTML, CSS. Experience with databases and cloud platforms.',
    65000,
    85000,
    'full-time',
    'mid',
    0,
    'https://internshala.com/jobs/detail/003',
    '2024-12-31 16:45:00',
    'internshala',
    0.78
);

-- Create triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users
    FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_applications_timestamp 
    AFTER UPDATE ON job_applications
    FOR EACH ROW
BEGIN
    UPDATE job_applications SET last_updated = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
