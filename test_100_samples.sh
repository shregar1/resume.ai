#!/bin/bash
# Test Resume.AI API with N random resume samples using curl
# Usage: ./test_100_samples.sh [NUM_SAMPLES]
# Example: ./test_100_samples.sh 50

set -e

API_BASE="http://localhost:8004"
RESUME_DIR="data/resumes"

# Get number of samples from command line argument, default to 100
NUM_SAMPLES=${1:-100}

# Validate that NUM_SAMPLES is a positive integer
if ! [[ "$NUM_SAMPLES" =~ ^[0-9]+$ ]] || [ "$NUM_SAMPLES" -lt 1 ]; then
    echo "Error: NUM_SAMPLES must be a positive integer"
    echo "Usage: $0 [NUM_SAMPLES]"
    echo "Example: $0 50"
    exit 1
fi

JOB_DESCRIPTION="We are seeking a Senior Python Backend Developer with 5+ years of experience. Must have expertise in FastAPI, Django, PostgreSQL, Redis, and AWS. Strong knowledge of Docker, microservices architecture, and RESTful API design required. Experience with LLM integration and vector databases is a plus."
JOB_TITLE="Senior Python Backend Developer"
COMPANY="TechCorp Inc."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================================"
echo "🧪 Resume.AI API - Testing with $NUM_SAMPLES Random Samples"
echo "================================================================================"
echo ""

# Check if API is running
echo "📍 Checking API health..."
if ! curl -s "$API_BASE/health" | grep -q "ok"; then
    echo -e "${RED}❌ API is not running. Please start it with: docker-compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API is healthy${NC}"
echo ""

# Get all resume files
ALL_RESUMES=($(ls $RESUME_DIR/*.pdf 2>/dev/null))
TOTAL_RESUMES=${#ALL_RESUMES[@]}

if [ $TOTAL_RESUMES -eq 0 ]; then
    echo -e "${RED}❌ No resume files found in $RESUME_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Found $TOTAL_RESUMES resume files${NC}"

# Determine how many to use
if [ $TOTAL_RESUMES -lt $NUM_SAMPLES ]; then
    echo -e "${YELLOW}⚠️  Only $TOTAL_RESUMES resumes available, will use all of them${NC}"
    NUM_SAMPLES=$TOTAL_RESUMES
else
    echo -e "${GREEN}✅ Will randomly select $NUM_SAMPLES resumes${NC}"
fi
echo ""

# Shuffle and select random resumes (macOS compatible)
SELECTED_RESUMES=($(printf '%s\n' "${ALL_RESUMES[@]}" | sort -R | head -n $NUM_SAMPLES))

echo "================================================================================"
echo "🚀 Creating Ranking Job with $NUM_SAMPLES Resume(s)"
echo "================================================================================"
echo ""

# Build curl command with all selected resumes
CURL_CMD="curl -s -w \"\nHTTP_CODE:%{http_code}\" -X POST \"$API_BASE/api/v1/ranking_jobs/create\""
CURL_CMD="$CURL_CMD -F \"job_description=$JOB_DESCRIPTION\""
CURL_CMD="$CURL_CMD -F \"job_title=$JOB_TITLE\""
CURL_CMD="$CURL_CMD -F \"company=$COMPANY\""

echo "📄 Adding resume files..."
for resume in "${SELECTED_RESUMES[@]}"; do
    CURL_CMD="$CURL_CMD -F \"cv_files=@$resume\""
    echo "  - $(basename $resume)"
done
echo ""

# Execute the curl command
echo "⏳ Submitting job to API (this may take a moment)..."
START_TIME=$(date +%s)
CREATE_RESPONSE=$(eval $CURL_CMD)
HTTP_CODE=$(echo "$CREATE_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$CREATE_RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}❌ Job creation failed (HTTP $HTTP_CODE)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi

echo -e "${GREEN}✅ Job created successfully!${NC}"
echo ""

# Extract job ID
JOB_ID=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('jobId', ''))" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
    echo -e "${RED}❌ Failed to extract job ID${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi

echo "================================================================================"
echo "📊 Job Details"
echo "================================================================================"
echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
echo ""
echo -e "${BLUE}Job ID: $JOB_ID${NC}"
echo ""

# Monitor job progress
echo "================================================================================"
echo "⏳ Monitoring Job Progress"
echo "================================================================================"
echo ""

MAX_WAIT=600  # 10 minutes max
ELAPSED=0
CHECK_INTERVAL=5
LAST_STATUS=""

while [ $ELAPSED -lt $MAX_WAIT ]; do
    sleep $CHECK_INTERVAL
    ELAPSED=$((ELAPSED + CHECK_INTERVAL))
    
    STATUS_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/ranking_jobs/$JOB_ID/status" 2>/dev/null)
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('status', 'unknown'))" 2>/dev/null)
    
    if [ "$STATUS" != "$LAST_STATUS" ]; then
        echo "[$(date '+%H:%M:%S')] Status changed: $LAST_STATUS → $STATUS"
        LAST_STATUS="$STATUS"
    else
        echo "[$(date '+%H:%M:%S')] Status: $STATUS (${ELAPSED}s elapsed)"
    fi
    
    if [ "$STATUS" = "completed" ]; then
        END_TIME=$(date +%s)
        TOTAL_TIME=$((END_TIME - START_TIME))
        echo ""
        echo -e "${GREEN}✅ Job completed successfully in ${TOTAL_TIME}s!${NC}"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo -e "${RED}❌ Job failed${NC}"
        echo "Status details:"
        echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
        exit 1
    fi
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo ""
    echo -e "${YELLOW}⏰ Timeout reached (${MAX_WAIT}s)${NC}"
    echo "Job may still be processing. Check status manually:"
    echo "  curl -X POST \"$API_BASE/api/v1/ranking_jobs/$JOB_ID/status\""
    exit 1
fi

# Fetch results
echo ""
echo "================================================================================"
echo "📈 Fetching Results"
echo "================================================================================"
echo ""

RESULTS_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X GET "$API_BASE/api/v1/ranking_jobs/$JOB_ID/results" 2>/dev/null)
HTTP_CODE=$(echo "$RESULTS_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$RESULTS_RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}❌ Failed to retrieve results (HTTP $HTTP_CODE)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi

echo -e "${GREEN}✅ Results retrieved successfully${NC}"
echo ""

# Parse and display results
TOTAL_CANDIDATES=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('totalCandidates', 0))" 2>/dev/null)

echo "================================================================================"
echo "🏆 Ranking Results Summary"
echo "================================================================================"
echo ""
echo "Total Candidates Processed: $TOTAL_CANDIDATES"
echo ""

# Display top 10 candidates
echo "Top 10 Candidates:"
echo "-------------------"
echo "$RESPONSE_BODY" | python3 << 'EOF'
import sys
import json

try:
    data = json.load(sys.stdin)
    candidates = data.get('data', {}).get('candidates', [])
    
    for i, candidate in enumerate(candidates[:10], 1):
        print(f"\n{i}. {candidate.get('candidateName', 'Unknown')}")
        print(f"   Tier: {candidate.get('tier', 'N/A')}")
        print(f"   Total Score: {candidate.get('totalScore', 0):.2f}")
        print(f"   Skills: {candidate.get('skillsScore', 0):.2f} | Experience: {candidate.get('experienceScore', 0):.2f} | Education: {candidate.get('educationScore', 0):.2f}")
        
        strengths = candidate.get('strengths', [])
        if strengths:
            print(f"   Strengths: {', '.join(strengths[:3])}")
except Exception as e:
    print(f"Error parsing results: {e}")
EOF

echo ""
echo "================================================================================"

# Save full results
OUTPUT_FILE="test_results_${JOB_ID}_$(date +%Y%m%d_%H%M%S).json"
echo "$RESPONSE_BODY" | python3 -m json.tool > "$OUTPUT_FILE" 2>/dev/null

echo ""
echo -e "${GREEN}💾 Full results saved to: $OUTPUT_FILE${NC}"
echo ""

# Final statistics
echo "================================================================================"
echo "📊 Test Statistics"
echo "================================================================================"
echo ""
echo "  Resumes Processed: $NUM_SAMPLES"
echo "  Total Time: ${TOTAL_TIME}s"
echo "  Average Time per Resume: $((TOTAL_TIME / NUM_SAMPLES))s"
echo "  Job ID: $JOB_ID"
echo "  Results File: $OUTPUT_FILE"
echo ""
echo "================================================================================"
echo -e "${GREEN}✅ Test Completed Successfully!${NC}"
echo "================================================================================"

