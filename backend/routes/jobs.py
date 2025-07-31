"""
Jobs API Routes
Endpoints for job search, scoring, and management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.database.db_connection import get_db, database
from backend.agents.supervisor_agent import SupervisorAgent

router = APIRouter()

# Pydantic models for request/response
class JobSearchRequest(BaseModel):
    keywords: str
    location: Optional[str] = "Remote"
    experience_level: Optional[str] = "entry"
    job_type: Optional[str] = "full-time"
    remote_ok: Optional[bool] = True
    max_jobs: Optional[int] = 50
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    remote_allowed: bool = False
    apply_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    scraped_at: datetime
    source: str
    relevance_score: Optional[float] = None

class ScoredJobResponse(JobResponse):
    relevance_score: float
    skills_match: Dict
    component_scores: Optional[Dict] = None

class BulkApplyRequest(BaseModel):
    job_ids: List[int]
    user_id: int = 1  # Default user for demo

# Dependency to get supervisor agent
async def get_supervisor() -> SupervisorAgent:
    # This would be injected from the main app
    # For now, create a new instance (not ideal for production)
    supervisor = SupervisorAgent()
    await supervisor.initialize()
    return supervisor


@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    db = Depends(get_db)
):
    """Get jobs with optional filtering"""
    try:
        # Build query filters
        filters = {}
        if source:
            filters['source'] = source
        if job_type:
            filters['job_type'] = job_type
        if experience_level:
            filters['experience_level'] = experience_level
        if min_score is not None:
            filters['min_score'] = min_score
        
        # This would query the database with filters
        # For now, return empty list
        jobs = []
        
        return jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")


@router.post("/search")
async def search_jobs(
    search_request: JobSearchRequest,
    supervisor: SupervisorAgent = Depends(get_supervisor)
):
    """Trigger job search and scraping"""
    try:
        # Convert request to search parameters
        search_params = search_request.dict(exclude_none=True)
        
        # Trigger job search workflow
        result = await supervisor.trigger_job_search(search_params)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Job search failed'))
        
        return {
            "message": "Job search completed successfully",
            "result": result,
            "jobs_found": result['phases']['scraping']['jobs_found'],
            "jobs_scored": result['phases']['scoring']['jobs_scored'],
            "high_scoring_jobs": result['phases']['scoring']['high_scoring_jobs']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in job search: {str(e)}")


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db = Depends(get_db)):
    """Get specific job by ID"""
    try:
        # This would query the database for the specific job
        # For now, return sample job
        job = None
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job: {str(e)}")


@router.get("/scored/{user_id}", response_model=List[ScoredJobResponse])
async def get_scored_jobs(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    db = Depends(get_db)
):
    """Get scored jobs for a specific user"""
    try:
        # This would query scored jobs for the user
        # For now, return empty list
        scored_jobs = []
        
        return scored_jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scored jobs: {str(e)}")


@router.post("/score/{user_id}")
async def score_jobs_for_user(
    user_id: int,
    max_jobs: int = Query(100, ge=1, le=500),
    supervisor: SupervisorAgent = Depends(get_supervisor)
):
    """Trigger job scoring for a specific user"""
    try:
        # Get scoring agent from supervisor
        scoring_agent = supervisor.scoring_agent
        
        # Score jobs for user
        scored_jobs = await scoring_agent.score_jobs(user_id, max_jobs)
        
        return {
            "message": "Job scoring completed successfully",
            "user_id": user_id,
            "jobs_scored": len(scored_jobs),
            "high_scoring_jobs": len([job for job in scored_jobs if job['score'] >= 0.7]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring jobs: {str(e)}")


@router.post("/apply")
async def apply_to_jobs(
    apply_request: BulkApplyRequest,
    supervisor: SupervisorAgent = Depends(get_supervisor)
):
    """Apply to multiple jobs automatically"""
    try:
        # Get auto-apply agent from supervisor
        autoapply_agent = supervisor.autoapply_agent
        
        # Apply to jobs
        application_results = await autoapply_agent.auto_apply_to_jobs(
            apply_request.user_id, apply_request.job_ids
        )
        
        successful_applications = len([r for r in application_results if r['success']])
        failed_applications = len([r for r in application_results if not r['success']])
        
        return {
            "message": "Bulk application completed",
            "user_id": apply_request.user_id,
            "total_jobs": len(apply_request.job_ids),
            "successful_applications": successful_applications,
            "failed_applications": failed_applications,
            "success_rate": (successful_applications / len(apply_request.job_ids) * 100) if apply_request.job_ids else 0,
            "application_results": application_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying to jobs: {str(e)}")


@router.get("/recommendations/{user_id}")
async def get_job_recommendations(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db = Depends(get_db)
):
    """Get personalized job recommendations for a user"""
    try:
        # This would get top scored jobs for the user
        # For now, return empty list
        recommendations = []
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


@router.get("/stats/summary")
async def get_jobs_summary(db = Depends(get_db)):
    """Get summary statistics about jobs in the system"""
    try:
        # This would query database for statistics
        # For now, return sample stats
        stats = {
            "total_jobs": 0,
            "jobs_today": 0,
            "top_companies": [],
            "top_job_titles": [],
            "sources": {
                "linkedin": 0,
                "indeed": 0,
                "internshala": 0
            },
            "job_types": {
                "full-time": 0,
                "part-time": 0,
                "contract": 0,
                "internship": 0
            },
            "experience_levels": {
                "entry": 0,
                "mid": 0,
                "senior": 0
            },
            "remote_jobs": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting job statistics: {str(e)}")


@router.delete("/{job_id}")
async def delete_job(job_id: int, db = Depends(get_db)):
    """Delete a specific job"""
    try:
        # This would delete the job from database
        # For now, just return success
        
        return {
            "message": f"Job {job_id} deleted successfully",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting job: {str(e)}")


@router.post("/bulk-delete")
async def bulk_delete_jobs(job_ids: List[int], db = Depends(get_db)):
    """Delete multiple jobs"""
    try:
        # This would delete multiple jobs from database
        # For now, just return success
        
        return {
            "message": f"Deleted {len(job_ids)} jobs successfully",
            "deleted_job_ids": job_ids,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error bulk deleting jobs: {str(e)}")


@router.post("/refresh-scores/{user_id}")
async def refresh_job_scores(
    user_id: int,
    supervisor: SupervisorAgent = Depends(get_supervisor)
):
    """Refresh job scores for a user (when their profile changes)"""
    try:
        # Get scoring agent from supervisor
        scoring_agent = supervisor.scoring_agent
        
        # Rescore jobs for user
        scored_jobs = await scoring_agent.rescore_jobs_for_user(user_id)
        
        return {
            "message": "Job scores refreshed successfully",
            "user_id": user_id,
            "jobs_rescored": len(scored_jobs),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing job scores: {str(e)}")


@router.get("/similar/{job_id}")
async def get_similar_jobs(
    job_id: int,
    limit: int = Query(5, ge=1, le=20),
    db = Depends(get_db)
):
    """Get jobs similar to a specific job"""
    try:
        # This would find similar jobs using ML/similarity algorithms
        # For now, return empty list
        similar_jobs = []
        
        return {
            "job_id": job_id,
            "similar_jobs": similar_jobs,
            "total_count": len(similar_jobs),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar jobs: {str(e)}")


# WebSocket endpoint for real-time job updates (would be implemented separately)
# @router.websocket("/ws/{user_id}")
# async def websocket_job_updates(websocket: WebSocket, user_id: int):
#     """WebSocket for real-time job updates"""
#     pass
