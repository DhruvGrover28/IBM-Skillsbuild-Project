"""
User API Routes
Endpoints for user profile management and preferences
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Dict, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import json

from database.db_connection import get_db, database

router = APIRouter()

# Pydantic models for request/response
class UserProfileResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    updated_at: datetime
    resume_path: Optional[str] = None
    skills: List[str] = []
    preferences: Dict = {}
    location: Optional[str] = None
    experience_years: int = 0

class UserPreferencesUpdate(BaseModel):
    preferred_locations: Optional[List[str]] = None
    job_types: Optional[List[str]] = None
    experience_levels: Optional[List[str]] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    preferred_companies: Optional[List[str]] = None
    avoided_companies: Optional[List[str]] = None
    remote_preference: Optional[bool] = None
    auto_apply: Optional[bool] = None
    max_applications_per_day: Optional[int] = None
    notification_preferences: Optional[Dict] = None

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[List[str]] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    location: Optional[str] = None
    experience_years: int = 0
    skills: List[str] = []
    preferences: Dict = {}


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: int, db = Depends(get_db)):
    """Get user profile by ID"""
    try:
        # This would query the database for user profile
        # For now, return sample profile
        user_profile = {
            "id": user_id,
            "email": "demo@skillnavigator.com",
            "name": "Demo User",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "resume_path": None,
            "skills": ["Python", "JavaScript", "React", "Machine Learning"],
            "preferences": {
                "preferred_locations": ["Remote", "San Francisco", "New York"],
                "job_types": ["full-time", "contract"],
                "experience_levels": ["entry", "mid"],
                "salary_min": 60000,
                "auto_apply": False
            },
            "location": "San Francisco, CA",
            "experience_years": 2
        }
        
        return UserProfileResponse(**user_profile)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user profile: {str(e)}")


@router.put("/profile/{user_id}")
async def update_user_profile(
    user_id: int,
    profile_update: UserProfileUpdate,
    db = Depends(get_db)
):
    """Update user profile"""
    try:
        # This would update user profile in database
        # For now, just return success
        
        update_data = profile_update.dict(exclude_none=True)
        
        return {
            "message": "Profile updated successfully",
            "user_id": user_id,
            "updated_fields": list(update_data.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: int, db = Depends(get_db)):
    """Get user preferences"""
    try:
        # This would query user preferences from database
        # For now, return sample preferences
        preferences = {
            "preferred_locations": ["Remote", "San Francisco", "New York"],
            "job_types": ["full-time", "contract"],
            "experience_levels": ["entry", "mid"],
            "salary_min": 60000,
            "salary_max": 120000,
            "preferred_companies": ["Google", "Microsoft", "Apple"],
            "avoided_companies": [],
            "remote_preference": True,
            "auto_apply": False,
            "max_applications_per_day": 5,
            "notification_preferences": {
                "email_notifications": True,
                "push_notifications": True,
                "weekly_summary": True
            }
        }
        
        return {
            "user_id": user_id,
            "preferences": preferences,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching preferences: {str(e)}")


@router.put("/preferences/{user_id}")
async def update_user_preferences(
    user_id: int,
    preferences_update: UserPreferencesUpdate,
    db = Depends(get_db)
):
    """Update user preferences"""
    try:
        # This would update user preferences in database
        # For now, just return success
        
        update_data = preferences_update.dict(exclude_none=True)
        
        return {
            "message": "Preferences updated successfully",
            "user_id": user_id,
            "updated_preferences": list(update_data.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")


@router.post("/resume/{user_id}")
async def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """Upload user resume"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "application/msword", 
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Only PDF, DOC, and DOCX files are allowed"
            )
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 10MB limit"
            )
        
        # Save file
        file_extension = file.filename.split('.')[-1].lower()
        filename = f"resume_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        file_path = f"uploads/resumes/{filename}"
        
        # This would save the file to disk/cloud storage
        # For now, just simulate the save
        
        # Update user profile with resume path
        # This would update the database
        
        return {
            "message": "Resume uploaded successfully",
            "user_id": user_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": len(file_content),
            "content_type": file.content_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading resume: {str(e)}")


@router.get("/resume/{user_id}")
async def get_resume_info(user_id: int, db = Depends(get_db)):
    """Get user resume information"""
    try:
        # This would query database for resume info
        # For now, return sample info
        resume_info = {
            "user_id": user_id,
            "resume_path": f"uploads/resumes/resume_{user_id}_20250101_120000.pdf",
            "uploaded_at": datetime.utcnow().isoformat(),
            "file_size": 1024000,
            "content_type": "application/pdf"
        }
        
        return resume_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resume info: {str(e)}")


@router.delete("/resume/{user_id}")
async def delete_resume(user_id: int, db = Depends(get_db)):
    """Delete user resume"""
    try:
        # This would delete resume file and update database
        # For now, just return success
        
        return {
            "message": "Resume deleted successfully",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {str(e)}")


@router.post("/create")
async def create_user(user_data: CreateUserRequest, db = Depends(get_db)):
    """Create new user"""
    try:
        # This would create user in database
        # For now, just return sample user
        
        new_user = {
            "id": 999,  # Would be auto-generated
            "email": user_data.email,
            "name": user_data.name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "skills": user_data.skills,
            "preferences": user_data.preferences,
            "location": user_data.location,
            "experience_years": user_data.experience_years
        }
        
        return {
            "message": "User created successfully",
            "user": new_user,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/skills/suggestions")
async def get_skill_suggestions(query: str = "", limit: int = 10):
    """Get skill suggestions for autocomplete"""
    try:
        # This would return skill suggestions based on query
        # For now, return common tech skills
        all_skills = [
            "Python", "JavaScript", "Java", "TypeScript", "C++", "C#", "Go", "Rust",
            "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask",
            "FastAPI", "Spring", "Laravel", "Ruby on Rails", "HTML", "CSS",
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Elasticsearch",
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
            "Git", "GitHub", "GitLab", "Linux", "Bash", "Machine Learning",
            "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy",
            "Scikit-learn", "Data Science", "Analytics", "Statistics"
        ]
        
        if query:
            suggestions = [skill for skill in all_skills 
                         if query.lower() in skill.lower()][:limit]
        else:
            suggestions = all_skills[:limit]
        
        return {
            "suggestions": suggestions,
            "query": query,
            "total_count": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting skill suggestions: {str(e)}")


@router.get("/stats/{user_id}")
async def get_user_stats(user_id: int, db = Depends(get_db)):
    """Get user statistics and insights"""
    try:
        # This would calculate user statistics from database
        # For now, return sample stats
        stats = {
            "profile_completeness": 85,
            "total_applications": 15,
            "response_rate": 33.3,
            "interview_rate": 20.0,
            "success_rate": 6.7,
            "avg_application_score": 0.72,
            "skill_match_rate": 78.5,
            "profile_views": 42,
            "recommended_jobs": 8,
            "profile_strength": "Strong",
            "areas_for_improvement": [
                "Add more recent projects to portfolio",
                "Expand skill set in cloud technologies",
                "Increase application frequency"
            ],
            "achievements": [
                "High skill match rate",
                "Strong profile completeness",
                "Active job seeker"
            ]
        }
        
        return {
            "user_id": user_id,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")


@router.delete("/{user_id}")
async def delete_user(user_id: int, db = Depends(get_db)):
    """Delete user and all associated data"""
    try:
        # This would delete user and all related data from database
        # For now, just return success
        
        return {
            "message": "User deleted successfully",
            "user_id": user_id,
            "deleted_data": [
                "profile", "applications", "preferences", "resume", "activity_logs"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


@router.get("/export/{user_id}")
async def export_user_data(
    user_id: int,
    format: str = "json",
    include_applications: bool = True,
    db = Depends(get_db)
):
    """Export all user data"""
    try:
        # This would export all user data
        # For now, return download info
        
        return {
            "message": "User data export generated",
            "user_id": user_id,
            "format": format,
            "includes": {
                "profile": True,
                "preferences": True,
                "applications": include_applications,
                "resume_info": True,
                "activity_logs": True
            },
            "download_url": f"/downloads/user_data_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}.{format}",
            "expires_at": (datetime.utcnow().replace(hour=23, minute=59, second=59)).isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting user data: {str(e)}")


@router.post("/analyze-resume/{user_id}")
async def analyze_resume(user_id: int, db = Depends(get_db)):
    """Analyze uploaded resume and extract insights"""
    try:
        # This would use AI to analyze the resume
        # For now, return sample analysis
        
        analysis = {
            "extracted_skills": [
                "Python", "JavaScript", "React", "Django", "PostgreSQL", 
                "Git", "AWS", "Machine Learning"
            ],
            "experience_level": "Mid-level (2-3 years)",
            "key_achievements": [
                "Led development of 3 web applications",
                "Improved system performance by 40%",
                "Managed team of 2 junior developers"
            ],
            "missing_skills": [
                "Docker", "Kubernetes", "TypeScript", "GraphQL"
            ],
            "suggestions": [
                "Add more quantifiable achievements",
                "Include relevant certifications",
                "Highlight leadership experience",
                "Add technical project details"
            ],
            "ats_score": 78,
            "readability_score": 85,
            "format_score": 90
        }
        
        return {
            "user_id": user_id,
            "analysis": analysis,
            "confidence_score": 0.89,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")


# WebSocket endpoint for real-time profile updates (would be implemented separately)
# @router.websocket("/ws/profile/{user_id}")
# async def websocket_profile_updates(websocket: WebSocket, user_id: int):
#     """WebSocket for real-time profile updates"""
#     pass
