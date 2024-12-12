resource "aws_lambda_function" "create_code" {
  filename      = "create_code_function.zip"
  function_name = "create_code_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "app.lambda_handler"
  runtime       = "python3.11"

  environment {
    variables = {
      ENVIRONMENT = "production"
    }
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "create_script_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}