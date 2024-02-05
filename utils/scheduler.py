from apscheduler.schedulers.background import BackgroundScheduler
from account.models import Score
from problem.utils import call_update_weekly_stats


class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.add_jobs()

    def add_jobs(self):
        self.scheduler.add_job(Score.calculate_basis, 'cron', hour=0)
        self.scheduler.add_job(Score.calculate_fluctuation, 'interval', minutes=1)
        self.scheduler.add_job(call_update_weekly_stats, 'interval', minutes=1)

    def start(self):
        self.scheduler.start()
