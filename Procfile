web: uvicorn main:app --host 0.0.0.0 --port 8000
worker: celery -A celery_config worker --loglevel=info --queues=code_review