import boto3
import time
import pymysql
from datetime import datetime
import os

FARGATE_CLUSTER = os.environ.get('fargate_cluster')
TASK_DEFINITION = os.environ.get('task_definition')
SUBNET = os.environ.get('subnet_id')
MAX_WORKERS = os.environ.get('max_workers')
MAX_IDLE_TIME = os.environ.get('max_idle_time')

ecs_client = boto3.client('ecs', region_name='us-west-2')


# AWS ECS helper functions
def start_fargate_task(job_id, job_parameters):
    response = ecs_client.run_task(
        cluster=FARGATE_CLUSTER,
        launchType='FARGATE',
        taskDefinition=TASK_DEFINITION,
        overrides={
            'containerOverrides': [
                {
                    'name': 'crawler',
                    'environment': [
                        {'name': 'JOB_ID', 'value': str(job_id)},
                        {'name': 'JOB_PARAMETERS', 'value': job_parameters}
                    ]
                }
            ]
        },
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [SUBNET_ID],
                'assignPublicIp': 'ENABLED'
            }
        }
    )
    if response['failures']:
        raise RuntimeError(f"Failed to start task for job {job_id}: {response['failures']}")

    task_arn = response['tasks'][0]['taskArn']
    print(f"Started Fargate task {task_arn} for job {job_id}")
    return task_arn

def stop_idle_jobs(idle_jobs):
    for job in idle_jobs:
        job_id = job['id']
        task_arn = job['task_arn']
        print(f"Stopping idle task {task_arn} for job {job_id}")
        ecs_client.stop_task(cluster=FARGATE_CLUSTER, task=task_arn)
        update_job_status(job_id, 'ERROR')

# Orchestration loop
def scan_jobs():
    mysql_connection = MySQL()
    while True:
        running_jobs = mysql_connection.count_running_jobs()
        if running_jobs < MAX_WORKERS:
            job = mysql_connection.get_queued_job()
            if job:
                try:
                    task_arn = start_fargate_task(job_id, job_parameters)
                    mysql_connection.update_job_status(job['id'], 'AVAILABLE', task_arn)
                except Exception as e:
                    update_job_status(job_id, 'ERROR')
                    print(f"Failed to start job {job_id}: {e}")
        else:
            print(f"Max workers running ({MAX_WORKERS}). Waiting...")
        idle_jobs = mysql_connection.get_idle_jobs()
        if idle_jobs:
            stop_idle_jobs(idle_jobs, MAX_IDLE_TIME)
        time.sleep(10) #can be adjusted

if __name__ == "__main__":
    scan_jobs()
