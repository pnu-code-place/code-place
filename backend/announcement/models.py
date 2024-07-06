from django.db import models

from account.models import User
from utils.models import RichTextField


class Announcement(models.Model):
    title = models.TextField()
    # HTML
    content = RichTextField()
    create_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_update_time = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "announcement"
        ordering = ("-create_time",)


class LinkAnnouncement(models.Model):
    la_id = models.IntegerField(primary_key=True)
    title = models.TextField()
    url = models.TextField()
    create_time = models.TextField()
    new_flag = models.BooleanField(default=False)

    class Meta:
        db_table = "link_announcement"
        ordering = ("-la_id",)