from dagster import Definitions, load_assets_from_modules
from .jobs import medical_pipeline_job
from .schedules import daily_schedule

defs = Definitions(
    jobs=[medical_pipeline_job],
    schedules=[daily_schedule],
)
