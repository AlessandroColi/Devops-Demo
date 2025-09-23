#!/bin/bash


PUBLIC_IP=$(cd terraform && terraform output -raw public_ip)


scp -i ~/.ssh/staging-demo-key.pem app/app.py ec2-user@$PUBLIC_IP:/home/ec2-user/

ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "
    
      docker build -t staging-demo-app .
    
      docker stop staging-demo-container
      docker rm staging-demo-container
    
      docker run -d \
        --name staging-demo-container \
        -p 80:80 \scp 
        staging-demo-app
"