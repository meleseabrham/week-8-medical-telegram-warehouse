from dagster import job
from .ops import (
    scrape_telegram_data,
    load_raw_to_postgres,
    run_yolo_enrichment,
    run_dbt_transformations
)

@job
def medical_pipeline_job():
    # Define dependencies
    scrape_output = scrape_telegram_data()
    load_output = load_raw_to_postgres(start_after=scrape_output)
    
    # YOLO and DBT can technically run in parallel after load, 
    # BUT dbt relies on YOLO data for fct_image_detections.
    # So YOLO must run before dbt.
    
    yolo_output = run_yolo_enrichment(start_after=load_output)
    
    # Pass yolo_output to dbt to ensure ordering
    run_dbt_transformations(start_after=yolo_output)
