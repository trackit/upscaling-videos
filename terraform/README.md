# Terraform

## Setup workspace

Create a stage on your local environment: `terraform workspace new <stage_name>`

Select an existing stage: `terraform workspace select <stage_name>`

## Env

Create a `terraform.tfvars` file with the following content
CLOCKIFY_API_KEY = "<The_API_KEY>"
Environment = "dev" # Possible values "prod", "stg", "dev"
Owner = "<your_name>"

## Deploy your stack

After selecting your workspace

(Option) Check your plan `terraform plan -var "DateOfCreation=$(date +"%m/%d/%Y")" -var-file terraform.tfvars`

Finally, deploy your stack `terraform apply -var "DateOfCreation=$(date +"%m/%d/%Y")" -var-file terraform.tfvars`
