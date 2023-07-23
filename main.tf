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


module "blog_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.1.0"
  name = "blog_sg_from_module"
  vpc_id = data.aws_vpc.default.id
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
    vpc_id = data.aws_vpc.default.id

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


resource "aws_instance" "blog" {
  ami           = data.aws_ami.app_ami.id
  instance_type = var.instance_type

  tags = {
    Name = "HelloWorld"
  }
  #vpc_security_group_ids = [aws_security_group.blog.id]
  # security_group_id from
  # https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest?tab=outputs
  vpc_security_group_ids = [module.blog_sg.security_group_id] 
}

data "aws_vpc" "default" {
  default = true
}


