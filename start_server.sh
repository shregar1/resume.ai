#!/bin/bash
cd /Users/shreyansh/Documents/projects/resume.ai
export PYTHONUNBUFFERED=1
./venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

