# Code Review Agent API

## Overview
The **Code Review Agent API** is an autonomous code review tool designed to analyze GitHub pull requests (PRs) using Google's Gemini AI model. It identifies style issues, bugs, performance concerns, and best practices in the submitted code. This API integrates with Celery for asynchronous task handling and Redis for task queue management. Rate limiting is implemented using SlowAPI.

---

## Features
- **Pull Request Code Analysis**: Automatically fetches and analyzes code changes from GitHub PRs.
- **AI-powered Review**: Uses the Gemini AI model to detect code issues.
- **Asynchronous Task Management**: Utilizes Celery for background processing.
- **Rate Limiting**: Limits API requests to prevent abuse.

---

## Prerequisites
- **Python 3.8+**
- **Redis**: For Celery's message broker and result backend.
- **Google Generative AI SDK**
- **FastAPI**: For building API endpoints.
- **Celery**: For task management.
- **SlowAPI**: For rate limiting.

---

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/code-review-agent.git
cd code-review-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root directory with the following variables:
```env
API_KEY=<your-google-generative-ai-api-key>
REDIS_URL=redis://localhost:6379/0
```

### 4. Redis Setup
Ensure Redis is running:
```bash
redis-server
```

### 5. Run the Application
#### Celery Worker
Start Celery for asynchronous task handling:
```bash
celery -A celery_config.celery_app worker --loglevel=info
```

#### FastAPI Server
Run the API:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## API Endpoints

### Analyze Pull Request
**POST** `/analyze-pr`
- **Request Body**:
```json
{
  "repo": "owner/repo-name",
  "pr_number": 1,
  "pat": "your-github-pat"
}
```
- **Response**:
```json
{
  "task_id": "12345",
  "message": "Task submitted successfully"
}
```

### Check Task Status
**GET** `/status/{task_id}`
- **Response**:
```json
{
  "task_id": "12345",
  "status": "PENDING"
}
```

### Get Task Results
**GET** `/results/{task_id}`
- **Response**:
```json
{
  "task_id": "12345",
  "status": "completed",
  "results": {...}
}
```

---

## Error Handling
- **Rate Limit Exceeded**: Returns `429 Too Many Requests` if API rate limits are exceeded.
- **Task Failures**: Returns detailed error messages for failed tasks.

---

## License
This project is licensed under the MIT License.

---

## Contributing
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request.

---

## Contact
For support or inquiries, reach out to khilav.jadav@gmail.com.