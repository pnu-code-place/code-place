import os
from celery import shared_task


@shared_task(max_retries=0, time_limit=3600, soft_time_limit=3600)
def delete_files(*args):
    for item in args:
        try:
            os.remove(item)
        except Exception:
            pass
