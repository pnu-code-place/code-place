

from apscheduler.schedulers.background import BackgroundScheduler


from account.models import UserScore
from announcement.tasks import scrap_link_announcement
from problem.tasks import update_weekly_stats, update_bonus_problem


class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.add_jobs()

    def add_jobs(self):
        self.scheduler.add_job(UserScore.calculate_basis, 'interval', minutes=1)
        self.scheduler.add_job(UserScore.calculate_fluctuation, 'interval', minutes=1)
        self.scheduler.add_job(update_weekly_stats, 'interval', minutes=1)
        self.scheduler.add_job(update_bonus_problem, 'interval', minutes=1)
        self.scheduler.add_job(scrap_link_announcement, 'interval', minutes=30)

    def start(self):
        self.scheduler.start()
