resource "null_resource" "install_dependencies" {
  provisioner "local-exec" {
    interpreter = var.Terminal == "windows/git/bash" ? ["C:/Program Files/Git/bin/bash.exe", "-c"] : null
    command     = "pip3 install $(grep -ivE 'pandas' ../src/requirements.txt) -t ../python/python"
  }
  triggers = {
    run_on_requirements_change = filemd5("../src/requirements.txt")
  }
}

data "archive_file" "lambda_dependencies" {
  depends_on = [null_resource.install_dependencies]
  excludes   = [
    "__pycache__",
    "venv",
  ]

  source_dir  = "../python"
  output_path = "../python.zip"
  type        = "zip"
}

data "archive_file" "lambda_src" {
  excludes = [
    "__pycache__",
    "etl",
    "scripts",
    "Pipfile",
    "Pipfile.lock",
    "requirements.txt"
  ]

  source_dir  = "../src/"
  output_path = "../code.zip"
  type        = "zip"
}

resource "aws_lambda_layer_version" "lambda_dependencies_layer" {
  depends_on       = [data.archive_file.lambda_dependencies]
  filename         = "../python.zip"
  layer_name       = "${local.prefix}_dependencies_layer"
  source_code_hash = data.archive_file.lambda_dependencies.output_base64sha256

  compatible_runtimes = ["python3.9"]
}

resource "aws_lambda_function" "get_dataset_videos" {
  function_name = "${local.prefix}_get_dataset_videos"
  role          = aws_iam_role.role_lambda.arn
  handler       = "lambdas.get_dataset_videos.handler"

  layers = [
    aws_lambda_layer_version.lambda_dependencies_layer.arn
  ]

  filename         = data.archive_file.lambda_src.output_path
  source_code_hash = filebase64sha256(data.archive_file.lambda_src.output_path)
  runtime          = "python3.9"
  timeout          = 600

  environment {
    variables = {
      REGION                       = local.region
      DATASET_VIDEOS_BUCKET_NAME   = aws_s3_bucket.dataset-videos.bucket
      DATASET_VIDEOS_DYNAMODB_NAME = aws_dynamodb_table.youtube_videos.name
    }
  }

  tags = {
    Name = "${local.prefix}_lambda_get_dataset_videos"
  }

  lifecycle {
    ignore_changes = [tags["Date of Creation"]]
  }
}
