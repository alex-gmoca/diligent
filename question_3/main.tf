terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.13"
    }
  }
}


provider "aws" {
  region = "us-west-2"
}

resource "aws_ecs_cluster" "fargate_cluster" {
  name = "fargate-cluster"
}

resource "aws_ecs_task_definition" "controller_task" {
  family                   = "controller-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "controller-container"
      image     = var.controller_image
      essential = true 
      portMappings = [
        {
          containerPort = var.controller_ui_port
          hostPort      = var.controller_ui_port
          protocol      = "tcp"
        },
        {
          containerPort = var.crawler_port
          hostPort      = var.crawler_port
          protocol      = "tcp"
        }
      ]
    }
  ])
}

resource "aws_ecs_task_definition" "crawler_task" {
  family                   = "crawler-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "crawler-container"
      image     = var.crawler_image
      essential = true
      env = ["CHROMIUM_FLAGS=${var.chromium_flags}", "CONTROLLER_HOSTNAME=${var.controller_hostname}", "CONTROLLER_PORT=${var.crawler_port}"] 
      portMappings = [
        for host in var.crawler_hostnames : {
          containerPort = host.port
          hostPort      = host.port
          protocol      = "tcp"
        }
      ]
    }
  ])
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_service" "controller_service" {
  name            = "controller-service"
  cluster         = aws_ecs_cluster.fargate_cluster.id
  task_definition = aws_ecs_task_definition.controller_task.arn
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private.*.id
    security_groups = [aws_security_group.ecs_security_group.id]
  }
}

# resource "aws_ecs_service" "crawler_service" {
#   name            = "crawler-service"
#   cluster         = aws_ecs_cluster.fargate_cluster.id
#   task_definition = aws_ecs_task_definition.crawler_task.arn
#   desired_count = var.number_of_crawlers
#   launch_type     = "FARGATE"

#   network_configuration {
#     subnets         = aws_subnet.private.*.id
#     security_groups = [aws_security_group.ecs_security_group.id]
#   }
# }

resource "aws_security_group" "ecs_security_group" {
  name_prefix = "ecs-security-group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = var.controller_ui_port
    to_port     = var.controller_ui_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = var.crawler_port
    to_port     = var.crawler_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "private" {
  count      = 2
  vpc_id     = aws_vpc.main.id
  cidr_block = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
}

resource "aws_lb" "main_lb" {
  name = "main-lb"
  internal = false
  load_balancer_type = "application"
  security_groups = [aws_security_group.ecs_security_group.id]
  subnets = aws_subnet.private.*.id
}

#one target group per hostname
resource "aws_lb_target_group" "crawler_target_group" {
  for_each = { for obj in var.crawler_hostnames : obj.hostname => obj }
  name = "tg-${each.key}"
  port = var.crawler_port
  protocol = "HTTP"
  vpc_id = aws_vpc.main.id
}

#gather all arns to pass to the orchestrator container
locals {
  target_group_arns = [for tg in aws_lb_target_group.crawler_target_group : tg.arn]
}
