resource "aws_s3_bucket" "dataset-high-quality-videos" {
  bucket = "${local.prefix_dashed}-dataset-high-quality-videos"

  tags = {
    Name = "${local.prefix_dashed}-dataset-high-quality-videos"
  }
  lifecycle {
    ignore_changes = [tags["Date of Creation"]]
  }
}

resource "aws_s3_bucket" "dataset-low-quality-videos" {
  bucket = "${local.prefix_dashed}-dataset-low-quality-videos"

  tags = {
    Name = "${local.prefix_dashed}-dataset-low-quality-videos"
  }
  lifecycle {
    ignore_changes = [tags["Date of Creation"]]
  }
}


output "HQ_VIDEOS_BUCKET_NAME" {
  value = aws_s3_bucket.dataset-high-quality-videos.bucket
}

output "LQ_VIDEOS_BUCKET_NAME" {
  value = aws_s3_bucket.dataset-low-quality-videos.bucket
}
