"""
app/agents/worker.py
──────────────────
Production worker entry point.
Used to start Celery workers with a specific configuration.
"""

from app.celery_app import celery_app

if __name__ == "__main__":
    import sys
    
    # Correct way to start a worker from code in Celery 5.x
    # You can pass additional arguments like sys.argv[1:] to customize at runtime
    args = ["worker", "--loglevel=INFO"]
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
        
    celery_app.worker_main(argv=args)
