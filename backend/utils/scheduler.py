from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from account.models import UserScore
from announcement.tasks import scrap_and_update
from problem.utils import call_update_weekly_stats, call_update_bonus_problem


class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.add_jobs()

    def add_jobs(self):
        pass
        # self.scheduler.add_job(UserScore.calculate_basis, 'cron', hour=0)
        # self.scheduler.add_job(UserScore.calculate_fluctuation, 'interval', minutes=1)
        # self.scheduler.add_job(call_update_weekly_stats, 'cron', day_of_week='mon', hour=0, minute=0)
        # self.scheduler.add_job(call_update_bonus_problem, 'cron', day_of_week='mon', hour=0, minute=0)
        # self.scheduler.add_job(scrap_and_update, 'interval', hours=2, next_run_time=timezone.now()+timedelta(seconds=30))

    def start(self):
        self.scheduler.start()
