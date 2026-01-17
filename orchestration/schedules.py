from dagster import ScheduleDefinition
from .jobs import medical_pipeline_job

daily_schedule = ScheduleDefinition(
    job=medical_pipeline_job,
    cron_schedule="0 0 * * *",  # Run daily at midnight
)
