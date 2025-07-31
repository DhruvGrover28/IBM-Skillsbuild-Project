-- SkillNavigator Database Schema
-- SQLite Database Structure for the AI-Powered Job Application Platform

-- Users table - stores user profile information
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resume_path TEXT,
    skills TEXT, -- JSON array of skills
    preferences TEXT, -- JSON object with user preferences
    location TEXT,
    experience_years INTEGER,
    phone TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP
);

-- Jobs table - stores scraped job listings
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    remote BOOLEAN DEFAULT FALSE,
    salary_min INTEGER,
    salary_max INTEGER,
    job_type TEXT, -- full-time, part-time, contract, internship
    experience_level TEXT, -- entry, mid, senior, executive
    description TEXT,
    requirements TEXT, -- JSON array of requirements
    skills TEXT, -- JSON array of required skills
    benefits TEXT, -- JSON array of benefits
    posted_date TIMESTAMP,
    application_deadline TIMESTAMP,
    status TEXT DEFAULT 'active', -- active, expired, filled, removed
    portal TEXT, -- linkedin, indeed, internshala, etc.
    url TEXT UNIQUE,
    company_size TEXT,
    industry TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job Applications table - tracks user applications
CREATE TABLE job_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT DEFAULT 'applied', -- applied, under_review, interview, offer, rejected, withdrawn, not_interested
    applied_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cover_letter TEXT,
    follow_up_date TIMESTAMP,
    score REAL, -- AI-generated relevance score (0-100)
    portal_response TEXT, -- Response from job portal
    auto_applied BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
    UNIQUE(user_id, job_id)
);

-- Scraping Logs table - tracks scraping activities
CREATE TABLE scraping_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portal TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running', -- running, completed, failed, cancelled
    jobs_found INTEGER DEFAULT 0,
    jobs_saved INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_details TEXT, -- JSON array of error messages
    filters_used TEXT, -- JSON object with applied filters
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Logs table - general system activity logs
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL, -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    component TEXT NOT NULL, -- scraper_agent, scoring_agent, etc.
    message TEXT NOT NULL,
    details TEXT, -- JSON object with additional details
    user_id INTEGER, -- Optional user context
    job_id INTEGER, -- Optional job context
    application_id INTEGER, -- Optional application context
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE SET NULL,
    FOREIGN KEY (application_id) REFERENCES job_applications (id) ON DELETE SET NULL
);

-- User Sessions table - for authentication and session management
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- API Keys table - for storing encrypted API keys and configuration
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT UNIQUE NOT NULL, -- openai, linkedin, indeed, etc.
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

-- Email Queue table - for managing email notifications
CREATE TABLE email_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    email_type TEXT NOT NULL, -- job_alert, application_update, weekly_summary, etc.
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, sent, failed, cancelled
    scheduled_for TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes for better query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_portal ON jobs(portal);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_remote ON jobs(remote);
CREATE INDEX idx_jobs_experience_level ON jobs(experience_level);
CREATE INDEX idx_job_applications_user_id ON job_applications(user_id);
CREATE INDEX idx_job_applications_job_id ON job_applications(job_id);
CREATE INDEX idx_job_applications_status ON job_applications(status);
CREATE INDEX idx_job_applications_applied_at ON job_applications(applied_at);
CREATE INDEX idx_scraping_logs_portal ON scraping_logs(portal);
CREATE INDEX idx_scraping_logs_status ON scraping_logs(status);
CREATE INDEX idx_scraping_logs_started_at ON scraping_logs(started_at);
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_component ON system_logs(component);
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active);
CREATE INDEX idx_email_queue_user_id ON email_queue(user_id);
CREATE INDEX idx_email_queue_status ON email_queue(status);
CREATE INDEX idx_email_queue_scheduled ON email_queue(scheduled_for);

-- Views for common queries

-- Active jobs view
CREATE VIEW active_jobs AS
SELECT * FROM jobs 
WHERE status = 'active' 
AND (application_deadline IS NULL OR application_deadline > CURRENT_TIMESTAMP);

-- User application summary view
CREATE VIEW user_application_summary AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    COUNT(ja.id) as total_applications,
    COUNT(CASE WHEN ja.status = 'applied' THEN 1 END) as applied_count,
    COUNT(CASE WHEN ja.status = 'under_review' THEN 1 END) as under_review_count,
    COUNT(CASE WHEN ja.status = 'interview' THEN 1 END) as interview_count,
    COUNT(CASE WHEN ja.status = 'offer' THEN 1 END) as offer_count,
    COUNT(CASE WHEN ja.status = 'rejected' THEN 1 END) as rejected_count,
    AVG(ja.score) as average_score,
    MAX(ja.applied_at) as last_application_date
FROM users u
LEFT JOIN job_applications ja ON u.id = ja.user_id
GROUP BY u.id, u.name, u.email;

-- Job application details view
CREATE VIEW job_application_details AS
SELECT 
    ja.id,
    ja.user_id,
    ja.job_id,
    ja.status,
    ja.applied_at,
    ja.score,
    ja.auto_applied,
    u.name as user_name,
    u.email as user_email,
    j.title as job_title,
    j.company as company_name,
    j.location as job_location,
    j.remote,
    j.salary_min,
    j.salary_max,
    j.portal
FROM job_applications ja
JOIN users u ON ja.user_id = u.id
JOIN jobs j ON ja.job_id = j.id;

-- Recent scraping activity view
CREATE VIEW recent_scraping_activity AS
SELECT 
    portal,
    status,
    jobs_found,
    jobs_saved,
    errors_count,
    duration_seconds,
    started_at,
    completed_at
FROM scraping_logs
ORDER BY started_at DESC
LIMIT 50;

-- Triggers for automatic timestamp updates

-- Update users.updated_at on modification
CREATE TRIGGER update_users_timestamp 
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update jobs.updated_at on modification
CREATE TRIGGER update_jobs_timestamp 
AFTER UPDATE ON jobs
FOR EACH ROW
BEGIN
    UPDATE jobs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update job_applications.updated_at on modification
CREATE TRIGGER update_job_applications_timestamp 
AFTER UPDATE ON job_applications
FOR EACH ROW
BEGIN
    UPDATE job_applications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Sample data insertion queries (commented out for reference)
/*
-- Insert demo user
INSERT INTO users (email, name, skills, preferences, location, experience_years) VALUES 
('demo@skillnavigator.com', 'Demo User', 
 '["Python", "JavaScript", "React", "Node.js", "FastAPI"]',
 '{"preferred_locations": ["Remote", "San Francisco, CA"], "job_types": ["full-time"], "salary_min": 70000, "auto_apply": false}',
 'San Francisco, CA', 2);

-- Insert sample job
INSERT INTO jobs (title, company, location, remote, salary_min, salary_max, job_type, experience_level, description, skills, portal, url) VALUES
('Senior Full Stack Developer', 'TechCorp Solutions', 'San Francisco, CA', 1, 120000, 160000, 'full-time', 'senior',
 'We are looking for a Senior Full Stack Developer...', 
 '["JavaScript", "React", "Node.js", "AWS"]',
 'linkedin', 'https://linkedin.com/jobs/view/123');

-- Insert sample application
INSERT INTO job_applications (user_id, job_id, status, applied_at, score, auto_applied) VALUES
(1, 1, 'applied', CURRENT_TIMESTAMP, 85.5, 0);
*/
