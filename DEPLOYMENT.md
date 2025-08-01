# SkillNavigator Deployment Guide

## Quick Deploy Options

### 1. Railway (Recommended)
1. Visit: https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select your `skillnavigator` repository
5. Set environment variable: `OPENAI_API_KEY=your_key_here`
6. Deploy automatically with railway.json config

### 2. Render
1. Visit: https://render.com
2. Connect GitHub account
3. "New Web Service" from repository
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python run_backend.py`
6. Add environment variables in dashboard

### 3. Heroku
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `git push heroku main`
4. `heroku config:set OPENAI_API_KEY=your_key_here`

## Environment Variables Needed
- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: Auto-set by hosting platform
- `HOST`: Auto-set by hosting platform

## Files Already Configured
- ✅ railway.json - Railway deployment config
- ✅ Procfile - Platform process definition  
- ✅ requirements.txt - Python dependencies
- ✅ .env.production - Production environment template
- ✅ run_backend.py - Production-ready backend runner

## Database
The SQLite database with 150+ real jobs is included in the repository and will work automatically on any platform.

## Frontend
The React frontend is built and served by the FastAPI backend, so deploying the backend serves the entire application.
