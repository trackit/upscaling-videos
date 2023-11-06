variable "Environment" {
  type = string
}

variable "DateOfCreation" {
  type = string
}

variable "Owner" {
  type = string
}

variable "Email" {
  type = string
}

variable "Terminal" {
  default = "bash"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "trackit-up-scaling-backend"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-backend"
    encrypt        = true
  }
}

provider "aws" {
  # This is a workaround to raise an error within terraform
  region = terraform.workspace == "default" ? "\n\n Please do not use default workspace\n" : "us-west-2"

  default_tags {
    tags = {
      Project            = "Up-scaling AI"
      TrackitPersistent  = "yes"
      Owner              = var.Owner
      Environment        = var.Environment
      "Date of Creation" = var.DateOfCreation
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_default_tags" "example" {}

locals {
  account_id                  = data.aws_caller_identity.current.account_id
  region                      = data.aws_region.current.id
  prefix                      = "up_scaling_${terraform.workspace}"
  prefix_dashed               = "up-scaling-${terraform.workspace}"
}

output "STAGE" {
  value = terraform.workspace
}

output "REGION" {
  value = local.region
}
