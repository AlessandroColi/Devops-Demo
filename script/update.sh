#!/bin/bash


PUBLIC_IP=$(cd terraform && terraform output -raw public_ip)


scp -i ~/.ssh/staging-demo-key.pem \
    app/Dockerfile \
    app/app.py \
    app/requirements.txt \
    ec2-user@$PUBLIC_IP:/home/ec2-user/

# Rebuild and redeploy
ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "
    
    echo '📦 Building new Docker image...'
    sudo docker build -t staging-demo-app .
    
    echo '🛑 Stopping current container...'
    sudo docker stop staging-demo-container || true
    sudo docker rm staging-demo-container || true
    
    echo '🚀 Starting new container...'
    sudo docker run -d \
        --name staging-demo-container \
        -p 80:80 \
        -e APP_MESSAGE='Application Updated via Docker Rebuild!' \
        -e APP_VERSION='$(date +%Y%m%d)' \
        staging-demo-app
    
    echo '⏳ Waiting for application to start...'
    sleep 10
    
    echo '🔍 Verifying deployment...'
    sudo docker ps
    sudo docker logs --tail 5 staging-demo-container
"