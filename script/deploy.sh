#!/bin/bash

echo "🚀 STARTING DEPLOYMENT..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"


cd "$PROJECT_ROOT/terraform"
terraform init -input=false
echo "✅ Terraform initialized"

terraform apply -auto-approve
echo "✅ Terraform infrastructure created"

PUBLIC_IP=$(terraform output -raw public_ip)
echo "🌐 SERVER PUBLIC IP: $PUBLIC_IP"

MAX_ATTEMPTS=20
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "echo 'SSH connection successful'"; then
        
        if ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP " docker --version" &>/dev/null; then
            echo "✅ SSH connection established and Docker is available"
            break
        else
            echo "⚠️ SSH connected but Docker not ready yet..."
        fi
    fi
    
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "❌ Instance not ready after $MAX_ATTEMPTS attempts"
        break
    fi
    
    sleep 15
    ((ATTEMPT++))
done

scp -i ~/.ssh/staging-demo-key.pem \
    "$PROJECT_ROOT/app/Dockerfile" \
    "$PROJECT_ROOT/app/app.py" \
    "$PROJECT_ROOT/app/requirements.txt" \
    ec2-user@$PUBLIC_IP:/home/ec2-user/

ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "mkdir -p /home/ec2-user/static"
scp -i ~/.ssh/staging-demo-key.pem \
    "$PROJECT_ROOT/app/imgs/space-r.svg" \
    "$PROJECT_ROOT/app/imgs/space-l.svg" \
    ec2-user@$PUBLIC_IP:/home/ec2-user/static/

echo "✅ Application files and image copied"

ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "    
     docker --version
    
     systemctl status docker | grep running ||  systemctl start docker
    
     docker build -t staging-demo-app .
    
     docker stop staging-demo-container 2>/dev/null || true
     docker rm staging-demo-container 2>/dev/null || true
    
     docker run -d \
        --name staging-demo-container \
        -p 80:80 \
        staging-demo-app
"


echo "✅ Application is fully live and accessible at http://$PUBLIC_IP"