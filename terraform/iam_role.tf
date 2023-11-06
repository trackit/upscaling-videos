
resource "aws_iam_role" "role_lambda" {
  name = "${local.prefix}_lambda_role"

  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    }
  )

  tags = {
    Name = "${local.prefix}_iam_policy_lambda"
  }
  lifecycle {
    ignore_changes = [tags["Date of Creation"]]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_access_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.role_lambda.name
}

resource "aws_iam_policy" "lambda_policy" {
  name = "${local.prefix}_lambda_policy"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "s3:GetObject",
            "s3:PutObject",
          ],
          "Resource" : [
            "${aws_s3_bucket.dataset-high-quality-videos.arn}/*",
            "${aws_s3_bucket.dataset-low-quality-videos.arn}/*"
          ],
          "Effect" : "Allow"
        }
      ]
    }
  )

  tags = {
    Name = "${local.prefix}_iam_policy_lambda"
  }
  lifecycle {
    ignore_changes = [tags["Date of Creation"]]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_policy.arn
  role       = aws_iam_role.role_lambda.name
}
