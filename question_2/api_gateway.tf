provider "aws" {
  region = "us-west-2"
}


resource "aws_api_gateway_rest_api" "main_api" {
  name        = "run-code-api"
  description = "API to create and run code scripts"
  binary_media_types = ["text/x-python"]
}

resource "aws_api_gateway_resource" "create_code_resource" {
  rest_api_id = aws_api_gateway_rest_api.main_api.id
  parent_id   = aws_api_gateway_rest_api.main_api.root_resource_id
  path_part   = "code/create"
}

resource "aws_api_gateway_resource" "run_code_resource" {
  rest_api_id = aws_api_gateway_rest_api.main_api.id
  parent_id   = aws_api_gateway_rest_api.main_api.root_resource_id
  path_part   = "code/"
}

resource "aws_api_gateway_resource" "run_code_resource_param" {
  rest_api_id = aws_api_gateway_rest_api.main_api.id
  parent_id   = aws_api_gateway_resource.run_code_resource.id
  path_part   = "{script_id}"
}

resource "aws_api_gateway_method" "create_code_method" {
  rest_api_id   = aws_api_gateway_rest_api.main_api.id
  resource_id   = aws_api_gateway_resource.create_code_resource.id
  http_method   = "POST"
  authorization = "NONE"
  request_parameters = {
    "method.request.header.Content-Type" = true
  }
}

resource "aws_api_gateway_method" "run_code_method" {
  rest_api_id   = aws_api_gateway_rest_api.main_api.id
  resource_id   = aws_api_gateway_resource.run_code_resource.id
  http_method   = "POST"
  authorization = "NONE"
  request_parameters = {
    "method.request.path.id" = true
  }
}

resource "aws_api_gateway_integration" "create_code_integration" {
  rest_api_id = aws_api_gateway_rest_api.main_api.id
  resource_id = aws_api_gateway_resource.create_code_resource.id
  http_method = aws_api_gateway_method.create_code_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_code.invoke_arn
  request_templates = {
    "application/json" = "{\n  \"body\": $input.body,\n  \"headers\": {\n    #foreach($header in $input.params().header.keySet())\n    \"$header\": \"$input.params().header.get($header)\",\n    #end\n  }\n}"
  }
}

resource "aws_api_gateway_integration" "run_code_integration" {
  rest_api_id = aws_api_gateway_rest_api.main_api.id
  resource_id = aws_api_gateway_resource.run_code_resource.id
  http_method = aws_api_gateway_method.run_code_method.http_method

  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = ("arn:aws:apigateway:us-west-2:states:action/StartExecution")

  request_parameters = {
    "integration.request.path.id" = "method.request.path.id"
  }
  credentials = aws_iam_role.api_to_sf_role.arn

  request_templates = {
    "application/json" = <<EOF
    #set($input = $input.json('$'))
    {
       "input": "$util.escapeJavaScript($input).replaceAll("\\'", "'")",
     "stateMachineArn": "${aws_sfn_state_machine.state_machine.arn}"
    }
    EOF
  }
}

resource "aws_lambda_permission" "create_code_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_code.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.main_api.execution_arn}/*/*"
}


resource "aws_api_gateway_deployment" "main_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.create_code_integration,
    aws_api_gateway_integration.run_code_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.main_api.id
  stage_name  = "prod"
}

output "base_url" {
  value = aws_api_gateway_deployment.main_api_deployment.invoke_url
}

output "first_endpoint_url" {
  value = "${aws_api_gateway_deployment.main_api_deployment.invoke_url}/code/create"
}

output "second_endpoint_url" {
  value = "${aws_api_gateway_deployment.main_api_deployment.invoke_url}/code/{id}/run"
}