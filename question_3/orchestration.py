import boto3
import time
import pymysql
from datetime import datetime
import os

FARGATE_CLUSTER = os.environ.get('fargate_cluster')
TASK_DEFINITION = os.environ.get('task_definition')
SUBNET = os.environ.get('subnet_id')
MAX_IDLE_TIME = os.environ.get('max_idle_time')
HOSTNAMES = os.environ.get('crwawler_hostnames')
TARGET_GROUP_ARNS = os.environ.get('target_group_arns')

ecs_client = boto3.client('ecs', region_name='us-west-2')


def get_task_network_interface_ip(cluster, task_arn):
    ecs_client = boto3.client('ecs')
    response = ecs_client.describe_tasks(
        cluster=cluster,
        tasks=[task_arn]
    )
    # Extract IP from the first task's network interfaces
    network_interfaces = response['tasks'][0]['attachments'][0]['details']
    for detail in network_interfaces:
        if detail['name'] == 'privateIPv4Address':
            return detail['value']
    raise RuntimeError(f"Failed to retrieve IP for task {task_arn}")

def attach_to_target_group(task_ip, target_group_arn):
    elbv2_client = boto3.client('elbv2')
    elbv2_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[
            {
                'Id': task_ip,
                'Port': 80
            }
        ]
    )

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

def stop_idle_jobs(idle_jobs, current_host):
    for job in idle_jobs:
        job_id = job['id']
        task_arn = job['task_arn']
        print(f"Stopping idle task {task_arn} for job {job_id}")
        ecs_client.stop_task(cluster=FARGATE_CLUSTER, task=task_arn)
        mysql_connection.update_job_status(job_id, 'ERROR')
        mysql_connection.change_host_availability(current_host, True)

# Orchestration loop
def scan_jobs():
    mysql_connection = MySQL()
    #create internal dict for availability, this could live on the DB also
    hosts = {
        host['hostname'] : {
            "hostname": host['hostname'],
            "port": host['port'],
            "target_group_arn": TARGET_GROUP_ARNS[host['hostname']]
        }
        for host in HOSTNAMES
    }

    #if needed initiate the hosts table
    #mysql_connection.initiate_hosts_table(hosts)

    current_host = None
    while True:
        current_host = mysql_connection.check_host_availability()
        if current_host:
            job = mysql_connection.get_queued_job()
            if job:
                try:
                    task_arn = start_fargate_task(job_id, job_parameters)
                    task_ip = get_task_network_interface_ip(FARGATE_CLUSTER, task_arn)
                    attach_to_target_group(task_ip, current_host['target_group_arn'])
                    mysql_connection.change_host_availability(current_host['hostname'], False)
                    mysql_connection.update_job_status(job['id'], 'AVAILABLE', task_arn)
                except Exception as e:
                    mysql_connection.update_job_status(job_id, 'ERROR')
                    print(f"Failed to start job {job_id}: {e}")
        else:
            print(f"No hosts available. Waiting...")
        idle_jobs = mysql_connection.get_idle_jobs()
        if idle_jobs:
            stop_idle_jobs(idle_jobs, current_host)
        time.sleep(10) #can be adjusted

if __name__ == "__main__":
    scan_jobs()
