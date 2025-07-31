# SkillNavigator Development Guide

## Quick Start

### 1. Initial Setup
```bash
# Clone or download the project
cd skillnavigator

# Option A: Use startup script (Windows)
./start.bat

# Option B: Use startup script (Linux/Mac)
chmod +x start.sh
./start.sh

# Option C: Manual setup
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (minimum required):
# OPENAI_API_KEY=your-openai-api-key-here
# SECRET_KEY=your-secret-key-here
```

### 3. Initialize Database
```bash
python scripts/init_db.py
```

### 4. Start the Application
```bash
python -m uvicorn backend.main:app --reload --host localhost --port 8000
```

### 5. Test the API
```bash
python scripts/test_api.py
```

## Project Structure

```
skillnavigator/
├── backend/                 # FastAPI backend application
│   ├── agents/             # AI agent implementations
│   │   ├── scraper_agent.py        # Job scraping agent
│   │   ├── scoring_agent.py        # Job scoring agent
│   │   ├── autoapply_agent.py      # Auto-application agent
│   │   ├── tracker_agent.py        # Application tracking agent
│   │   └── supervisor_agent.py     # Orchestration agent
│   ├── routes/             # API route handlers
│   │   ├── jobs.py         # Job-related endpoints
│   │   ├── tracker.py      # Application tracking endpoints
│   │   └── user.py         # User management endpoints
│   ├── utils/              # Utility modules
│   │   ├── scraper_helpers.py      # Web scraping utilities
│   │   ├── matching.py     # Job-profile matching logic
│   │   └── prompt_templates.py     # AI prompt templates
│   ├── database/           # Database configuration
│   │   └── db_connection.py        # SQLAlchemy models
│   └── main.py             # FastAPI application entry point
├── data/                   # Sample data for testing
│   ├── user_profiles.json          # Sample user profiles
│   ├── job_listings.json           # Sample job listings
│   └── applications.json           # Sample applications
├── database/               # Database schema and scripts
│   └── schema.sql          # Complete database schema
├── scripts/                # Utility scripts
│   ├── init_db.py          # Database initialization
│   └── test_api.py         # API testing script
├── uploads/                # File upload directory (created at runtime)
├── logs/                   # Application logs (created at runtime)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Docker Compose for easy deployment
├── start.bat              # Windows startup script
├── start.sh               # Linux/Mac startup script
└── README.md              # Project documentation
```

## Development Workflow

### 1. Agent Development
Each agent is an independent module with specific responsibilities:

- **ScraperAgent**: Scrapes job listings from various portals
- **ScoringAgent**: Scores jobs based on user profile match
- **AutoApplyAgent**: Automatically applies to suitable jobs
- **TrackerAgent**: Tracks application status and follow-ups
- **SupervisorAgent**: Orchestrates all agents and workflows

### 2. API Development
The API is organized into three main route groups:
- `/api/jobs/`: Job search, scoring, and management
- `/api/tracker/`: Application tracking and analytics
- `/api/users/`: User profile and preference management

### 3. Database Development
- Uses SQLAlchemy ORM with SQLite (default) or PostgreSQL
- Schema defined in `database/schema.sql`
- Models in `backend/database/db_connection.py`
- Sample data in `data/` directory

## Testing

### Unit Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when test files are created)
pytest tests/
```

### API Testing
```bash
# Test all endpoints
python scripts/test_api.py

# Test specific functionality
curl http://localhost:8000/health
curl http://localhost:8000/agents/status
```

### Manual Testing
1. Start the backend server
2. Open http://localhost:8000/docs for Swagger UI
3. Test individual endpoints using the interactive documentation

## Deployment

### Local Development
```bash
python -m uvicorn backend.main:app --reload --host localhost --port 8000
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t skillnavigator .
docker run -p 8000:8000 skillnavigator

# Or use Docker Compose
docker-compose up -d
```

### Production Deployment
1. Set `APP_ENV=production` in `.env`
2. Use PostgreSQL instead of SQLite
3. Configure proper secret keys and API keys
4. Set up reverse proxy (nginx)
5. Use process manager (supervisor, systemd)

## Configuration

### Required Environment Variables
```bash
# Minimum required for basic functionality
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./skillnavigator.db
```

### Optional Configurations
- **Email**: Configure SMTP for notifications
- **Redis**: Enable caching and background tasks
- **Job Portal APIs**: LinkedIn, Indeed API keys
- **Cloud Storage**: AWS S3 for file uploads
- **Monitoring**: Sentry for error tracking

## System Verification Guide

### Complete System Check

To verify everything is working perfectly, run the comprehensive verification script:

```bash
# Run complete system verification
python scripts/verify_system.py
```

This script will check:
- ✅ Python environment and dependencies
- ✅ Project file structure
- ✅ Configuration files
- ✅ Database setup and data
- ✅ Server startup capability
- ✅ API endpoint functionality
- ✅ Agent system operations

### Step-by-Step Manual Verification

#### 1. Environment Setup Check
```bash
# Verify Python version (3.8+ required)
python --version

# Check virtual environment
pip list | grep fastapi

# Verify all dependencies
pip install -r requirements.txt
```

#### 2. Configuration Verification
```bash
# Check if .env file exists
ls -la .env

# Verify critical settings (edit .env with your values)
# OPENAI_API_KEY=your-actual-api-key
# SECRET_KEY=your-secret-key
# DATABASE_URL=sqlite:///./skillnavigator.db
```

#### 3. Database Initialization
```bash
# Initialize database with sample data
python scripts/init_db.py

# Verify database creation
ls -la skillnavigator.db

# Check sample data (should show 5 users, 10 jobs, 10 applications)
python -c "import sqlite3; conn=sqlite3.connect('skillnavigator.db'); print('Users:', conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]); print('Jobs:', conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]); conn.close()"
```

#### 4. Server Startup Test
```bash
# Start the backend server
python -m uvicorn backend.main:app --reload --host localhost --port 8000

# In another terminal, test basic connectivity
curl http://localhost:8000/health
# Should return: {"status": "healthy", "timestamp": "..."}
```

#### 5. API Functionality Test
```bash
# Run API test suite
python scripts/test_api.py

# Manual API tests
curl http://localhost:8000/agents/status
curl "http://localhost:8000/api/jobs/search?q=python&limit=5"
curl http://localhost:8000/api/users/
```

#### 6. Agent System Test
```bash
# Test workflow trigger
curl -X POST http://localhost:8000/workflow \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "workflow_type": "score_jobs"}'

# Test scraping trigger (small test)
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"portals": ["linkedin"], "filters": {"keywords": ["python"], "max_jobs": 2}}'
```

#### 7. Interactive API Documentation
```bash
# Open Swagger UI in browser
# http://localhost:8000/docs

# Try out endpoints interactively:
# - GET /health
# - GET /agents/status  
# - GET /api/jobs/search
# - GET /api/users/
# - POST /workflow
```

### Expected Results

When everything is working correctly, you should see:

#### ✅ Healthy System Indicators
- Server starts without errors
- All API endpoints return 200 status codes
- Database contains sample data (5 users, 10 jobs, 10 applications)
- Agents status shows all agents as "ready"
- Workflow triggers return success messages

#### ✅ Sample API Responses
```json
# GET /health
{
  "status": "healthy",
  "timestamp": "2025-07-31T12:00:00Z",
  "database": "connected",
  "agents": "ready"
}

# GET /agents/status
{
  "scraper_agent": "ready",
  "scoring_agent": "ready", 
  "autoapply_agent": "ready",
  "tracker_agent": "ready",
  "supervisor_agent": "ready"
}

# GET /api/jobs/search?q=python&limit=3
{
  "jobs": [
    {
      "id": 1,
      "title": "Senior Full Stack Developer",
      "company": "TechCorp Solutions",
      "location": "San Francisco, CA",
      "remote": true,
      "skills": ["Python", "JavaScript", "React"]
    }
  ],
  "total": 10,
  "page": 1
}
```

### Performance Benchmarks

A healthy system should achieve:
- **Server startup**: < 10 seconds
- **API response time**: < 500ms for basic endpoints
- **Database queries**: < 100ms for simple operations
- **Job search**: < 2 seconds for 100 jobs
- **AI scoring**: < 5 seconds per job (with API)

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`

2. **Database Errors**
   - Initialize database: `python scripts/init_db.py`
   - Check database permissions

3. **Playwright Issues**
   - Install browsers: `playwright install chromium`
   - Check if running in headless mode

4. **API Key Errors**
   - Verify `.env` file exists and contains valid keys
   - Check OpenAI API key format

5. **Port Already in Use**
   - Change port in `.env`: `PORT=8001`
   - Kill existing process: `lsof -ti:8000 | xargs kill`

### Debug Mode
```bash
# Enable debug logging
DEBUG=true
LOG_LEVEL=DEBUG

# Mock APIs for testing
DEV_MOCK_APIS=true
TEST_SKIP_REAL_APIS=true
```

## Contributing

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and modular

### Adding New Agents
1. Create new agent class inheriting from base agent
2. Implement required methods
3. Register agent in supervisor
4. Add corresponding API endpoints
5. Update documentation

### Adding New API Endpoints
1. Create route handler in appropriate route file
2. Define Pydantic models for request/response
3. Add proper error handling
4. Update API documentation
5. Add tests

## Performance Optimization

### Database Optimization
- Use database indexes for frequent queries
- Implement connection pooling
- Consider read replicas for scaling

### API Optimization
- Implement response caching
- Use async/await for I/O operations
- Add request rate limiting
- Optimize database queries

### Agent Optimization
- Implement background task queues
- Add retry mechanisms
- Optimize scraping delays
- Cache AI model responses

## Security Considerations

### API Security
- Implement proper authentication
- Use HTTPS in production
- Validate all input data
- Implement rate limiting

### Data Security
- Encrypt sensitive data
- Secure API keys
- Regular security updates
- GDPR compliance features

### Scraping Ethics
- Respect robots.txt
- Implement reasonable delays
- Don't overload target servers
- Follow terms of service

## Monitoring and Logging

### Application Monitoring
- Health check endpoints
- Performance metrics
- Error tracking with Sentry
- Database query monitoring

### Business Metrics
- Application success rates
- User engagement metrics
- Job matching accuracy
- System performance KPIs

## Future Enhancements

### Planned Features
- Advanced AI models for better matching
- Interview preparation assistance
- Salary negotiation guidance
- Company culture insights
- Mobile application
- Browser extension

### Technical Improvements
- GraphQL API
- Real-time notifications
- Advanced caching strategies
- Microservices architecture
- Kubernetes deployment
- CI/CD pipeline automation
