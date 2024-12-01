web: uvicorn main:app --host 0.0.0.0 --port $PORT
worker: celery -A celery_config worker --loglevel=info --queues=code_review