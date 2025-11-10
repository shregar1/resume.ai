#!/bin/bash

echo "================================================================================"
echo "🧪 Testing API with 2 Diverse Samples (Python + Non-Python)"
echo "================================================================================"
echo ""

# API endpoint
API_URL="http://localhost:8004"

# Check API health
echo "📍 Checking API health..."
HEALTH=$(curl -s ${API_URL}/health)
if [ $? -ne 0 ]; then
    echo "❌ API is not running. Please start it with: docker-compose up -d"
    exit 1
fi
echo "✅ API is healthy"
echo ""

# Select 2 diverse resumes
RESUME_DIR="data/resumes"
RESUME1="${RESUME_DIR}/1.pdf"
RESUME2="${RESUME_DIR}/2.pdf"

if [ ! -f "$RESUME1" ] || [ ! -f "$RESUME2" ]; then
    echo "❌ Resume files not found"
    exit 1
fi

echo "📄 Selected resumes:"
echo "  1. $(basename $RESUME1)"
echo "  2. $(basename $RESUME2)"
echo ""

# Job description for Python developer
JOB_TITLE="Senior Python Developer"
COMPANY="Tech Innovations Inc"
JOB_DESC="We are seeking a Senior Python Developer with 5+ years of experience in Python, FastAPI, Django, and machine learning. The ideal candidate should have strong experience with RESTful APIs, microservices architecture, Docker, and cloud platforms (AWS/GCP). Experience with data science libraries (pandas, numpy, scikit-learn) is a plus. Strong problem-solving skills and ability to work in an agile team environment required."

echo "================================================================================"
echo "🚀 Creating Ranking Job"
echo "================================================================================"
echo ""
echo "Job Title: $JOB_TITLE"
echo "Company: $COMPANY"
echo ""

# Submit job
RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/ranking_jobs/create \
    -F "job_title=${JOB_TITLE}" \
    -F "company=${COMPANY}" \
    -F "job_description=${JOB_DESC}" \
    -F "cv_files=@${RESUME1}" \
    -F "cv_files=@${RESUME2}")

# Extract job ID
JOB_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['jobId'])" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to create job"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Job created successfully!"
echo "Job ID: $JOB_ID"
echo ""

echo "================================================================================"
echo "📊 Monitoring Logs (Press Ctrl+C to stop)"
echo "================================================================================"
echo ""
echo "Watch for:"
echo "  🚀 Job start"
echo "  📋 Phase 1: JD Analysis"
echo "  📄 Phase 2: CV Parsing"
echo "  🔍 Phase 3: Matching & Scoring"
echo "  🏆 Phase 4: Ranking"
echo "  🎉 Job completion"
echo "  🤖 LLM calls"
echo ""
echo "Starting log monitor in 2 seconds..."
sleep 2

# Monitor logs with filtering
docker logs -f resumeai-fastapi-1 2>&1 | grep --line-buffered -E "🚀|📋|📄|🔍|🏆|🎉|🤖|🧮|✅|❌|⚠️|PHASE|Parsing CV|LLM|embeddings|JOB COMPLETED|Total Candidates|Tier Distribution" &
LOG_PID=$!

# Wait for job to complete
echo ""
echo "Waiting for job to complete..."
sleep 5

MAX_WAIT=120
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS_RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/ranking_jobs/${JOB_ID}/status)
    STATUS=$(echo $STATUS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null)
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "✅ Job completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo "❌ Job failed"
        break
    fi
    
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

# Stop log monitoring
kill $LOG_PID 2>/dev/null

echo ""
echo "================================================================================"
echo "📈 Fetching Results"
echo "================================================================================"
echo ""

# Get results
RESULTS=$(curl -s ${API_URL}/api/v1/ranking_jobs/${JOB_ID}/results)

# Save results
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="test_results_2samples_${JOB_ID}_${TIMESTAMP}.json"
echo "$RESULTS" > "$RESULTS_FILE"

# Parse and display results
echo "$RESULTS" | python3 << 'PYTHON_EOF'
import json
import sys

try:
    data = json.load(sys.stdin)
    
    if data.get("success"):
        result_data = data.get("data", {})
        candidates = result_data.get("ranked_candidates", [])
        
        print("✅ Results retrieved successfully")
        print("")
        print("="*80)
        print("🏆 Ranking Results")
        print("="*80)
        print("")
        print(f"Total Candidates: {len(candidates)}")
        print("")
        
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. {candidate.get('name', 'Unknown')}")
            print(f"   Tier: {candidate.get('tier', 'N/A')}")
            print(f"   Total Score: {candidate.get('total_score', 0):.2f}")
            
            scores = candidate.get('scores', {})
            print(f"   Skills: {scores.get('skills_match', 0):.2f} | " +
                  f"Experience: {scores.get('experience_match', 0):.2f} | " +
                  f"Education: {scores.get('education_match', 0):.2f}")
            
            # Show key skills
            cv_data = candidate.get('cv_data', {})
            skills = cv_data.get('skills', {})
            tech_skills = skills.get('technical', [])
            if tech_skills:
                print(f"   Key Skills: {', '.join(tech_skills[:5])}")
            
            print("")
        
        print("="*80)
    else:
        print("❌ Failed to retrieve results")
        print(json.dumps(data, indent=2))

except Exception as e:
    print(f"Error parsing results: {e}")
    sys.exit(1)
PYTHON_EOF

echo ""
echo "================================================================================"
echo "📊 Summary"
echo "================================================================================"
echo ""
echo "  Job ID: $JOB_ID"
echo "  Resumes Tested: 2"
echo "  Results File: $RESULTS_FILE"
echo ""
echo "To view full logs:"
echo "  docker logs resumeai-fastapi-1 2>&1 | grep '$JOB_ID'"
echo ""
echo "================================================================================"
echo "✅ Test Complete!"
echo "================================================================================"
