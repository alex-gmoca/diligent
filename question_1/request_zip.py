import json
import uuid
import boto3
import os
import pymysql
from mysql_connection import MySQL

        
def send_to_queue(job_id, folder):
    sqs = boto3.client('sqs')
    queue_url = os.environ['zip_queue_url']
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({
            "job_id": job_id,
            "folder": folder
        })
    )
    return response

def insert_job(job_id, folder):
    mysql_connection = MySQL()
    mysql_connection.insert(job_id, folder, 'pending')
    mysql_connection.close()
    
def lambda_handler(event, context):
    ### Request body example:
    ### {
    ###    "folder": "/any_folder_name"
    ### }
    try:
        folder = event.get("folder")
        if not folder:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "folder name is required"
                }),
            }
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket='diligent_bucket', Prefix=folder)
        if 'Contents' in response:
            #generate a new job id to keep track of the progress
            job_id = str(uuid.uuid4())
            #send the job to the queue to be processed
            send_to_queue(job_id, folder)
            #insert the job in the database with status pending
            insert_job(job_id, folder)
            return {
                "statusCode": 201,
                "body": json.dumps({
                    "job_id": job_id
                }),
            }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "folder not found"
                }),
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            }),
        }

