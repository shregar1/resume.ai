# Multi-Agent CV Ranking System - Design Specification

## Executive Summary

This document outlines the architecture for an intelligent multi-agent system designed to automatically rank 50+ CVs based on job descriptions. The system employs specialized AI agents working collaboratively to parse, analyze, match, and rank candidates efficiently and accurately.

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                         │
│                    (REST API + WebSocket)                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                               │                                  │
│                    Orchestrator Agent                            │
│                 (Coordination & Workflow)                        │
│                                                                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼─────────┐  ┌─────────▼──────────┐  ┌────────▼────────┐
│  Input Handler  │  │  Parser Agents     │  │  JD Analyzer    │
│     Agent       │  │   (Parallel)       │  │     Agent       │
└───────┬─────────┘  └─────────┬──────────┘  └────────┬────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼─────────┐          ┌─────────▼──────────┐
        │  Matching Agent │          │  Scoring Engine    │
        │   (Semantic)    │          │     Agent          │
        └───────┬─────────┘          └─────────┬──────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                        ┌───────▼─────────┐
                        │  Ranking Agent  │
                        │  (Final Output) │
                        └───────┬─────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼─────────┐          ┌─────────▼──────────┐
        │  Explainability │          │  Report Generator  │
        │     Agent       │          │      Agent         │
        └─────────────────┘          └────────────────────┘
```

### 1.2 Architecture Pattern

**Event-Driven Microservices Architecture with Agent Orchestration**

- **Async Message Passing**: Agents communicate via message queues
- **Distributed Processing**: Parallel processing of multiple CVs
- **Scalability**: Horizontal scaling for parser and matching agents
- **Resilience**: Circuit breakers and retry mechanisms
- **Observability**: Distributed tracing and monitoring

---

## 2. Agent Roles and Responsibilities

### 2.1 Orchestrator Agent

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

### 2.2 Input Handler Agent

**Role**: Validate and preprocess incoming data

**Responsibilities**:
- Accept CVs in multiple formats (PDF, DOCX, TXT, HTML)
- Validate file integrity and size
- Extract metadata (filename, upload time, candidate info)
- Store raw files in object storage
- Queue CVs for parsing
- Handle job description intake

**Key Capabilities**:
- Format detection and validation
- Duplicate detection
- Batch processing support
- Error handling and logging

### 2.3 Parser Agent (Pool of Agents)

**Role**: Extract structured data from unstructured CVs

**Responsibilities**:
- OCR for scanned documents
- Text extraction from various formats
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

**Key Capabilities**:
- Multi-format parsing (PDF, DOCX, etc.)
- Layout analysis (multi-column, tables)
- Temporal reasoning (date extraction and ordering)
- Skill taxonomy mapping
- LLM-assisted extraction for complex layouts
- Parallel processing (multiple parser instances)

**Technology Stack**:
- `pdfplumber`, `PyPDF2` for PDF parsing
- `python-docx` for DOCX files
- `spaCy` or `Transformers` for NER
- LLM (GPT-4, Claude) for complex extraction
- `Tesseract` for OCR

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

**Key Capabilities**:
- Intent classification
- Requirement prioritization
- Skill taxonomy normalization
- Seniority level detection
- Industry/domain identification
- Generate scoring rubric

**Technology Stack**:
- LLM for semantic understanding
- Vector embeddings (OpenAI, Cohere)
- Custom prompt templates

### 2.5 Matching Agent (Semantic Matcher)

**Role**: Calculate relevance between CVs and job requirements

**Responsibilities**:
- Semantic similarity matching
- Skill matching with fuzzy logic
- Experience level alignment
- Education requirement matching
- Industry experience matching
- Generate match scores for each criterion
- Identify gaps and strengths

**Key Capabilities**:
- Vector similarity search (cosine, euclidean)
- Multi-dimensional matching
- Weighted scoring based on JD priorities
- Synonym and related skill detection
- Context-aware matching (e.g., "React" implies JavaScript)
- Years of experience calculation

**Technology Stack**:
- Vector database (Pinecone, Weaviate, Qdrant)
- Sentence transformers
- Custom similarity algorithms
- Skill ontology database

### 2.6 Scoring Engine Agent

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

**Key Capabilities**:
- Configurable scoring rules
- Dynamic weight adjustment
- Bias detection and mitigation
- Score calibration
- Threshold-based filtering

### 2.7 Ranking Agent

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

**Key Capabilities**:
- Multi-criteria ranking
- Tie-breaking logic
- Filter pipeline execution
- Tier classification
- Ranking explanations

### 2.8 Explainability Agent

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

**Key Capabilities**:
- Natural language generation
- Comparative analysis
- Visual report generation
- Customizable explanation depth

### 2.9 Report Generator Agent

**Role**: Create comprehensive reports and dashboards

**Responsibilities**:
- Generate PDF/HTML reports
- Create candidate comparison matrices
- Build interactive dashboards
- Export data in multiple formats (CSV, JSON, Excel)
- Send notifications
- Archive results

**Deliverables**:
- Executive summary
- Top 10 candidates list
- Detailed scorecards per candidate
- Gap analysis
- Recommendations
- Diversity metrics

---

## 3. Inter-Agent Communication

### 3.1 Communication Patterns

**Message Queue Architecture**

```
Orchestrator → [Task Queue] → Worker Agents → [Result Queue] → Orchestrator
```

**Technology Choices**:
- **RabbitMQ** or **Redis Streams** for message queuing
- **WebSockets** for real-time progress updates to frontend
- **gRPC** for high-performance synchronous calls (optional)

### 3.2 Message Format

**Standard Message Schema**:
```json
{
  "message_id": "uuid",
  "timestamp": "ISO8601",
  "source_agent": "agent_name",
  "target_agent": "agent_name",
  "message_type": "task|result|error|status",
  "priority": "high|medium|low",
  "payload": {
    "task_id": "uuid",
    "data": {},
    "metadata": {}
  },
  "correlation_id": "uuid",
  "retry_count": 0
}
```

### 3.3 Workflow State Management

**State Machine States**:
1. `INITIALIZED` - Request received
2. `PARSING` - CVs being parsed
3. `ANALYZING_JD` - Job description analysis
4. `MATCHING` - Semantic matching in progress
5. `SCORING` - Score calculation
6. `RANKING` - Final ranking generation
7. `GENERATING_REPORT` - Report creation
8. `COMPLETED` - Process finished
9. `FAILED` - Error occurred

**State Storage**: Redis or PostgreSQL for distributed state

---

## 4. Data Models

### 4.1 CV Data Model (Structured)

```json
{
  "cv_id": "uuid",
  "candidate": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "url"
  },
  "summary": "string",
  "experience": [
    {
      "company": "string",
      "role": "string",
      "start_date": "date",
      "end_date": "date",
      "duration_months": "number",
      "description": "string",
      "key_achievements": ["string"],
      "technologies": ["string"]
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "field": "string",
      "graduation_year": "number",
      "gpa": "number"
    }
  ],
  "skills": {
    "technical": ["string"],
    "soft": ["string"],
    "tools": ["string"],
    "languages": ["string"]
  },
  "certifications": [
    {
      "name": "string",
      "issuer": "string",
      "date": "date"
    }
  ],
  "projects": [
    {
      "name": "string",
      "description": "string",
      "technologies": ["string"],
      "url": "string"
    }
  ],
  "total_experience_years": "number",
  "metadata": {
    "parsed_at": "timestamp",
    "parser_version": "string",
    "confidence_score": "number"
  }
}
```

### 4.2 Job Description Model

```json
{
  "jd_id": "uuid",
  "job_title": "string",
  "company": "string",
  "department": "string",
  "seniority_level": "junior|mid|senior|lead|executive",
  "requirements": {
    "must_have_skills": [
      {
        "skill": "string",
        "weight": "number (0-1)"
      }
    ],
    "nice_to_have_skills": [
      {
        "skill": "string",
        "weight": "number (0-1)"
      }
    ],
    "min_experience_years": "number",
    "education_level": "string",
    "industry_experience": ["string"],
    "certifications": ["string"]
  },
  "responsibilities": ["string"],
  "scoring_weights": {
    "skills": 0.4,
    "experience": 0.3,
    "education": 0.15,
    "career_trajectory": 0.1,
    "other": 0.05
  },
  "embeddings": {
    "full_description": [/* vector */],
    "skills": [/* vector */],
    "responsibilities": [/* vector */]
  }
}
```

### 4.3 Candidate Score Model

```json
{
  "candidate_id": "uuid",
  "cv_id": "uuid",
  "jd_id": "uuid",
  "scores": {
    "total": 85.5,
    "skills_match": 90,
    "experience_relevance": 85,
    "education_fit": 80,
    "career_trajectory": 85,
    "confidence": 0.92
  },
  "matches": {
    "matched_skills": [
      {
        "skill": "Python",
        "cv_proficiency": "expert",
        "jd_requirement": "required",
        "match_score": 100
      }
    ],
    "missing_skills": ["Kubernetes"],
    "extra_skills": ["Go"]
  },
  "strengths": ["string"],
  "weaknesses": ["string"],
  "explanation": "string",
  "rank": "number",
  "tier": "A|B|C|D"
}
```

---

## 5. Technology Stack

### 5.1 Core Technologies

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Programming Language** | Python 3.11+ | Rich ML/NLP ecosystem, async support |
| **Agent Framework** | LangGraph / CrewAI | Built for multi-agent orchestration |
| **LLM Provider** | OpenAI GPT-4o / Anthropic Claude 3.5 | State-of-the-art reasoning and extraction |
| **Vector Database** | Qdrant / Pinecone | Efficient similarity search at scale |
| **Message Queue** | Redis Streams / RabbitMQ | Reliable async communication |
| **Primary Database** | PostgreSQL | Structured data storage, ACID compliance |
| **Cache** | Redis | Fast state storage, session management |
| **Object Storage** | AWS S3 / MinIO | Raw file storage (CVs, reports) |
| **API Framework** | FastAPI | Modern, async, automatic docs |
| **Task Queue** | Celery | Distributed task execution |
| **Containerization** | Docker + Docker Compose | Consistent deployment |
| **Orchestration** | Kubernetes (optional) | Production-grade scaling |
| **Monitoring** | Prometheus + Grafana | Metrics and alerting |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) | Centralized logging |
| **Tracing** | Jaeger / OpenTelemetry | Distributed tracing |

### 5.2 Key Libraries

**NLP & ML**:
- `transformers` - Hugging Face transformers
- `sentence-transformers` - Semantic embeddings
- `spacy` - NER and linguistic analysis
- `langchain` / `langgraph` - Agent orchestration
- `openai` / `anthropic` - LLM APIs

**Document Processing**:
- `pdfplumber` - PDF text extraction
- `python-docx` - Word document parsing
- `pytesseract` - OCR
- `unstructured` - Multi-format parsing

**Data & API**:
- `fastapi` - Web framework
- `pydantic` - Data validation
- `sqlalchemy` - ORM
- `alembic` - Database migrations
- `httpx` - Async HTTP client

**Infrastructure**:
- `celery` - Task queue
- `redis-py` - Redis client
- `psycopg2` - PostgreSQL driver
- `qdrant-client` - Vector database client

---

## 6. System Workflows

### 6.1 End-to-End Ranking Workflow

```
1. REQUEST SUBMISSION
   └─> User uploads CVs + Job Description via API
   
2. INPUT VALIDATION (Input Handler Agent)
   └─> Validate files, store in S3, create task records
   
3. PARALLEL PROCESSING PHASE
   ├─> Parser Agents (parallel): Extract data from CVs
   └─> JD Analyzer Agent: Analyze job requirements
   
4. MATCHING PHASE (Matching Agent)
   └─> For each CV: Calculate semantic similarity
   
5. SCORING PHASE (Scoring Engine Agent)
   └─> Apply scoring formula, normalize scores
   
6. RANKING PHASE (Ranking Agent)
   └─> Sort, filter, tier classification
   
7. EXPLANATION PHASE (Explainability Agent)
   └─> Generate reasons for each ranking
   
8. REPORT GENERATION (Report Generator Agent)
   └─> Create comprehensive reports
   
9. RESPONSE DELIVERY
   └─> Return ranked list + reports to user
```

### 6.2 Error Handling & Resilience

**Retry Strategy**:
- Exponential backoff with jitter
- Max 3 retries per agent task
- Dead letter queue for failed tasks

**Circuit Breaker**:
- Monitor agent failure rates
- Open circuit after 50% failure rate
- Auto-recover after cooldown period

**Graceful Degradation**:
- If LLM unavailable: Use rule-based parsing
- If vector DB down: Use keyword matching
- Partial results better than no results

---

## 7. Scalability & Performance

### 7.1 Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| **Throughput** | 50 CVs in < 5 minutes | With 10 parser agents |
| **Latency (single CV)** | < 10 seconds | End-to-end processing |
| **Concurrent Requests** | 100+ | API gateway limit |
| **Vector Search** | < 100ms | Per CV matching |
| **API Response Time** | < 200ms | Status check endpoints |

### 7.2 Scaling Strategy

**Horizontal Scaling**:
- Parser Agents: Scale to N instances based on queue depth
- Matching Agents: Replicate for parallel processing
- API Gateway: Load balancer across multiple instances

**Vertical Scaling**:
- Vector DB: GPU-accelerated for large embedding searches
- LLM Inference: Dedicated GPU instances

**Caching Strategy**:
- Cache parsed CVs (1 hour TTL)
- Cache JD analysis (24 hour TTL)
- Cache skill embeddings (permanent)

---

## 8. Security & Privacy

### 8.1 Data Protection

- **Encryption at Rest**: AES-256 for stored CVs
- **Encryption in Transit**: TLS 1.3 for all communication
- **PII Redaction**: Option to anonymize candidate data
- **Access Control**: RBAC for API endpoints
- **Audit Logging**: Track all data access

### 8.2 Compliance

- **GDPR**: Right to erasure, data portability
- **CCPA**: Privacy notices, opt-out mechanisms
- **SOC 2**: Security controls and monitoring

### 8.3 API Security

- **Authentication**: OAuth 2.0 / JWT tokens
- **Rate Limiting**: Token bucket algorithm
- **Input Validation**: Strict schema validation
- **File Upload Limits**: Max 10MB per CV, virus scanning

---

## 9. Monitoring & Observability

### 9.1 Key Metrics

**Business Metrics**:
- CVs processed per hour
- Average ranking time
- User satisfaction scores
- API usage patterns

**Technical Metrics**:
- Agent success/failure rates
- Queue depth and lag
- API latency (p50, p95, p99)
- LLM API costs
- Database query performance
- Cache hit rates

**Quality Metrics**:
- Parsing accuracy (sampled validation)
- Ranking consistency (A/B tests)
- Score distribution analysis
- User feedback on rankings

### 9.2 Alerting

**Critical Alerts**:
- Agent failure rate > 10%
- Queue depth > 1000
- API error rate > 5%
- Database connection failures

**Warning Alerts**:
- Processing time > 2x baseline
- Cache hit rate < 70%
- Disk space < 20%

---

## 10. Deployment Architecture

### 10.1 Development Environment

```
docker-compose.yml:
  - API Gateway (FastAPI)
  - Orchestrator Agent
  - 3x Parser Agents
  - Other specialized agents
  - PostgreSQL
  - Redis
  - Qdrant (vector DB)
  - MinIO (S3-compatible)
```

### 10.2 Production Environment (AWS)

```
- ECS/EKS: Container orchestration
- ALB: Load balancing
- RDS PostgreSQL: Primary database
- ElastiCache Redis: Caching & queues
- S3: File storage
- SageMaker: LLM inference (optional)
- CloudWatch: Monitoring
- Secrets Manager: Credential management
```

### 10.3 CI/CD Pipeline

```
1. Code push to GitHub
2. GitHub Actions triggers
3. Run tests (pytest)
4. Build Docker images
5. Push to ECR
6. Deploy to staging
7. Run integration tests
8. Manual approval
9. Deploy to production
```

---

## 11. Future Enhancements

### 11.1 Phase 2 Features

1. **Active Learning Agent**
   - Learn from recruiter feedback
   - Adjust scoring weights dynamically
   - Improve matching accuracy over time

2. **Interview Scheduling Agent**
   - Auto-schedule top candidates
   - Calendar integration
   - Email automation

3. **Video Analysis Agent**
   - Analyze video resumes
   - Speech-to-text for interviews
   - Sentiment analysis

4. **Diversity & Inclusion Agent**
   - Bias detection in rankings
   - Diversity metrics tracking
   - Blind screening options

5. **Market Intelligence Agent**
   - Salary benchmarking
   - Skill demand trends
   - Competitive analysis

### 11.2 Advanced Capabilities

- **Multi-modal Analysis**: Process video resumes, GitHub profiles
- **Real-time Ranking**: Stream processing for instant results
- **Federated Learning**: Privacy-preserving model updates
- **Explainable AI**: SHAP/LIME for scoring transparency
- **Custom Skill Ontologies**: Industry-specific taxonomies

---

## 12. Cost Estimation

### 12.1 Infrastructure Costs (Monthly, 10K CVs)

| Service | Cost | Notes |
|---------|------|-------|
| **Compute (ECS/EKS)** | $500 | 10 containers, t3.medium |
| **Database (RDS)** | $200 | db.t3.medium |
| **Redis (ElastiCache)** | $50 | cache.t3.micro |
| **S3 Storage** | $30 | 100GB |
| **Vector DB (Qdrant Cloud)** | $100 | 1M vectors |
| **LLM API (OpenAI)** | $300 | ~500K tokens/day |
| **Data Transfer** | $50 | Outbound traffic |
| **Monitoring** | $50 | CloudWatch, Grafana Cloud |
| **Total** | **~$1,280/month** | |

### 12.2 Cost Optimization

- Use open-source LLMs (Llama 3.1, Mistral) for parsing
- Cache embeddings and parsed results
- Batch API calls to LLM providers
- Reserved instances for compute

---

## 13. Success Metrics

### 13.1 Technical KPIs

- ✅ 99.5% uptime
- ✅ < 5 min processing time for 50 CVs
- ✅ < 0.1% error rate
- ✅ 90%+ parsing accuracy

### 13.2 Business KPIs

- ✅ 70% reduction in manual screening time
- ✅ 85%+ recruiter satisfaction
- ✅ Top 5 ranked candidates include 80%+ interview-worthy profiles
- ✅ 50%+ time-to-hire improvement

---

## 14. Risk Analysis & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **LLM API downtime** | High | Medium | Fallback to rule-based parsing |
| **Poor parsing accuracy** | High | Medium | Human-in-the-loop validation |
| **Bias in rankings** | High | Medium | Fairness audits, blind screening |
| **Data privacy breach** | Critical | Low | Encryption, access controls, audits |
| **Scalability bottlenecks** | Medium | Medium | Load testing, auto-scaling |
| **High API costs** | Medium | High | Cost monitoring, usage caps |

---

## 15. Implementation Roadmap

### Phase 1: MVP (8 weeks)
- ✅ Week 1-2: Core agent framework setup
- ✅ Week 3-4: Parser + JD Analyzer agents
- ✅ Week 5-6: Matching + Scoring agents
- ✅ Week 7: Ranking + basic reports
- ✅ Week 8: API + testing

### Phase 2: Production Ready (6 weeks)
- ✅ Week 9-10: Explainability agent
- ✅ Week 11-12: Security + monitoring
- ✅ Week 13-14: Performance optimization
- ✅ Week 15: Load testing + deployment

### Phase 3: Enhancements (Ongoing)
- Active learning integration
- Advanced analytics
- Mobile app
- Integration with ATS systems

---

## 16. Conclusion

This multi-agent architecture provides a scalable, intelligent, and explainable solution for automated CV ranking. By leveraging specialized agents with clear responsibilities, the system can efficiently process large volumes of CVs while maintaining high accuracy and providing transparency into ranking decisions.

The design emphasizes:
- **Modularity**: Each agent is independently deployable and upgradeable
- **Scalability**: Horizontal scaling for high throughput
- **Reliability**: Fault tolerance and graceful degradation
- **Explainability**: Clear reasoning for every ranking decision
- **Privacy**: Strong security controls for sensitive candidate data

**Next Steps**: Review this specification, gather stakeholder feedback, and proceed with Phase 1 implementation.

---

## Appendix A: Technology Alternatives

### Alternative Agent Frameworks
- **AutoGen** (Microsoft): Multi-agent conversations
- **LangGraph**: Graph-based agent orchestration
- **CrewAI**: Role-based agent framework
- **Custom**: Built on Celery + Redis

### Alternative LLM Providers
- **OpenAI GPT-4**: Best reasoning, expensive
- **Anthropic Claude 3.5**: Strong at analysis, good cost
- **Google Gemini Pro**: Multimodal, competitive pricing
- **Open Source**: Llama 3.1 70B, Mistral Large (self-hosted)

### Alternative Vector Databases
- **Pinecone**: Managed, easy to use
- **Weaviate**: Open source, GraphQL API
- **Qdrant**: Fast, Rust-based, affordable
- **Milvus**: Highly scalable, complex setup

---

## Appendix B: Sample API Endpoints

```
POST   /api/v1/rankings                 # Create new ranking job
GET    /api/v1/rankings/{job_id}        # Get ranking status
GET    /api/v1/rankings/{job_id}/results # Get final rankings
POST   /api/v1/cvs/upload                # Upload CV files
POST   /api/v1/job-descriptions          # Submit job description
GET    /api/v1/candidates/{id}/scorecard # Get detailed scorecard
GET    /api/v1/reports/{job_id}/pdf      # Download PDF report
POST   /api/v1/feedback                  # Submit ranking feedback
GET    /api/v1/health                    # System health check
```

---

**Document Version**: 1.0  
**Last Updated**: November 8, 2025  
**Author**: Resume.AI Architecture Team  
**Status**: Draft for Review

