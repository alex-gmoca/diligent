import json
import uuid
import boto3
import os
import base64
import pymysql
from mysql_connection import MySQL

def insert_script(script_id, script_location, status):
    mysql_connection = MySQL()
    mysql_connection.insert(script_id, script_location, 'Pending')
    mysql_connection.close()
    
def lambda_handler(event, context):
    try:
        is_base64_encoded = event.get('isBase64Encoded', False)
        body = event['body']

        if is_base64_encoded:
            file_content = base64.b64decode(body)
        else:
            file_content = body.encode('utf-8')
        #geneate an id so it can be used to trigger the code
        script_id = str(uuid.uuid4())
        script_file_name = f'/scripts/{script_id}.py'
        s3_client.upload_file(
            Filename=file_content,
            Bucket='diligent_bucket',
            Key=script_file_name,
            ExtraArgs={'ContentDisposition': f'attachment; filename="{script_file_name}"'}
        )
        #save record into db so we can get the location of the script to run
        insert_script(script_id, script_file_name, 'created')
        return {
            "statusCode": 201,
            "body": json.dumps({
                "script_id": script_id
            }),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            }),
        }

