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

resource "aws_instance" "blog" {
  ami           = data.aws_ami.app_ami.id
  instance_type = var.instance_type

  tags = {
    Name = "HelloWorld"
  }
}

data "aws_vpc" "default" {
  defauolt = true
}




resource "aws_security_group" "blog" {
    description = "Allow http/https in. all out"
    name = "blog"
    tags = {
        for-use-with-amazon-emr-managed-policies = "true"
    }
    vpc_id = data.aws_vpc.default.id

    ingress {
        security_groups = [aws_security_group.blog.id]
        from_port = 80
        protocol = "tcp"
        to_port = 80
        cidr_blocks = ["0.0.0.0/0"]        
    }

    ingress {
        security_groups = [aws_security_group.blog.id]
        from_port = 443
        protocol = "tcp"
        to_port = 443
        cidr_blocks = ["0.0.0.0/0"]        
    }

    egress {
        security_groups = [aws_security_group.blog.id]
        cidr_blocks = ["0.0.0.0/0"]
        from_port = 0
        protocol = "-1"
        to_port = 0
    }
}
