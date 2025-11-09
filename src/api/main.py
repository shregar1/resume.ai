"""FastAPI application for CV ranking system."""

import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiofiles
import os

from src.agents.orchestrator_agent import OrchestratorAgent
from src.config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Resume.AI - CV Ranking System",
    description="Multi-agent system for automated CV ranking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# In-memory storage for job results (use database in production)
job_store = {}


# Request/Response Models
class RankingRequest(BaseModel):
    """Request model for ranking job."""
    job_description: str
    job_title: Optional[str] = ""
    company: Optional[str] = ""


class RankingResponse(BaseModel):
    """Response model for ranking job."""
    job_id: str
    status: str
    message: str


class CandidateResult(BaseModel):
    """Candidate ranking result."""
    rank: int
    candidate_name: str
    tier: str
    total_score: float
    skills_score: float
    experience_score: float
    education_score: float
    strengths: List[str]
    weaknesses: List[str]
    explanation: str


class RankingResults(BaseModel):
    """Complete ranking results."""
    job_id: str
    job_title: str
    total_candidates: int
    tier_distribution: dict
    top_candidates: List[CandidateResult]
    completed_at: str


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Resume.AI - Multi-Agent CV Ranking System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.app_env
    }


@app.post("/api/v1/rankings", response_model=RankingResponse)
async def create_ranking_job(
    background_tasks: BackgroundTasks,
    job_description: str = Form(...),
    job_title: str = Form(""),
    company: str = Form(""),
    cv_files: List[UploadFile] = File(...)
):
    """Create a new CV ranking job.
    
    Args:
        job_description: Job description text
        job_title: Job title
        company: Company name
        cv_files: List of CV files (PDF, DOCX, TXT)
        
    Returns:
        Job information
    """
    try:
        # Validate files
        if not cv_files:
            raise HTTPException(status_code=400, detail="No CV files provided")
        
        if len(cv_files) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 CVs allowed per job")
        
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Ensure data directory exists
        os.makedirs(settings.cv_dir, exist_ok=True)
        
        # Save uploaded files
        saved_files = []
        for i, cv_file in enumerate(cv_files):
            # Validate file extension
            file_ext = os.path.splitext(cv_file.filename)[1].lower()
            if file_ext not in settings.allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(settings.allowed_extensions)}"
                )
            
            # Save file
            file_path = os.path.join(settings.cv_dir, f"{job_id}_{i}_{cv_file.filename}")
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await cv_file.read()
                
                # Check file size
                if len(content) > settings.max_upload_size_mb * 1024 * 1024:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File {cv_file.filename} exceeds maximum size of {settings.max_upload_size_mb}MB"
                    )
                
                await f.write(content)
            
            saved_files.append({
                "file_path": file_path,
                "file_type": file_ext.replace(".", ""),
                "original_name": cv_file.filename
            })
        
        # Store initial job status
        job_store[job_id] = {
            "job_id": job_id,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "cv_count": len(saved_files),
            "job_title": job_title,
            "company": company
        }
        
        # Process in background
        background_tasks.add_task(
            process_ranking_job,
            job_id,
            job_description,
            job_title,
            company,
            saved_files
        )
        
        return RankingResponse(
            job_id=job_id,
            status="processing",
            message=f"Ranking job created with {len(saved_files)} CVs. Processing in background."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ranking job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def process_ranking_job(
    job_id: str,
    job_description: str,
    job_title: str,
    company: str,
    cv_files: List[dict]
):
    """Process ranking job in background.
    
    Args:
        job_id: Job ID
        job_description: Job description
        job_title: Job title
        company: Company name
        cv_files: List of CV file information
    """
    try:
        logger.info(f"Processing ranking job {job_id}")
        
        # Update status
        job_store[job_id]["status"] = "processing"
        
        # Run orchestrator
        result = await orchestrator.process({
            "job_description": job_description,
            "job_title": job_title,
            "company": company,
            "cv_files": cv_files
        })
        
        if result.get("success"):
            job_store[job_id].update({
                "status": "completed",
                "results": result,
                "completed_at": datetime.now().isoformat()
            })
            logger.info(f"Job {job_id} completed successfully")
        else:
            job_store[job_id].update({
                "status": "failed",
                "error": result.get("error", "Unknown error"),
                "completed_at": datetime.now().isoformat()
            })
            logger.error(f"Job {job_id} failed: {result.get('error')}")
        
        # Cleanup files
        for cv_file in cv_files:
            try:
                os.remove(cv_file["file_path"])
            except Exception as e:
                logger.warning(f"Could not delete file {cv_file['file_path']}: {e}")
    
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
        job_store[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


@app.get("/api/v1/rankings/{job_id}")
async def get_ranking_status(job_id: str):
    """Get status of a ranking job.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job status and progress
    """
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = job_store[job_id]
    
    return {
        "job_id": job_id,
        "status": job_data["status"],
        "created_at": job_data.get("created_at"),
        "completed_at": job_data.get("completed_at"),
        "cv_count": job_data.get("cv_count", 0),
        "error": job_data.get("error")
    }


@app.get("/api/v1/rankings/{job_id}/results")
async def get_ranking_results(job_id: str, top_n: Optional[int] = None):
    """Get results of a completed ranking job.
    
    Args:
        job_id: Job ID
        top_n: Number of top candidates to return (default: all)
        
    Returns:
        Ranking results
    """
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = job_store[job_id]
    
    if job_data["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job_data['status']}"
        )
    
    results = job_data.get("results", {})
    ranked_candidates = results.get("ranked_candidates", [])
    
    # Limit to top N if specified
    if top_n:
        ranked_candidates = ranked_candidates[:top_n]
    
    # Format response
    candidates = []
    for candidate in ranked_candidates:
        candidates.append({
            "rank": candidate.get("rank"),
            "candidate_name": candidate.get("candidate_name", "Unknown"),
            "tier": candidate.get("tier"),
            "total_score": candidate.get("scores", {}).get("total", 0),
            "skills_score": candidate.get("scores", {}).get("skills_match", 0),
            "experience_score": candidate.get("scores", {}).get("experience_relevance", 0),
            "education_score": candidate.get("scores", {}).get("education_fit", 0),
            "strengths": candidate.get("strengths", []),
            "weaknesses": candidate.get("weaknesses", []),
            "explanation": candidate.get("explanation", "")
        })
    
    return {
        "job_id": job_id,
        "job_title": results.get("jd_data", {}).get("job_title", ""),
        "total_candidates": results.get("total_candidates_ranked", 0),
        "tier_distribution": results.get("tier_distribution", {}),
        "candidates": candidates,
        "completed_at": results.get("completed_at")
    }


@app.delete("/api/v1/rankings/{job_id}")
async def delete_ranking_job(job_id: str):
    """Delete a ranking job and its results.
    
    Args:
        job_id: Job ID
        
    Returns:
        Deletion confirmation
    """
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del job_store[job_id]
    
    return {
        "message": f"Job {job_id} deleted successfully"
    }


@app.get("/api/v1/stats")
async def get_system_stats():
    """Get system statistics.
    
    Returns:
        System stats
    """
    total_jobs = len(job_store)
    completed_jobs = sum(1 for job in job_store.values() if job["status"] == "completed")
    processing_jobs = sum(1 for job in job_store.values() if job["status"] == "processing")
    failed_jobs = sum(1 for job in job_store.values() if job["status"] == "failed")
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "processing_jobs": processing_jobs,
        "failed_jobs": failed_jobs,
        "environment": settings.app_env
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

