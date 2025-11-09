<<<<<<< HEAD
# Resume.AI - Multi-Agent CV Ranking System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent multi-agent system that automatically ranks 50+ CVs based on job descriptions using AI-powered semantic matching and scoring.

## 🌟 Features

- **Intelligent CV Parsing**: Extracts structured data from PDFs, DOCX, and TXT files
- **Semantic Matching**: Uses LLM embeddings for deep understanding of skills and experience
- **Multi-Agent Architecture**: Specialized agents for parsing, matching, scoring, and ranking
- **RESTful API**: Easy-to-use API for integration with existing systems
- **Scalable Design**: Process 50 CVs in under 5 minutes
- **Explainable Results**: Provides detailed reasoning for each ranking
- **Tier Classification**: Automatically categorizes candidates into A, B, C, D tiers

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                         │
│                    (REST API + WebSocket)                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │  Orchestrator Agent   │
                    └───────────┬───────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼─────────┐  ┌─────────▼──────────┐  ┌────────▼────────┐
│  Parser Agent   │  │  JD Analyzer Agent │  │ Matching Agent  │
└─────────────────┘  └────────────────────┘  └─────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼─────────┐          ┌─────────▼──────────┐
        │  Scoring Agent  │          │  Ranking Agent     │
        └─────────────────┘          └────────────────────┘
```

## 📋 Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- OpenAI API key or Anthropic API key

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd resume.ai
```

> **📊 Have a CV Dataset?** If you have a CSV file with resumes (like the included `data/cvs/dataset.csv`), see [DATASET_USAGE.md](DATASET_USAGE.md) for instructions on using it directly.

### 2. Set Up Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Install Dependencies

#### Option A: Using Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

#### Option B: Using Docker

```bash
docker-compose up --build
```

### 4. Run the Application

#### Without Docker:

```bash
# From project root
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### With Docker:

```bash
docker-compose up
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📖 Usage

### API Endpoints

#### 1. Create Ranking Job

```bash
curl -X POST "http://localhost:8000/api/v1/rankings" \
  -F "job_description=We are looking for a Senior Python Developer..." \
  -F "job_title=Senior Python Developer" \
  -F "company=Tech Corp" \
  -F "cv_files=@/path/to/cv1.pdf" \
  -F "cv_files=@/path/to/cv2.pdf"
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Ranking job created with 2 CVs. Processing in background."
}
```

#### 2. Check Job Status

```bash
curl "http://localhost:8000/api/v1/rankings/{job_id}"
```

#### 3. Get Results

```bash
curl "http://localhost:8000/api/v1/rankings/{job_id}/results"
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_title": "Senior Python Developer",
  "total_candidates": 50,
  "tier_distribution": {
    "A": 8,
    "B": 15,
    "C": 20,
    "D": 7
  },
  "candidates": [
    {
      "rank": 1,
      "candidate_name": "John Doe",
      "tier": "A",
      "total_score": 92.5,
      "skills_score": 95.0,
      "experience_score": 90.0,
      "education_score": 85.0,
      "strengths": [
        "Strong match on required skills: Python, AWS, Docker",
        "10 years of experience (exceeds requirement)"
      ],
      "weaknesses": [],
      "explanation": "Excellent match for this position. Strengths: Strong match on required skills..."
    }
  ]
}
```

### Python SDK Example

```python
import requests

# Create ranking job
files = [
    ('cv_files', open('cv1.pdf', 'rb')),
    ('cv_files', open('cv2.pdf', 'rb'))
]

data = {
    'job_description': 'We need a Python developer with 5+ years experience...',
    'job_title': 'Senior Python Developer',
    'company': 'Tech Corp'
}

response = requests.post(
    'http://localhost:8000/api/v1/rankings',
    files=files,
    data=data
)

job_id = response.json()['job_id']

# Check status
import time
while True:
    status_response = requests.get(
        f'http://localhost:8000/api/v1/rankings/{job_id}'
    )
    status = status_response.json()['status']
    
    if status == 'completed':
        break
    elif status == 'failed':
        print("Job failed!")
        break
    
    time.sleep(5)

# Get results
results = requests.get(
    f'http://localhost:8000/api/v1/rankings/{job_id}/results'
).json()

print(f"Top candidate: {results['candidates'][0]['candidate_name']}")
print(f"Score: {results['candidates'][0]['total_score']}")
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## 📁 Project Structure

```
resume.ai/
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── base_agent.py
│   │   ├── parser_agent.py
│   │   ├── jd_analyzer_agent.py
│   │   ├── matching_agent.py
│   │   ├── scoring_agent.py
│   │   ├── ranking_agent.py
│   │   └── orchestrator_agent.py
│   ├── api/                 # FastAPI application
│   │   └── main.py
│   ├── models/              # Data models
│   │   └── schemas.py
│   ├── services/            # Services (database, cache)
│   │   └── database.py
│   ├── utils/               # Utilities
│   │   ├── llm_client.py
│   │   └── helpers.py
│   └── config/              # Configuration
│       └── settings.py
├── data/                    # Data storage
│   ├── cvs/                 # Uploaded CVs
│   └── reports/             # Generated reports
├── tests/                   # Test files
├── logs/                    # Log files
├── docker-compose.yml       # Docker Compose config
├── Dockerfile               # Docker image
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── DESIGN_SPECIFICATION.md  # Detailed architecture
└── README.md               # This file
```

## ⚙️ Configuration

Key configuration options in `.env`:

```env
# LLM Provider
OPENAI_API_KEY=your_key
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/resume_ai
REDIS_URL=redis://localhost:6379/0

# Vector Database
QDRANT_URL=http://localhost:6333

# Application
MAX_UPLOAD_SIZE_MB=10
ALLOWED_EXTENSIONS=.pdf,.docx,.txt

# Scoring Weights
WEIGHT_SKILLS=0.4
WEIGHT_EXPERIENCE=0.3
WEIGHT_EDUCATION=0.15
WEIGHT_CAREER=0.1
```

## 🔧 Advanced Configuration

### Custom Scoring Weights

Adjust scoring weights based on role requirements:

```python
# For skill-heavy roles (e.g., Senior Engineer)
WEIGHT_SKILLS=0.5
WEIGHT_EXPERIENCE=0.3
WEIGHT_EDUCATION=0.1
WEIGHT_CAREER=0.1

# For leadership roles (e.g., Engineering Manager)
WEIGHT_SKILLS=0.3
WEIGHT_EXPERIENCE=0.3
WEIGHT_EDUCATION=0.1
WEIGHT_CAREER=0.3
```

### Using Different LLM Providers

The system supports OpenAI and Anthropic:

```python
# OpenAI (default)
OPENAI_API_KEY=your_key
LLM_MODEL=gpt-4o-mini

# Anthropic Claude
ANTHROPIC_API_KEY=your_key
LLM_MODEL=claude-3-5-sonnet-20241022
```

## 📊 Performance

- **Throughput**: 50 CVs in < 5 minutes
- **Latency**: Single CV processing in ~10 seconds
- **Accuracy**: 90%+ parsing accuracy
- **Scalability**: Horizontal scaling with multiple parser agents

## 🛡️ Security

- TLS encryption for API endpoints
- API key authentication
- File upload validation
- Size limits on uploads
- Sandboxed file processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**1. LLM API Errors**
- Ensure your API key is valid
- Check API rate limits
- Verify network connectivity

**2. PDF Parsing Issues**
- Some scanned PDFs may require OCR
- Complex layouts might need manual review
- Try converting to text format first

**3. Memory Issues**
- Reduce batch size for large CV sets
- Increase Docker memory allocation
- Use pagination for results

### Getting Help

- Check the [DESIGN_SPECIFICATION.md](DESIGN_SPECIFICATION.md) for architecture details
- Open an issue on GitHub
- Contact: support@resume.ai (example)

## 🗺️ Roadmap

- [ ] Active learning from recruiter feedback
- [ ] Video resume analysis
- [ ] Interview scheduling integration
- [ ] Bias detection and mitigation
- [ ] Mobile app
- [ ] ATS system integrations
- [ ] Real-time ranking with WebSocket

## 📚 Documentation

- [Design Specification](DESIGN_SPECIFICATION.md) - Detailed architecture and design decisions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- LLM integration via [LangChain](https://langchain.com/)
- Document parsing with [pdfplumber](https://github.com/jsvine/pdfplumber)
- Vector search with [Qdrant](https://qdrant.tech/)

---

**Made with ❤️ by the Resume.AI Team**

=======
# FastMVC
MVC Pattern FastAPI Design
>>>>>>> fastmvc/main
