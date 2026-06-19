from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("submission", "0004_auto_20250904_1525"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
                        '"submission_judge_end_time_c28a7535" ON "submission" ("judge_end_time")'
                    ),
                    reverse_sql='DROP INDEX CONCURRENTLY IF EXISTS "submission_judge_end_time_c28a7535"',
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="submission",
                    name="judge_end_time",
                    field=models.DateTimeField(db_index=True, null=True),
                ),
            ],
        ),
    ]
