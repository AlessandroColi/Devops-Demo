#!/bin/bash

cd terraform
terraform destroy -auto-approve

echo "✅ ENVIRONMENT TEARDOWN COMPLETE!"