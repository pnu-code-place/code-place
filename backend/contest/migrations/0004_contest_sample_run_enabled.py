from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0003_contest_ai_assistant_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='sample_run_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
