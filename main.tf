# Configure the AWS Provider

provider "aws" {
  region = "eu-west-3"
}

# Create S3 Bucket

resource "aws_s3_bucket" "alita-webapp" {

    bucket = var.s3bucket_name
}

# Enable Bucket versioning

resource "aws_s3_bucket_versioning" "alita-version-enabled" {
  bucket = aws_s3_bucket.alita-webapp.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable Bucket lifecycle for permanetly deleting nocurrent object versions

resource "aws_s3_bucket_lifecycle_configuration" "alita-bucket-lifecycle" {
  depends_on = [aws_s3_bucket_versioning.alita-version-enabled]
  bucket = aws_s3_bucket.alita-webapp.bucket

  rule {

    id = "alita"

    filter {

        prefix = "uploaded_images/"
    }

    expiration {
      days = 3
      expired_object_delete_marker = true
    }

    noncurrent_version_expiration {
      newer_noncurrent_versions = 10
      noncurrent_days = 7
    }

    status = "Enabled"
  }
}

# Public access to uploaded images

resource "aws_s3_bucket_policy" "allow_public_access" {
  bucket = aws_s3_bucket.alita-webapp.id
  policy = <<EOT
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"AddPerm",
      "Effect":"Allow",
      "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["${aws_s3_bucket.alita-webapp.arn}/uploaded_images/*"]
      }
  ]
}
EOT
}

#Now we have s3 bucket  with versioning and lifecycle police where images will be uploaded to uploaded_images/ and that DIR will have public access.
