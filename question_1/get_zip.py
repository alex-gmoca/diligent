import json
import uuid
import boto3
import os
import base64
import zipfile
import pymysql
from mysql_connection import MySQL

STATUS_RESPONSES = {
    'pending': {
        'status_code': 202,
        'message': 'Job still running'
    },
    'completed': {
        'status_code': 200,
        'message': 'Job completed'
    },
    'failed': {
        'status_code': 500,
        'message': 'Error while processing the job'
    }
}

def get_file(file_name):
    s3_client = boto3.client('s3')
    file_obj = s3_client.get_object(
        Bucket='diligent_bucket', 
        Key=file_name
    )
    base_64_file = base64.b64encode(file_obj['Body'].read()).decode('utf-8')
    return base_64_file

def get_job(job_id):
    mysql_connection = MySQL()
    job = mysql_connection.get(job_id)
    mysql_connection.close()
    return job

def lambda_handler(event, context):
    try:
        job_id = event['queryStringParameters'].get('job_id')
        if not job_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "job_id is required"
                }),
            }
        job = get_job(job_id)
        if not job:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "message": "job not found"
                }),
            }
        response_info = STATUS_RESPONSES.get(job['status'])
        response = {
            "statusCode": response_info['status_code']
        }
        if job.get('status') == 'completed':
            response['body'] = get_file(job["file_name"])
            response['headers'] = {
                'Content-Type': 'application/zip',
                'Content-Disposition': f'attachment; filename="{job["file_name"]}"'
            }
        else:
            response['body'] = {
                "status": job.get('status'),
                "message": response_info['message']
            }
        return response
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            }),
        }

