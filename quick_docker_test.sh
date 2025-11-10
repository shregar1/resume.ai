#!/bin/bash
# Quick Docker API Test

echo "🐳 Resume.AI Docker API Quick Test"
echo "===================================="
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Endpoint..."
HEALTH=$(curl -s http://localhost:8004/health)
if echo "$HEALTH" | grep -q "ok"; then
    echo "✅ Health check passed: $HEALTH"
else
    echo "❌ Health check failed"
    exit 1
fi
echo ""

# Test 2: Simple Job Creation
echo "2️⃣  Testing Job Creation (1 resume)..."
RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/ranking_jobs/create" \
  -F "job_description=Looking for Python developer" \
  -F "job_title=Python Dev" \
  -F "company=Test Co" \
  -F "cv_files=@data/resumes/00782d2a-6c8d-41e6-ab7b-d26bce182086.pdf")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if job was created
if echo "$RESPONSE" | grep -q "SUCCESS\|jobId"; then
    echo "✅ Job creation successful!"
    JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('jobId', ''))" 2>/dev/null)
    echo "Job ID: $JOB_ID"
else
    echo "⚠️  Job creation returned an error"
fi

echo ""
echo "===================================="
echo "Docker containers status:"
docker-compose ps 2>/dev/null || docker ps | grep resumeai

