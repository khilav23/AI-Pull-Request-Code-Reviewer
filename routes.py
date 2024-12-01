from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from celery.result import AsyncResult
from services import analyze_pr_task
import requests
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

class AnalyzePRRequest(BaseModel):
    repo: str  
    pr_number: int  
    pat: str  # Personal Access Token (GitHub PAT)

def fetch_pr_code(repo: str, pr_number: int, pat: str) -> list:
    """Fetch code changes from a GitHub pull request."""
    try:
        headers = {"Authorization": f"token {pat}"}
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch PR files: {response.json().get('message', 'Unknown error')}"
            )
        
        pr_files = response.json()
        files_data = []
        
        for file in pr_files:
            if file["status"] in ["added", "modified"]:  
                raw_url = file["raw_url"]
                file_response = requests.get(raw_url, headers=headers)
                if file_response.status_code == 200:
                    files_data.append({
                        "filename": file["filename"],
                        "content": file_response.text
                    })
                else:
                    logging.warning(f"Failed to fetch content of {file['filename']}")
        
        return files_data
    except Exception as e:
        logging.error(f"Error fetching PR code: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching PR code.")

@router.post("/analyze-pr")
@limiter.limit("10/minute")
async def analyze_pr(request: Request, body: AnalyzePRRequest):
    try:
        # Fetch code from the PR
        files_data = fetch_pr_code(body.repo, body.pr_number, body.pat)
        
        # Submit the Celery task with the full file list
        task = analyze_pr_task.apply_async(args=[files_data])
        return {"task_id": task.id, "message": "Task submitted successfully"}
    except Exception as e:
        logging.error(f"Error analyzing PR: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing PR.")


@router.get("/status/{task_id}")
@limiter.limit("10/minute")
async def get_status(request: Request, task_id: str):
    """Check the status of a Celery task."""
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"task_id": task_id, "status": "PENDING"}
    elif task_result.state == "FAILURE":
        return {"task_id": task_id, "status": "FAILURE", "error": str(task_result.info)}
    return {"task_id": task_id, "status": task_result.state}

@router.get("/results/{task_id}")
@limiter.limit("10/minute")
async def get_results(request: Request, task_id: str):
    """Retrieve the results of a completed task."""
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        raise HTTPException(status_code=400, detail="Task is still pending")
    elif task_result.state == "FAILURE":
        raise HTTPException(status_code=400, detail=f"Task failed: {str(task_result.info)}")
    elif task_result.state == "SUCCESS":
        structured_results = task_result.result
        return {
            "task_id": task_id,
            "status": "completed",
            "results": structured_results,
        }
    return {"task_id": task_id, "status": task_result.state}

