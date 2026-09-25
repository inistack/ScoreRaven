from celery import Celery

celery = Celery(__name__)

def init_celery(app):
    celery.conf.update(
        broker_url = app.config['CELERY_BROKER_URL'],
        result_backend = app.config['CELERY_RESULT_BACKEND']
    )

    celery.conf.beat_schedule = {
    "expire-stale-dispatches": {
        "task": "app.tasks.expire_stale_dispatches",
        "schedule": 300.0,  # every 5 minutes
    },
    "auto-submit-expired-attempts": {
        "task": "app.tasks.auto_submit_expired_attempts",
        "schedule": 60.0,  # every 1 minute
    },
    "release-stale-claims": {
        "task": "app.tasks.release_stale_claims",
        "schedule": 900.0,  # every 15 minutes
    },
    "release-scheduled-results": {
    "task": "app.tasks.release_scheduled_results",
    "schedule": 300.0,  # every 5 minutes
},
}

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery