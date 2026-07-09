# Generated manually for contest community post visibility.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0003_alter_post_question_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="visibility",
            field=models.CharField(
                choices=[
                    ("CONTEST_PARTICIPANTS", "대회 참여자 전체"),
                    ("CONTEST_HOSTS", "주최자만"),
                ],
                default="CONTEST_PARTICIPANTS",
                max_length=30,
            ),
        ),
    ]
