data "template_file" "state_machine_template" {
  template = file("${path.module}/step_function_definition.json")
}

resource "aws_sfn_state_machine" "state_machine" {
  name     = "run_code_sf"
  role_arn = aws_iam_role.api_to_sf_role.arn
  type     = "STANDARD"

  definition = data.template_file.state_machine_template.rendered
}