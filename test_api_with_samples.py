#!/usr/bin/env python3
"""
Test script to submit 20 sample resumes to the ranking API.
This script will:
1. Start the FastAPI server
2. Submit a ranking job with 20 resumes
3. Monitor the job status
4. Display the results
"""

import os
import sys
import time
import requests
import json
from pathlib import Path
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8000"
RESUMES_DIR = Path("data/resumes")
JOB_DESCRIPTION_FILE = Path("data/sample_job_description.txt")
NUM_RESUMES = 20

def read_job_description() -> str:
    """Read the job description from file."""
    with open(JOB_DESCRIPTION_FILE, 'r') as f:
        return f.read()

def get_sample_resumes(num_files: int = 20) -> List[Path]:
    """Get the first N resume files from the resumes directory."""
    resume_files = sorted(RESUMES_DIR.glob("*.pdf"))[:num_files]
    print(f"📁 Found {len(resume_files)} resume files")
    return resume_files

def create_ranking_job(job_description: str, resume_files: List[Path]) -> Dict:
    """
    Create a ranking job by submitting resumes to the API.
    
    Args:
        job_description: The job description text
        resume_files: List of paths to resume PDF files
        
    Returns:
        Response from the API
    """
    url = f"{API_BASE_URL}/api/v1/ranking_jobs/create"
    
    print(f"\n🚀 Submitting ranking job to {url}")
    print(f"📄 Job Description: {len(job_description)} characters")
    print(f"📑 Number of resumes: {len(resume_files)}")
    
    # Prepare the multipart form data
    files = []
    for resume_file in resume_files:
        files.append(
            ('cv_files', (resume_file.name, open(resume_file, 'rb'), 'application/pdf'))
        )
    
    data = {
        'job_description': job_description,
        'job_title': 'Senior Python Backend Developer',
        'company': 'TechCorp Inc.'
    }
    
    try:
        response = requests.post(url, data=data, files=files, timeout=300)
        
        # Close all file handles
        for _, file_tuple in files:
            file_tuple[1].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job created successfully!")
            print(f"📋 Job ID: {result.get('data', {}).get('jobId', 'N/A')}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def check_job_status(job_id: str) -> Dict:
    """
    Check the status of a ranking job.
    
    Args:
        job_id: The job ID to check
        
    Returns:
        Status response from the API
    """
    url = f"{API_BASE_URL}/api/v1/ranking_jobs/{job_id}/status"
    
    try:
        response = requests.post(url, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Status check failed: {e}")
        return None

def get_job_results(job_id: str) -> Dict:
    """
    Get the results of a completed ranking job.
    
    Args:
        job_id: The job ID to get results for
        
    Returns:
        Results from the API
    """
    url = f"{API_BASE_URL}/api/v1/ranking_jobs/{job_id}/results"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Results fetch failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Results fetch failed: {e}")
        return None

def monitor_job(job_id: str, max_wait_seconds: int = 600):
    """
    Monitor a job until completion or timeout.
    
    Args:
        job_id: The job ID to monitor
        max_wait_seconds: Maximum time to wait in seconds
    """
    print(f"\n⏳ Monitoring job {job_id}...")
    start_time = time.time()
    check_interval = 5  # Check every 5 seconds
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > max_wait_seconds:
            print(f"⏰ Timeout after {max_wait_seconds} seconds")
            break
        
        status_response = check_job_status(job_id)
        
        if status_response:
            status_data = status_response.get('data', {})
            current_status = status_data.get('status', 'unknown')
            
            print(f"📊 Status: {current_status} (elapsed: {int(elapsed)}s)")
            
            if current_status == 'completed':
                print(f"✅ Job completed!")
                return True
            elif current_status == 'failed':
                print(f"❌ Job failed!")
                return False
        
        time.sleep(check_interval)
    
    return False

def display_results(results: Dict):
    """
    Display the ranking results in a formatted way.
    
    Args:
        results: The results dictionary from the API
    """
    print("\n" + "="*80)
    print("📊 RANKING RESULTS")
    print("="*80)
    
    data = results.get('data', {})
    candidates = data.get('rankedCandidates', [])
    
    if not candidates:
        print("No candidates found in results")
        return
    
    print(f"\n🎯 Total Candidates Ranked: {len(candidates)}")
    print(f"📋 Job: {data.get('jobTitle', 'N/A')} at {data.get('company', 'N/A')}")
    print("\n" + "-"*80)
    
    for idx, candidate in enumerate(candidates, 1):
        print(f"\n#{idx} - {candidate.get('candidateId', 'Unknown')}")
        print(f"   📈 Total Score: {candidate.get('totalScore', 0):.2f}/100")
        print(f"   🏆 Tier: {candidate.get('tier', 'N/A')}")
        print(f"   💪 Confidence: {candidate.get('confidence', 0):.2%}")
        
        scores = candidate.get('scores', {})
        if scores:
            print(f"   📊 Breakdown:")
            print(f"      • Skills: {scores.get('skills', 0):.1f}")
            print(f"      • Experience: {scores.get('experience', 0):.1f}")
            print(f"      • Education: {scores.get('education', 0):.1f}")
            print(f"      • Career Trajectory: {scores.get('careerTrajectory', 0):.1f}")
        
        strengths = candidate.get('strengths', [])
        if strengths:
            print(f"   ✅ Strengths: {', '.join(strengths[:3])}")
        
        weaknesses = candidate.get('weaknesses', [])
        if weaknesses:
            print(f"   ⚠️  Areas for improvement: {', '.join(weaknesses[:3])}")
        
        if idx >= 10:  # Show only top 10 in detail
            print(f"\n... and {len(candidates) - 10} more candidates")
            break
    
    print("\n" + "="*80)
    
    # Save full results to file
    output_file = f"ranking_results_{data.get('jobId', 'unknown')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Full results saved to: {output_file}")

def check_server_health() -> bool:
    """Check if the API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"⚠️  API server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ API server is not running")
        print(f"💡 Please start the server with: python app.py")
        print(f"   Or: uvicorn app:app --host localhost --port 8000")
        return False

def main():
    """Main test execution."""
    print("="*80)
    print("🧪 RESUME.AI API TEST - 20 Sample Resumes")
    print("="*80)
    
    # Check if server is running
    if not check_server_health():
        sys.exit(1)
    
    # Read job description
    try:
        job_description = read_job_description()
        print(f"\n✅ Loaded job description ({len(job_description)} chars)")
    except Exception as e:
        print(f"❌ Failed to read job description: {e}")
        sys.exit(1)
    
    # Get resume files
    try:
        resume_files = get_sample_resumes(NUM_RESUMES)
        if len(resume_files) < NUM_RESUMES:
            print(f"⚠️  Warning: Only found {len(resume_files)} resumes (requested {NUM_RESUMES})")
        if len(resume_files) == 0:
            print(f"❌ No resume files found in {RESUMES_DIR}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to get resume files: {e}")
        sys.exit(1)
    
    # Create ranking job
    result = create_ranking_job(job_description, resume_files)
    
    if not result:
        print("❌ Failed to create ranking job")
        sys.exit(1)
    
    # Extract job ID
    job_id = result.get('data', {}).get('jobId')
    if not job_id:
        print("❌ No job ID in response")
        sys.exit(1)
    
    # Monitor job progress
    success = monitor_job(job_id, max_wait_seconds=600)
    
    if not success:
        print("❌ Job did not complete successfully")
        sys.exit(1)
    
    # Get and display results
    print("\n📥 Fetching results...")
    results = get_job_results(job_id)
    
    if results:
        display_results(results)
        print("\n✅ Test completed successfully!")
    else:
        print("❌ Failed to fetch results")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

