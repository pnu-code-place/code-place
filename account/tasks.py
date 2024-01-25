import logging
import dramatiq

from options.options import SysOptions
from utils.shortcuts import send_email, DRAMATIQ_WORKER_ARGS
from apscheduler.schedulers.background import BackgroundScheduler
from .models import Score

# 점수 변동폭을 계산하는 위한 Scheduler 실행
scheduler = BackgroundScheduler()
scheduler.add_job(Score.calculate_basis, 'cron', hour=0)
scheduler.add_job(Score.calculate_fluctuation, 'interval', minutes=1)
scheduler.start()

logger = logging.getLogger(__name__)


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS(max_retries=3))
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
