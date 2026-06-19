from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("submission", "0005_submission_judge_end_time_index"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        'CREATE INDEX CONCURRENTLY IF NOT EXISTS "sub_result_ctime_idx" '
                        'ON "submission" ("result", "create_time")'
                    ),
                    reverse_sql='DROP INDEX CONCURRENTLY IF EXISTS "sub_result_ctime_idx"',
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="submission",
                    index=models.Index(
                        fields=["result", "create_time"],
                        name="sub_result_ctime_idx",
                    ),
                ),
            ],
        ),
    ]
