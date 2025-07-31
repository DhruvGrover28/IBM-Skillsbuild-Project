# SkillNavigator - Setup Instructions for Recipients

## 📥 Getting Started

### Prerequisites
- Python 3.8+ (3.13.5 recommended)
- Git (for GitHub clone)

### Option 1: From ZIP File
1. Extract the ZIP file to your desired location
2. Open terminal/command prompt in the extracted folder

### Option 2: From GitHub
```bash
git clone [YOUR_GITHUB_REPO_URL]
cd skillnavigator
```

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
# Install core packages
pip install -r requirements_simple.txt

# Install additional packages
pip install schedule aiosmtplib email-validator

# Install Playwright browsers
python -m playwright install chromium
```

### 2. Configure Environment
```bash
# Copy environment template
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac

# Edit .env file and add your OpenAI API key:
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Initialize Database
```bash
python scripts/init_db.py
```

### 4. Verify Installation
```bash
python scripts/verify_system.py
```

### 5. Start the Application
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

## 🌐 Access the Application
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

## 🆘 Need Help?
Check VERIFICATION.md for troubleshooting or run:
```bash
python scripts/verify_system.py
```
