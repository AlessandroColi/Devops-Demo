#!/bin/bash

echo "🚀 DEPLOYING PRE-BUILT DOCKER IMAGE..."
echo "========================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Save the correct image name (demo-app:latest instead of production-demo-app:latest)
echo "💾 SAVING DOCKER IMAGE..."
docker save -o demo-app.tar demo-app:latest

cd terraform
PRODUCTION_IP=$(terraform output -raw public_ip 2>/dev/null || echo "NOT_DEPLOYED")

if [ "$PRODUCTION_IP" = "NOT_DEPLOYED" ]; then
    echo "❌ Production infrastructure not running"
    echo "   Run: terraform apply"
    exit 1
fi

echo "📤 TRANSFERRING TO: $PRODUCTION_IP"
scp -i ~/.ssh/staging-demo-key.pem ../demo-app.tar ec2-user@$PRODUCTION_IP:/home/ec2-user/

echo "🐳 LOADING AND RUNNING..."
ssh -i ~/.ssh/staging-demo-key.pem ec2-user@$PRODUCTION_IP "
    docker load -i demo-app.tar
    docker stop production-container 2>/dev/null || true
    docker rm production-container 2>/dev/null || true
    docker run -d --name production-container -p 80:80 -e ENVIRONMENT=production demo-app:latest
    rm -f demo-app.tar
    echo '✅ Deployment complete!'
"

rm -f demo-app.tar

echo "========================================================"
echo "✅ IMAGE DEPLOYED TO PRODUCTION!"
echo "🌐 http://$PRODUCTION_IP"
echo "========================================================"