#!/bin/bash
# Script to create App Runner service from ECR image

set -e

# Configuration
SERVICE_NAME="deal-deck-api"
REGION="us-east-2"
ACCOUNT_ID="442707283978"
ECR_IMAGE_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/deal-deck-api:latest"
PORT="8000"

echo "🚀 Creating App Runner service from ECR image..."

# Create service configuration JSON
cat > /tmp/apprunner-service.json << EOF
{
  "ServiceName": "${SERVICE_NAME}",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "${ECR_IMAGE_URI}",
      "ImageConfiguration": {
        "Port": "${PORT}",
        "RuntimeEnvironmentVariables": {
          "PORT": "${PORT}"
        }
      },
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": true
  },
  "InstanceConfiguration": {
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  },
  "HealthCheckConfiguration": {
    "Protocol": "HTTP",
    "Path": "/api/docs",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 5
  }
}
EOF

# Create the service
aws apprunner create-service \
  --region "${REGION}" \
  --cli-input-json file:///tmp/apprunner-service.json

echo ""
echo "✅ Service creation initiated!"
echo "📋 Monitor progress in AWS Console: https://console.aws.amazon.com/apprunner/"
echo ""
echo "⚠️  Don't forget to add environment variables:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_SERVICE_ROLE_KEY"
echo "   - DATABASE_URL"
echo "   - SUPABASE_ANON_KEY (if needed)"
echo ""
echo "Update service with:"
echo "aws apprunner update-service --service-arn <service-arn> ..."

