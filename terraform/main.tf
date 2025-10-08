terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "6.14.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "demo_instance" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.demo_sg.id]
  key_name               = "staging-demo-key"

  user_data = <<-EOF
              #!/bin/bash
              # Update system
              yum update -y
              
              # Install Docker
              amazon-linux-extras enable docker
              yum install docker -y
              
              # Start and enable Docker
              systemctl enable docker
              systemctl start docker
              
              # Add ec2-user to docker group
              usermod -aG docker ec2-user
              
              # Restart docker to apply group changes
              systemctl restart docker
                            EOF

  tags = {
    Name = "staging-demo-instance"
  }

  # Wait for the instance to be ready
  provisioner "remote-exec" {
    inline = [
      "echo 'Instance is ready'"
    ]
    
    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("~/.ssh/staging-demo-key.pem")
      host        = self.public_ip
    }
  }
}

resource "aws_security_group" "demo_sg" {
  name        = "staging-demo-sg"
  description = "Allow HTTP and SSH traffic"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "staging-demo-sg"
  }
}

output "public_ip" {
  description = "Public IP of the instance"
  value       = aws_instance.demo_instance.public_ip
}

output "ssh_command" {
  description = "Command to SSH into the instance"
  value       = "ssh -i ~/.ssh/staging-demo-key.pem ec2-user@${aws_instance.demo_instance.public_ip}"
}