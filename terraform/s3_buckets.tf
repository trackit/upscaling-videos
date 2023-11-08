resource "aws_s3_bucket" "dataset-videos" {
  bucket = "${local.prefix_dashed}-dataset-videos"

  tags = {
    Name = "${local.prefix_dashed}-dataset-videos"
  }
  lifecycle {
    ignore_changes = [tags["Date of Creation"]]
  }
}

output "DATA_SET_VIDEOS_BUCKET_NAME" {
  value = aws_s3_bucket.dataset-videos.bucket
}
