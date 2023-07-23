data "aws_ami" "app_ami" {
  most_recent = true

  filter {
    name   = "name"
    values = ["bitnami-tomcat-*-x86_64-hvm-ebs-nami"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["979382823631"] # Bitnami
}

# https://registry.terraform.io/
module "blog_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.1.0"
  name = "blog_sg_from_module"
  #vpc_id = data.aws_vpc.default.id
  vpc_id = module.vpc.vpc_id

  ingress_rules       = ["http-80-tcp","https-443-tcp"]
  ingress_cidr_blocks = ["0.0.0.0/0"] 

  egress_rules       = ["all-all"]
  egress_cidr_blocks = ["0.0.0.0/0"] 
}



resource "aws_security_group" "blog" {
    description = "Allow http/https in. all out"
    name = "blog"
    tags = {
        for-use-with-amazon-emr-managed-policies = "true"
    }
    #vpc_id = data.aws_vpc.default.id
    vpc_id = module.vpc.vpc_id

    ingress {
        
        from_port = 80
        protocol = "tcp"
        to_port = 80
        cidr_blocks = ["0.0.0.0/0"]        
    }

    ingress {
        
        from_port = 443
        protocol = "tcp"
        to_port = 443
        cidr_blocks = ["0.0.0.0/0"]        
    }

    egress {
        
        cidr_blocks = ["0.0.0.0/0"]
        from_port = 0
        protocol = "-1"
        to_port = 0
    }
}


resource "aws_instance" "blog2" {
  ami           = data.aws_ami.app_ami.id
  instance_type = var.instance_type
  associate_public_ip_address = true

  tags = {
    Name = "HelloWorld"
  }
  subnet_id =  module.vpc.public_subnets[0]
  #vpc_security_group_ids = [aws_security_group.blog.id]
  # security_group_id from
  # https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest?tab=outputs
  vpc_security_group_ids = [module.blog_sg.security_group_id] 
}


module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 8.0"

  name = "blog-alb"

  load_balancer_type = "application"

  vpc_id             = module.vpc.vpc_id
  subnets            = module.blog_vpc.public_subnets
  security_groups    = module.blog_sg.security_group_id

  #access_logs = {
  #  bucket = "my-alb-logs"
  #}

  target_groups = [
    {
      name_prefix      = "blog-"
      backend_protocol = "HTTP"
      backend_port     = 80
      target_type      = "instance"
      targets = {
        my_target = {
          target_id = aws_instance.blog2.id
          port = 80
        }

      }
    }
  ]

  #https_listeners = [
  #  {
  #    port               = 443
  #    protocol           = "HTTPS"
  #    certificate_arn    = "arn:aws:iam::123456789012:server-certificate/test_cert-123456789012"
  #    target_group_index = 0
  #  }
  #]

  http_tcp_listeners = [
    {
      port               = 80
      protocol           = "HTTP"
      target_group_index = 0
    }
  ]

  tags = {
    Environment = "dev"
  }
}





#data "aws_vpc" "default" {
#  default = true
#}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "dev-vpc"
  cidr = "10.0.0.0/16"

  azs              = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets   = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  #enable_vpn_gateway = true

  tags = {
    Terraform = "true"
    Environment = "dev"
  }
}




