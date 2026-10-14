from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("announcement", "0002_auto_20260120_0943"),
    ]

    operations = [
        migrations.AddField(
            model_name="announcement",
            name="is_release_note",
            field=models.BooleanField(default=False),
        ),
    ]
