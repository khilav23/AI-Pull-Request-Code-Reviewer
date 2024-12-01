import google.generativeai as genai
from celery_config import celery_app
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")

MODEL_NAME = "gemini-1.5-flash"

genai.configure(api_key=API_KEY)


try:
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    logging.error(f"Error initializing the Gemini model: {str(e)}")
    raise e

def analyze_code_with_gemini(files_data: list) -> dict:
    """Analyze code files using Gemini AI and return structured results."""
    try:
        client = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"temperature": 0.8},
            system_instruction=None,
        )

        all_issues = []
        for file_data in files_data:
            filename = file_data["filename"]
            code_snippet = file_data["content"]
            
            user_content = f"""Analyze the following code from `{filename}` for style, bugs, performance issues, and best practices:\n\n{code_snippet}"""
            response = client.generate_content([user_content], stream=True)
            
            result_text = ""
            for chunk in response:
                result_text += chunk.text
            

            issues = []
            lines = result_text.split("\n")
            for line in lines:
                if "Issue:" in line:
                    issue_details = line.split(" | ")
                    issue = {
                        "type": issue_details[0].split(":")[1].strip(),
                        "line": int(issue_details[1].split(":")[1].strip()),
                        "description": issue_details[2].split(":")[1].strip(),
                        "suggestion": issue_details[3].split(":")[1].strip(),
                    }
                    issues.append(issue)
            
            all_issues.append({
                "filename": filename,
                "issues": issues
            })

        structured_results = {
            "files": all_issues,
            "summary": {
                "total_files": len(all_issues),
                "total_issues": sum(len(file["issues"]) for file in all_issues),
                "critical_issues": sum(1 for file in all_issues for issue in file["issues"] if issue["type"].lower() == "bug"),
            },
        }
        return structured_results
    except Exception as e:
        logging.error(f"Error generating structured results: {str(e)}")
        return None

@celery_app.task(bind=True)
def analyze_pr_task(self, code_snippet: str):
    """Task to analyze a code snippet using Gemini."""
    try:

        logging.info("Starting code analysis with Gemini.")
        analysis_results = analyze_code_with_gemini(code_snippet)

        return analysis_results
    except Exception as e:
        logging.error(f"Task failed: {str(e)}")
        raise self.retry(exc=e, countdown=5, max_retries=3)
