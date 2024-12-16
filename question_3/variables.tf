variable "controller_image" {
    type = string
    description = "Docker image of the controller component"
}

variable "controller_ui_port" {
    type = number
    description = "Port for the controller UI"
    default = 80
}

variable "controller_hostname"{
    type = string
    description = "Controller hostname"
}

variable "crawler_image" {
    type = string
    description = "Docker image of the crawler component"
}

variable "crawler_port" {
    type = number
    description = "Port for the crawler service"
    default = 8080
}

variable "chromium_flags"{
    type = string
    description = "Chromium flags for crawler"
} 

variable "number_of_crawlers" {
    type = number
    description = "Number of crawler tasks to run"
}

variable "fargate_cpu" {
    type = string
    description = "CPU units for Fargate tasks"
}

variable "fargate_memory" {
    type = string
    description = "Memory for Fargate tasks"
}

variable "max_idle_time" {
    type = number
    description = "Maximum idle time for workers in minutes"
}

variable "orchestrator_image" {
    type = string
    description = "Docker image for the orchestrator"
}

variable "crawler_hostnames" {
    type = set(object({
        hostname = string
        port = number
    }))
    description = "List of crawler hostnames and ports"
}