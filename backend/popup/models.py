from django.db import models, transaction

from utils.constants import POPUP_VISIBLE_LIMIT

class Popup(models.Model):
    popup_image = models.TextField()
    link_url = models.URLField()
    visible = models.BooleanField(default=False)
    order = models.PositiveIntegerField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "popup"
        ordering = ("order", "-create_time")
