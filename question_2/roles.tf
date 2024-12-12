resource "aws_iam_role" "api_to_sf_role" {
  name = "api_trigger_sf_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
        Action = ["sts:AssumeRole"]
      }
    ]
  })
}

resource "aws_iam_role_policy" "step_functions_execution_policy" {
  name = "AllowSFExecution"
  role = aws_iam_role.api_to_sf_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:StartSyncExecution"
        ]
        Resource = "*"
      }
    ]
  })
}