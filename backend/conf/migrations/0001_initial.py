# Generated by Django 3.2.25 on 2024-07-20 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='JudgeServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.TextField()),
                ('ip', models.TextField(null=True)),
                ('judger_version', models.TextField()),
                ('cpu_core', models.IntegerField()),
                ('memory_usage', models.FloatField()),
                ('cpu_usage', models.FloatField()),
                ('last_heartbeat', models.DateTimeField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('task_number', models.IntegerField(default=0)),
                ('service_url', models.TextField(null=True)),
                ('is_disabled', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'judge_server',
            },
        ),
    ]
