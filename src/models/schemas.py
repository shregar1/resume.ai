"""Data models for the CV ranking system."""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class SeniorityLevel(str, Enum):
    """Job seniority levels."""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class CandidateTier(str, Enum):
    """Candidate ranking tiers."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class WorkflowStatus(str, Enum):
    """Workflow states."""
    INITIALIZED = "initialized"
    PARSING = "parsing"
    ANALYZING_JD = "analyzing_jd"
    MATCHING = "matching"
    SCORING = "scoring"
    RANKING = "ranking"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class Experience(BaseModel):
    """Work experience entry."""
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_months: Optional[int] = None
    description: str = ""
    key_achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry."""
    institution: str
    degree: str
    field: str
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class Certification(BaseModel):
    """Certification entry."""
    name: str
    issuer: str
    date: Optional[str] = None


class Project(BaseModel):
    """Project entry."""
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None


class Skills(BaseModel):
    """Skills grouping."""
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class Candidate(BaseModel):
    """Candidate personal information."""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""


class CVData(BaseModel):
    """Structured CV data."""
    cv_id: str
    candidate: Candidate
    summary: str = ""
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    certifications: List[Certification] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    total_experience_years: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SkillRequirement(BaseModel):
    """Skill with weight."""
    skill: str
    weight: float = 1.0


class JobRequirements(BaseModel):
    """Job requirements."""
    must_have_skills: List[SkillRequirement] = Field(default_factory=list)
    nice_to_have_skills: List[SkillRequirement] = Field(default_factory=list)
    min_experience_years: float = 0.0
    education_level: str = ""
    industry_experience: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class ScoringWeights(BaseModel):
    """Scoring weights."""
    skills: float = 0.4
    experience: float = 0.3
    education: float = 0.15
    career_trajectory: float = 0.1
    other: float = 0.05


class JobDescription(BaseModel):
    """Job description model."""
    jd_id: str
    job_title: str
    company: str = ""
    department: str = ""
    seniority_level: SeniorityLevel = SeniorityLevel.MID
    requirements: JobRequirements = Field(default_factory=JobRequirements)
    responsibilities: List[str] = Field(default_factory=list)
    scoring_weights: ScoringWeights = Field(default_factory=ScoringWeights)
    full_description: str = ""


class SkillMatch(BaseModel):
    """Individual skill match."""
    skill: str
    cv_proficiency: str = "unknown"
    jd_requirement: str = "required"
    match_score: float = 0.0


class Matches(BaseModel):
    """Matching details."""
    matched_skills: List[SkillMatch] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    extra_skills: List[str] = Field(default_factory=list)


class Scores(BaseModel):
    """Score breakdown."""
    total: float = 0.0
    skills_match: float = 0.0
    experience_relevance: float = 0.0
    education_fit: float = 0.0
    career_trajectory: float = 0.0
    confidence: float = 0.0


class CandidateScore(BaseModel):
    """Candidate scoring result."""
    candidate_id: str
    cv_id: str
    jd_id: str
    candidate_name: str = ""
    scores: Scores = Field(default_factory=Scores)
    matches: Matches = Field(default_factory=Matches)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    explanation: str = ""
    rank: int = 0
    tier: CandidateTier = CandidateTier.C


class RankingJob(BaseModel):
    """Ranking job tracking."""
    job_id: str
    status: WorkflowStatus = WorkflowStatus.INITIALIZED
    cv_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    jd_id: Optional[str] = None
    results: List[CandidateScore] = Field(default_factory=list)
    error_message: Optional[str] = None


class AgentMessage(BaseModel):
    """Standard agent message format."""
    message_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    source_agent: str
    target_agent: str
    message_type: str  # task, result, error, status
    priority: str = "medium"  # high, medium, low
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str
    retry_count: int = 0

