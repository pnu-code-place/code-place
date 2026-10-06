from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0004_problemaihintlog_problem_ai__user_id_7fac82_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='problemaihintlog',
            name='role',
            field=models.CharField(
                choices=[('user', 'user'), ('assistant', 'assistant')],
                default='assistant',
                max_length=16,
            ),
        ),
    ]
