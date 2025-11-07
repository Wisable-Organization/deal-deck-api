# AWS CLI Setup Guide

## ✅ AWS CLI Installation
AWS CLI has been successfully installed!

## 🔐 Authentication Setup

### Option 1: Using AWS Access Keys (Recommended for CLI)

1. **Get your AWS credentials:**
   - Go to: https://console.aws.amazon.com/iam/home#/security_credentials
   - Click "Create access key"
   - Choose "Command Line Interface (CLI)"
   - Download or copy your:
     - Access Key ID
     - Secret Access Key

2. **Configure AWS CLI:**
   ```bash
   aws configure
   ```
   
   You'll be prompted for:
   - **AWS Access Key ID**: [paste your access key]
   - **AWS Secret Access Key**: [paste your secret key]
   - **Default region name**: `us-east-1` (or your preferred region)
   - **Default output format**: `json` (recommended)

3. **Verify configuration:**
   ```bash
   aws sts get-caller-identity
   ```
   
   This should return your AWS account ID and user ARN.

### Option 2: Using AWS SSO (If your organization uses it)

```bash
aws configure sso
```

Follow the prompts to set up SSO authentication.

## 🚀 Deploying to App Runner from VSCode

Once authenticated, you can deploy using:

### Via AWS CLI:
```bash
# Create App Runner service (see DEPLOY.md for full config)
aws apprunner create-service --cli-input-json file://apprunner-service.json

# Update service
aws apprunner update-service --service-arn <your-service-arn> ...

# List services
aws apprunner list-services

# Get service details
aws apprunner describe-service --service-arn <your-service-arn>
```

### Via AWS Console:
- Navigate to: https://console.aws.amazon.com/apprunner/
- Follow the steps in `DEPLOY.md`

## 🔍 Troubleshooting

### Check your current configuration:
```bash
aws configure list
```

### Test authentication:
```bash
aws sts get-caller-identity
```

### View configured profiles:
```bash
cat ~/.aws/credentials
cat ~/.aws/config
```

### Switch profiles (if you have multiple):
```bash
export AWS_PROFILE=your-profile-name
```

## 📝 Next Steps

1. Run `aws configure` to set up your credentials
2. Test with `aws sts get-caller-identity`
3. Review `DEPLOY.md` for App Runner deployment instructions
4. Deploy your service!

