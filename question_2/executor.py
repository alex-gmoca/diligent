import subprocess
import boto3
import sys
import os
from mysql_connection import MySQL

def get_script_info(script_id)
    mysql_connection = MySQL()
    script = mysql_connection.get(script_id)
    mysql_connection.close()
    return script

def update_script_info(script_id, output_location, status):
    mysql_connection = MySQL()
    mysql_connection.update(script_id, output_location, status)
    mysql_connection.close()

def main():
    code_s3_bucket = os.getenv("CODE_S3_BUCKET")
    script_id = os.getenv("SCRIPT_ID")
    script = get_script_info(script_id)
    # Download code from S3
    s3 = boto3.client("s3")
    local_code_file = "/tmp/code.py"
    s3.download_file(code_s3_bucket, script['script_location'], local_code_file)
    # Execute the code
    try:
        result = subprocess.run(
            ["python", local_code_file],
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        output = result.stdout
        error = result.stderr
        status = 'Completed'
    except subprocess.TimeoutExpired:
        output = ""
        error = "Execution timed out."
        status = 'Failed'

    # Save the result to S3
    output_file = "/tmp/output.log"
    with open(output_file, "w") as f:
        f.write(f"Output:\n{output}\nError:\n{error}")
    output_s3_key = f'/output/{script_id}'
    s3.upload_file(output_file, code_s3_bucket, output_s3_key)
    update_script_info(script_id, output_s3_key, status)
if __name__ == "__main__":
    main()
