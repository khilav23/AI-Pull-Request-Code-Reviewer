# celery_config.py
from celery import Celery
import sys
import os
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')


# Load environment variables from .env file
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,  # Redis broker URL
    backend=REDIS_URL  # Redis result backend
)

celery_app.conf.task_routes = {
    "services.analyze_pr_task": {"queue": "code_review"}
}


celery_app.autodiscover_tasks(["services"])
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  
    result_serializer='json',
)
