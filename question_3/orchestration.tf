provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_container" "orchestrator" {
  name = "orchestrator"
  image = var.orchestrator_image
  env = [
    "fargate_cluster=data.aws_ecs_cluster.fargate_cluster.id",
    "task_definition=data.aws_ecs_task_definition.crawler_task.arn",
    "subnet_id=data.aws_subnet.private.*.id",
    "max_workers=var.number_of_crawlers",
    "max_idle_time=var.max_idle_time"
  ]
}