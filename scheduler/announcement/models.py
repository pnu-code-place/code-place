from django.db import models


class LinkAnnouncement(models.Model):
    la_id = models.IntegerField(primary_key=True)
    title = models.TextField()
    url = models.TextField()
    create_time = models.TextField()
    new_flag = models.BooleanField(default=False)

    class Meta:
        db_table = "link_announcement"
        ordering = ("-la_id",)