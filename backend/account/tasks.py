import logging
from django.db.models import F
import celery

from options.options import SysOptions
from utils.shortcuts import send_email

from .models import UserScore

logger = logging.getLogger(__name__)


@celery.shared_task(max_retries=3, time_limit=3600, soft_time_limit=3600)
def send_email_async(from_name, to_email, to_name, subject, content):
    if not SysOptions.smtp_config:
        return
    try:
        send_email(smtp_config=SysOptions.smtp_config,
                   from_name=from_name,
                   to_email=to_email,
                   to_name=to_name,
                   subject=subject,
                   content=content)
    except Exception as e:
        logger.exception(e)


@celery.shared_task(max_retries=0, time_limit=3600, soft_time_limit=3600)
def calculate_user_score_basis():
    """Calculate the basis for user scores by resetting the yesterday's score and fluctuation.

    This method updates all users' `yesterday_score` to their total scores
    and resets their `fluctuation` to 0.
    """
    UserScore.objects.update(yesterday_score=F('total_score'), fluctuation=0)
    logging.info("User scores have been reset successfully")


@celery.shared_task(max_retries=0, time_limit=3600, soft_time_limit=3600)
def calculate_user_score_fluctuation():
    """Calculate the fluctuation of user scores.

    This method calculates the fluctuation of each user's score by subtracting
    their `yesterday_score` from their `total_score`, and updates the `fluctuation`
    field in the `UserScore` model.
    """
    UserScore.objects.update(fluctuation=F('total_score') - F('yesterday_score'))
    logging.info("User score fluctuations have been calculated successfully")
