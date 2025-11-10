# Multi-Agent CV Ranking System - Design Specification

## Executive Summary

This document outlines the architecture for an intelligent multi-agent system designed to automatically rank 50+ CVs based on job descriptions. The system employs specialized AI agents working collaboratively to parse, analyze, match, and rank candidates efficiently and accurately.

---

### Orchestrator Agent

**Role**: Master coordinator managing workflow and agent lifecycle

**Responsibilities**:
- Receive ranking requests via API
- Distribute tasks to specialized agents
- Monitor agent health and performance
- Handle failures and retries
- Aggregate results from all agents
- Maintain state machine for workflow

**Key Capabilities**:
- Dynamic load balancing
- Priority queue management
- Deadlock detection and resolution
- Real-time progress tracking

### Parser Agent (Pool of Agents)

**Role**: Extract structured data from unstructured CVs

**Responsibilities**:
- Text extraction from pdfs
- Structured data extraction:
  - Personal information
  - Education history
  - Work experience (roles, companies, dates, descriptions)
  - Skills (technical, soft skills)
  - Certifications
  - Projects
  - Languages
- Named Entity Recognition (NER)
- Generate structured JSON output

### 2.4 Job Description Analyzer Agent

**Role**: Extract requirements and priorities from job descriptions

**Responsibilities**:
- Parse job description text
- Extract key requirements:
  - Must-have skills
  - Nice-to-have skills
  - Required experience level
  - Educational requirements
  - Industry experience
  - Role responsibilities
- Identify implicit requirements
- Generate weighted criteria
- Create semantic embeddings
- Build matching profile

### Matching Agent (Semantic Matcher)

**Role**: Calculate relevance between CVs and job requirements

**Responsibilities**:
- Semantic similarity matching
- Skill matching with fuzzy logic
- Experience level alignment
- Education requirement matching
- Industry experience matching
- Generate match scores for each criterion
- Identify gaps and strengths

### Scoring Engine Agent

**Role**: Assign quantitative scores to each CV

**Responsibilities**:
- Aggregate match scores from Matching Agent
- Apply weighted scoring formula
- Calculate sub-scores:
  - Skills match score (0-100)
  - Experience relevance score (0-100)
  - Education fit score (0-100)
  - Career trajectory score (0-100)
  - Culture fit score (0-100) [optional]
- Normalize scores across all CVs
- Generate confidence intervals
- Flag anomalies or edge cases

**Scoring Formula**:
```
Total Score = (w1 × Skills) + (w2 × Experience) + (w3 × Education) 
              + (w4 × Career) + (w5 × Other)

where w1 + w2 + w3 + w4 + w5 = 1
Weights derived from Job Description priorities
```

### Ranking Agent

**Role**: Generate final ranked candidate list

**Responsibilities**:
- Sort candidates by total score
- Apply business rules:
  - Minimum threshold scores
  - Mandatory requirement filters
  - Diversity considerations
- Group candidates into tiers (A, B, C)
- Handle ties intelligently
- Generate ranking metadata
- Output final ranked list

### Explainability Agent

**Role**: Provide human-interpretable explanations for rankings

**Responsibilities**:
- Generate explanation for each candidate's score
- Highlight strengths and weaknesses
- Identify top matching skills
- Flag missing critical requirements
- Provide comparison insights
- Create visualizations
- Generate natural language summaries

**Output Examples**:
- "Strong match: 8+ years Java experience, AWS certified"
- "Gap: No experience with Kubernetes"
- "Overqualified: Senior level for mid-level role"
