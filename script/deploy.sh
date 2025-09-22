#!/bin/bash

echo "🚀 STARTING DEPLOYMENT..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"


check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 failed!"
        exit 1
    fi
}

cd "$PROJECT_ROOT/terraform"
terraform init -input=false
check_success "Terraform initialized"

terraform apply -auto-approve
check_success "Terraform infrastructure created"

PUBLIC_IP=$(terraform output -raw public_ip)
echo "🌐 [2/6] SERVER PUBLIC IP: $PUBLIC_IP"

MAX_ATTEMPTS=20
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "echo 'SSH connection successful'"; then
        
        if ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "sudo docker --version" &>/dev/null; then
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
check_success "Application files copied"

ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "
    set -e
    
    sudo docker --version
    
    sudo systemctl status docker | grep running || sudo systemctl start docker
    sleep 10
    
    sudo docker build -t staging-demo-app .
    
    sudo docker stop staging-demo-container 2>/dev/null || true
    sudo docker rm staging-demo-container 2>/dev/null || true
    
    sudo docker run -d \
        --name staging-demo-container \
        -p 80:80 \
        -e APP_MESSAGE='Hello from Docker Deployment!' \
        -e APP_VERSION='2.0' \
        staging-demo-app
    
    sleep 15
        
    if curl -f http://localhost:80 >/dev/null 2>&1; then
        echo '✅ Application is running internally'
    else
        echo '❌ Application failed internal health check'
        sudo docker logs staging-demo-container
        exit 1
    fi
"


# More robust health check that handles different failure modes
MAX_HEALTH_CHECKS=15
HEALTH_ATTEMPT=1
HEALTH_SUCCESS=false

while [ $HEALTH_ATTEMPT -le $MAX_HEALTH_CHECKS ]; do
    
    # Try multiple connection methods
    if curl -f -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://$PUBLIC_IP/ >/dev/null 2>&1; then
        echo "✅ Application is accessible at http://$PUBLIC_IP"
        HEALTH_SUCCESS=true
        break
    elif curl -f -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://$PUBLIC_IP/api/health >/dev/null 2>&1; then
        echo "✅ API endpoint is accessible at http://$PUBLIC_IP/api/health"
        HEALTH_SUCCESS=true
        break
    else
        if [ $HEALTH_ATTEMPT -eq $MAX_HEALTH_CHECKS ]; then
            echo "⚠️ Application not accessible after $MAX_HEALTH_CHECKS attempts"
            echo "📋 Debugging information:"
            ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PUBLIC_IP "
                echo '=== Container status ==='
                sudo docker ps -a
                echo '=== Recent logs ==='
                sudo docker logs --tail 20 staging-demo-container
                echo '=== Network status ==='
                sudo netstat -tulpn | grep :80 || echo 'Nothing listening on port 80'
                echo '=== Docker port mapping ==='
                sudo docker port staging-demo-container
                echo '=== Security group check ==='
                sudo iptables -L -n | grep 80 || echo 'No iptables rules for port 80'
            "
            break
        fi
        sleep 5
        ((HEALTH_ATTEMPT++))
    fi
done
