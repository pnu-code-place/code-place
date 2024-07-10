from django.db import models

class Banner(models.Model):
    banner_image = models.TextField()
    link_url = models.URLField()
    visible = models.BooleanField(default=False)
    order = models.PositiveIntegerField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "banner"
        ordering = ("order","-create_time")
