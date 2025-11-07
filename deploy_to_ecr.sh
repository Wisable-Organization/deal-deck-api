#!/bin/bash
# Script to build and push Docker image to ECR for App Runner

set -e  # Exit on error

# Configuration
REGION="${AWS_REGION:-us-east-1}"
REPOSITORY_NAME="deal-deck-api"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Building and pushing Docker image to ECR...${NC}"

# Get AWS account ID
echo -e "${YELLOW}📋 Getting AWS account ID...${NC}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "❌ Error: Could not get AWS account ID. Make sure AWS CLI is configured."
    exit 1
fi

echo -e "${GREEN}✓ AWS Account ID: $AWS_ACCOUNT_ID${NC}"

# Set ECR repository URI
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORY_NAME}"

# Check if ECR repository exists, create if it doesn't
echo -e "${YELLOW}📋 Checking ECR repository...${NC}"
if ! aws ecr describe-repositories --repository-names "$REPOSITORY_NAME" --region "$REGION" &>/dev/null; then
    echo -e "${YELLOW}📦 Creating ECR repository: $REPOSITORY_NAME${NC}"
    aws ecr create-repository \
        --repository-name "$REPOSITORY_NAME" \
        --region "$REGION" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    
    echo -e "${GREEN}✓ Repository created${NC}"
else
    echo -e "${GREEN}✓ Repository already exists${NC}"
fi

# Authenticate Docker to ECR
echo -e "${YELLOW}🔐 Authenticating Docker to ECR...${NC}"
aws ecr get-login-password --region "$REGION" | \
    docker login --username AWS --password-stdin "$ECR_REPOSITORY_URI"

echo -e "${GREEN}✓ Docker authenticated${NC}"

# Build the Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t "$REPOSITORY_NAME:$IMAGE_TAG" .

echo -e "${GREEN}✓ Image built successfully${NC}"

# Tag the image for ECR
echo -e "${YELLOW}🏷️  Tagging image...${NC}"
docker tag "$REPOSITORY_NAME:$IMAGE_TAG" "$ECR_REPOSITORY_URI:$IMAGE_TAG"

echo -e "${GREEN}✓ Image tagged${NC}"

# Push the image to ECR
echo -e "${YELLOW}📤 Pushing image to ECR...${NC}"
docker push "$ECR_REPOSITORY_URI:$IMAGE_TAG"

echo -e "${GREEN}✓ Image pushed successfully${NC}"

# Display summary
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${BLUE}📋 Image Details:${NC}"
echo -e "   Repository: ${ECR_REPOSITORY_URI}"
echo -e "   Tag: ${IMAGE_TAG}"
echo -e "   Region: ${REGION}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo -e "   1. Go to AWS App Runner Console"
echo -e "   2. Create a new service"
echo -e "   3. Select 'Container image' as source"
echo -e "   4. Choose: ${ECR_REPOSITORY_URI}:${IMAGE_TAG}"
echo -e "   5. Configure port: 8000"
echo -e "   6. Add environment variables (SUPABASE_URL, etc.)"
echo ""

