import os
import sys
import subprocess
from dagster import op, Out, Output, String

WORKING_DIR = os.getcwd()

def run_script(script_path):
    result = subprocess.run(
        ["python", script_path],
        cwd=WORKING_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Script {script_path} failed:\n{result.stderr}")
    return result.stdout

@op
def scrape_telegram_data() -> String:
    """Runs the Telegram scraper."""
    output = run_script("src/scraper.py")
    return output

@op
def load_raw_to_postgres(start_after: String = "") -> String:
    """
    Loads scraped JSON data into PostgreSQL raw schema.
    Accepts 'start_after' to enforce dependency on scraper.
    """
    output = run_script("src/load_data.py")
    return output

@op
def run_yolo_enrichment(start_after: String = "") -> String:
    """
    Runs YOLO object detection on images.
    Accepts 'start_after' to enforce dependency on loader.
    """
    output = run_script("src/yolo_detect.py")
    return output

@op
def run_dbt_transformations(start_after: String = "") -> String:
    """
    Runs dbt run and dbt test.
    Accepts 'start_after' to enforce dependency on YOLO/Loader.
    """
    dbt_dir = os.path.join(WORKING_DIR, "medical_warehouse")
    
    # Calculate dbt absolute path
    # sys.executable is .../python.exe, dbt is in .../Scripts/dbt.exe
    python_dir = os.path.dirname(sys.executable)
    dbt_path = os.path.join(python_dir, "Scripts", "dbt.exe")
    
    if not os.path.exists(dbt_path):
        # Fallback if Scripts is not a subdir of python dir (e.g. venv vs global)
        # But for this user, we know the path
        dbt_path = "dbt" 

    # dbt run
    run_res = subprocess.run(
        [dbt_path, "run"],
        cwd=dbt_dir,
        capture_output=True,
        text=True,
        shell=True 
    )
    if run_res.returncode != 0:
        raise Exception(f"dbt run failed:\n{run_res.stderr}\n{run_res.stdout}")
        
    # dbt test
    test_res = subprocess.run(
        [dbt_path, "test"],
        cwd=dbt_dir,
        capture_output=True,
        text=True,
        shell=True
    )
    if test_res.returncode != 0:
        raise Exception(f"dbt test failed:\n{test_res.stderr}\n{test_res.stdout}")
        
    return f"DBT Run Output:\n{run_res.stdout}\nDBT Test Output:\n{test_res.stdout}"
