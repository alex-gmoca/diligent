controller_image = "controller-image"
controller_ui_port = 80
crawler_image = "crawler-image"
crawler_port = 8080
number_of_crawlers = 2
fargate_cpu = "1024"
fargate_memory = "2048"
chromium_flags = "--no-sandbox"
controller_hostname = "some.hostname"
max_idle_time = 5
orchestrator_image = "orchestrator-image"
crawler_hostnames = [
  {
    hostname = "crawler1-hostname"
    port = 8081
  },
  {
    hostname = "crawler2-hostname"
    port = 8082
  },
  {
    hostname = "crawler3-hostname"
    port = 8083
  }
]