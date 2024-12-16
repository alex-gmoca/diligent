provider "docker" {
  host = "unix:///Users/alejandro.gomez/.docker/run/docker.sock"
}

resource "docker_container" "orchestrator" {
  name = "orchestrator"
  image = var.orchestrator_image
  env = [
    "fargate_cluster=data.aws_ecs_cluster.fargate_cluster.id",
    "task_definition=data.aws_ecs_task_definition.crawler_task.arn",
    "subnet_id=data.aws_subnet.private.*.id",
    "max_idle_time=var.max_idle_time",
    "crawler_hostnames=var.crawler_hostnames",
    "target_group_arns=local.target_group_arns"
  ]
}