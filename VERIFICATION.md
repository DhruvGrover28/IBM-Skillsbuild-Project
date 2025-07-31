# SkillNavigator Verification Checklist

## 🚀 How to Check if Everything Works Perfectly

### Option 1: One-Click Verification (Recommended)

**Windows:**
```bash
# Double-click or run in Command Prompt
./verify.bat
```

**Linux/Mac:**
```bash
# Make executable and run
chmod +x verify.sh
./verify.sh
```

This will automatically check everything and guide you through any issues.

---

### Option 2: Comprehensive System Verification

```bash
# Run the detailed verification script
python scripts/verify_system.py
```

This provides a complete health check with colored output and detailed diagnostics.

---

### Option 3: Manual Step-by-Step Verification

#### ✅ **Step 1: Environment Check**
```bash
# Check Python version (should be 3.8+)
python --version

# Check if virtual environment is recommended
pip list | grep fastapi
```

**Expected Result:** Python 3.8+ and FastAPI should be listed if installed.

#### ✅ **Step 2: Dependencies Check**
```bash
# Install/verify all dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

**Expected Result:** All packages install without errors.

#### ✅ **Step 3: Project Structure Check**
```bash
# Verify core files exist
ls backend/main.py
ls backend/agents/
ls backend/routes/
ls data/
ls requirements.txt
```

**Expected Result:** All files and directories should exist.

#### ✅ **Step 4: Configuration Check**
```bash
# Check if .env exists
ls .env

# If not, create from template
cp .env.example .env

# Edit .env with your actual API keys
# OPENAI_API_KEY=sk-your-actual-key-here
# SECRET_KEY=your-secret-key-here
```

**Expected Result:** .env file exists with your actual API keys configured.

#### ✅ **Step 5: Database Initialization**
```bash
# Initialize database with sample data
python scripts/init_db.py

# Verify database was created
ls skillnavigator.db

# Check data was loaded
python -c "
import sqlite3
conn = sqlite3.connect('skillnavigator.db')
print('Users:', conn.execute('SELECT COUNT(*) FROM users').fetchone()[0])
print('Jobs:', conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0])  
print('Applications:', conn.execute('SELECT COUNT(*) FROM job_applications').fetchone()[0])
conn.close()
"
```

**Expected Result:** Database file exists with 5 users, 10 jobs, and 10 applications.

#### ✅ **Step 6: Server Startup Test**
```bash
# Start the backend server
python -m uvicorn backend.main:app --reload --host localhost --port 8000
```

**Expected Result:** Server starts without errors and shows:
```
INFO:     Uvicorn running on http://localhost:8000
INFO:     Application startup complete
```

#### ✅ **Step 7: API Health Check**
Open a new terminal/command prompt and run:
```bash
# Test basic connectivity
curl http://localhost:8000/health

# Or use Python
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

**Expected Result:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-31T12:00:00Z",
  "database": "connected",
  "agents": "ready"
}
```

#### ✅ **Step 8: Agent Status Check**
```bash
curl http://localhost:8000/agents/status
```

**Expected Result:**
```json
{
  "scraper_agent": "ready",
  "scoring_agent": "ready",
  "autoapply_agent": "ready", 
  "tracker_agent": "ready",
  "supervisor_agent": "ready"
}
```

#### ✅ **Step 9: API Endpoints Test**
```bash
# Test job search
curl "http://localhost:8000/api/jobs/search?q=python&limit=3"

# Test user profiles
curl http://localhost:8000/api/users/

# Test applications
curl http://localhost:8000/api/tracker/applications
```

**Expected Result:** Each endpoint returns JSON data with sample records.

#### ✅ **Step 10: Interactive API Documentation**
Open your browser and go to: `http://localhost:8000/docs`

**Expected Result:** Swagger UI loads showing all 40+ API endpoints with interactive testing capability.

#### ✅ **Step 11: Agent Functionality Test**
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

**Expected Result:** Both return success messages indicating agents are working.

#### ✅ **Step 12: Comprehensive API Test**
```bash
# Run the complete API test suite
python scripts/test_api.py
```

**Expected Result:** All tests pass with ✅ green checkmarks.

---

## 🎯 Success Indicators

When everything is working perfectly, you should see:

### ✅ **System Health Indicators**
- Server starts in < 10 seconds
- All API endpoints return HTTP 200
- Database contains sample data
- All 5 agents show "ready" status
- No error messages in logs

### ✅ **Performance Benchmarks**
- API responses < 500ms
- Database queries < 100ms  
- Health check < 100ms
- Job search < 2 seconds

### ✅ **Functional Verification**
- Jobs can be searched and filtered
- User profiles can be created/updated
- Applications can be tracked
- Workflows can be triggered
- Agents respond to commands

---

## 🔧 Common Issues & Quick Fixes

### ❌ **"Module not found" errors**
```bash
# Fix: Install dependencies
pip install -r requirements.txt
```

### ❌ **"Database file not found"**
```bash
# Fix: Initialize database
python scripts/init_db.py
```

### ❌ **"Port 8000 already in use"**
```bash
# Fix: Kill existing process or use different port
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -ti:8000 | xargs kill
# Or change port: PORT=8001 in .env
```

### ❌ **"OpenAI API error"**
```bash
# Fix: Add valid API key to .env
OPENAI_API_KEY=sk-your-actual-key-here
```

### ❌ **"Playwright browser not found"**
```bash
# Fix: Install Playwright browsers
playwright install chromium
```

---

## 🎉 Final Verification

If all steps pass, your SkillNavigator system is **100% operational** and ready for:

- ✅ **Production deployment**
- ✅ **Frontend development**  
- ✅ **Real job searching**
- ✅ **AI-powered matching**
- ✅ **Automated applications**
- ✅ **Application tracking**

**🚀 You're ready to start using SkillNavigator!**

---

## 📞 Need Help?

If any verification step fails:

1. **Check the error message** - it usually tells you exactly what's wrong
2. **Run the troubleshooting commands** listed above
3. **Check the logs** in the terminal where the server is running
4. **Verify your .env configuration** - especially API keys
5. **Try the one-click verification scripts** - they often fix issues automatically

The system is designed to be robust and self-healing, so most issues can be resolved quickly!
