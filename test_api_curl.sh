#!/bin/bash
# Comprehensive API testing script using curl

echo "=========================================="
echo "🧪 Resume.AI API Testing with curl"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0.32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_BASE="http://localhost:8004"

# Test 1: Health Check
echo "📍 Test 1: Health Check"
echo "----------------------------------------"
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_BASE/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "Response: $RESPONSE_BODY"
else
    echo -e "${RED}❌ Health check failed (HTTP $HTTP_CODE)${NC}"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

# Test 2: Create Ranking Job with 3 resumes
echo "📍 Test 2: Create Ranking Job (3 resumes)"
echo "----------------------------------------"

# Get first 3 resume files
RESUME_DIR="data/resumes"
RESUMES=($(ls $RESUME_DIR/*.pdf | head -3))

if [ ${#RESUMES[@]} -eq 0 ]; then
    echo -e "${RED}❌ No resume files found in $RESUME_DIR${NC}"
    exit 1
fi

echo "Using resumes:"
for resume in "${RESUMES[@]}"; do
    echo "  - $(basename $resume)"
done
echo ""

# Create the curl command with multiple file uploads
CURL_CMD="curl -s -w \"\nHTTP_CODE:%{http_code}\" -X POST \"$API_BASE/api/v1/ranking_jobs/create\""
CURL_CMD="$CURL_CMD -F \"job_description=We are seeking a Senior Python Backend Developer with 5+ years of experience. Must have expertise in FastAPI, Django, PostgreSQL, Redis, and AWS. Strong knowledge of Docker and microservices architecture required.\""
CURL_CMD="$CURL_CMD -F \"job_title=Senior Python Backend Developer\""
CURL_CMD="$CURL_CMD -F \"company=TechCorp Inc.\""

for resume in "${RESUMES[@]}"; do
    CURL_CMD="$CURL_CMD -F \"cv_files=@$resume\""
done

# Execute the curl command
CREATE_RESPONSE=$(eval $CURL_CMD)
HTTP_CODE=$(echo "$CREATE_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$CREATE_RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Ranking job created successfully${NC}"
    echo "Response:"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    
    # Extract job ID
    JOB_ID=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('jobId', ''))" 2>/dev/null)
    
    if [ -n "$JOB_ID" ]; then
        echo ""
        echo -e "${GREEN}Job ID: $JOB_ID${NC}"
        
        # Test 3: Check Job Status
        echo ""
        echo "📍 Test 3: Check Job Status"
        echo "----------------------------------------"
        sleep 2
        
        STATUS_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_BASE/api/v1/ranking_jobs/$JOB_ID/status")
        HTTP_CODE=$(echo "$STATUS_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
        RESPONSE_BODY=$(echo "$STATUS_RESPONSE" | sed '/HTTP_CODE/d')
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✅ Status check successful${NC}"
            echo "Response:"
            echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
        else
            echo -e "${RED}❌ Status check failed (HTTP $HTTP_CODE)${NC}"
            echo "Response: $RESPONSE_BODY"
        fi
        
        # Test 4: Monitor job until completion (max 2 minutes)
        echo ""
        echo "📍 Test 4: Monitor Job Progress"
        echo "----------------------------------------"
        MAX_WAIT=120
        ELAPSED=0
        CHECK_INTERVAL=5
        
        while [ $ELAPSED -lt $MAX_WAIT ]; do
            sleep $CHECK_INTERVAL
            ELAPSED=$((ELAPSED + CHECK_INTERVAL))
            
            STATUS_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/ranking_jobs/$JOB_ID/status")
            STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('status', 'unknown'))" 2>/dev/null)
            
            echo "[$ELAPSED s] Status: $STATUS"
            
            if [ "$STATUS" = "completed" ]; then
                echo -e "${GREEN}✅ Job completed successfully!${NC}"
                break
            elif [ "$STATUS" = "failed" ]; then
                echo -e "${RED}❌ Job failed${NC}"
                break
            fi
        done
        
        if [ $ELAPSED -ge $MAX_WAIT ]; then
            echo -e "${YELLOW}⏰ Timeout reached (${MAX_WAIT}s)${NC}"
        fi
        
        # Test 5: Get Results
        echo ""
        echo "📍 Test 5: Get Job Results"
        echo "----------------------------------------"
        
        RESULTS_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X GET "$API_BASE/api/v1/ranking_jobs/$JOB_ID/results")
        HTTP_CODE=$(echo "$RESULTS_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
        RESPONSE_BODY=$(echo "$RESULTS_RESPONSE" | sed '/HTTP_CODE/d')
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✅ Results retrieved successfully${NC}"
            echo "Response:"
            echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
            
            # Save to file
            echo "$RESPONSE_BODY" > "ranking_results_${JOB_ID}.json"
            echo ""
            echo -e "${GREEN}💾 Full results saved to: ranking_results_${JOB_ID}.json${NC}"
        else
            echo -e "${RED}❌ Failed to retrieve results (HTTP $HTTP_CODE)${NC}"
            echo "Response: $RESPONSE_BODY"
        fi
    fi
else
    echo -e "${RED}❌ Failed to create ranking job (HTTP $HTTP_CODE)${NC}"
    echo "Response: $RESPONSE_BODY"
fi

echo ""
echo "=========================================="
echo "✅ API Testing Complete"
echo "=========================================="

