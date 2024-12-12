import json
import uuid
import boto3
import os
import zipfile
import pymysql
from mysql_connection import MySQL

def update_job_status(job_id, status, file_name=None):
    mysql_connection = MySQL()
    mysql_connection.update(job_id, status, file_name)
    mysql_connection.close()

def generate_and_save_zip(folder, job_id):
    s3_client = boto3.client('s3')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        s3_objects = s3_client.list_objects_v2(
            Bucket='diligent_bucket', 
            Prefix=f"{folder}/"
        )
        for obj in s3_objects.get('Contents', []):
            file_obj = s3_client.get_object(
                Bucket='customer-attachments', 
                Key=obj['Key']
            )
            file_content = file_obj['Body']
            filename = obj['Key'].split('/')[-1]
            zipf.writestr(filename, file_content.read())
    zip_filename = f'zip-files/{folder}-{job_id}.zip'
    s3_client.upload_file(
        Filename=zip_path,
        Bucket='diligent_bucket',
        Key=zip_filename,
        ExtraArgs={'ContentDisposition': f'attachment; filename="{zip_filename}"'}
    )
    return zip_filename

        update_job_status(job_id, 'failed')
        return None

def lambda_handler(event, context):
    records = event['Records']
    #assuming there is only one record per event
    job = json.loads(records[0]['body'])
    try:
        zip_file_url = generate_and_save_zip(job['folder'])
        update_job_status(job['job_id'], 'completed', zip_file_url)
    except Exception as e:
        update_job_status(job['job_id'], 'failed')
        #consider raising an exception for retrying the job

