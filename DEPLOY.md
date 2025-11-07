# Deploying to AWS App Runner

## How App Runner Uses Your Dockerfile

App Runner automatically:
1. **Detects** your `Dockerfile` in the repository root
2. **Builds** the Docker image using `docker build`
3. **Runs** the container using the `CMD` instruction in your Dockerfile
4. **Routes traffic** to the port specified in your App Runner configuration

## Deployment Methods

### Method 1: Source-Based Deployment (Recommended)

App Runner connects to your source repository and builds from the Dockerfile automatically.

#### Step 1: Ensure Your Code is in a Repository

```bash
# Make sure all files are committed
git add .
git commit -m "Ready for App Runner deployment"
git push origin main
```

#### Step 2: Deploy via AWS Console

1. **Go to AWS App Runner Console**
   - Navigate to: https://console.aws.amazon.com/apprunner/
   - Click **"Create service"**

2. **Choose Source**
   - Select **"Source code repository"**
   - Connect your GitHub/Bitbucket account (first time only)
   - Select your repository: `deal-deck-api`
   - Select branch: `main` (or your default branch)

3. **Configure Build Settings**
   - **Deployment trigger**: Choose "Automatic" (deploys on every push) or "Manual"
   - **Build configuration**: Select **"Use a configuration file"** or **"Automatic"**
     - If automatic: App Runner will auto-detect your Dockerfile
     - If config file: Use `apprunner.yaml` (optional)

4. **Configure Service**
   - **Service name**: `deal-deck-api`
   - **Virtual CPU**: `1 vCPU` (start small)
   - **Memory**: `2 GB` (start small)
   - **Port**: `8000` (must match EXPOSE in Dockerfile)

5. **Add Environment Variables**
   Click "Add environment variable" and add:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   DATABASE_URL=your_database_url
   SUPABASE_ANON_KEY=your_anon_key (if needed)
   ```

6. **Review and Create**
   - Review settings
   - Click **"Create & deploy"**

7. **Wait for Deployment**
   - App Runner will:
     - Clone your repository
     - Build the Docker image using your Dockerfile
     - Start the container
   - This takes 5-10 minutes the first time
   - Monitor progress in the "Events" tab

8. **Get Your Service URL**
   - Once status is "Running", you'll see a service URL like:
     `https://xxxxx.us-east-1.awsapprunner.com`
   - Test it: `https://your-url.run.app/api/docs`

#### Step 3: Deploy via AWS CLI (Alternative)

```bash
# Create a service configuration file
cat > apprunner-service.json << EOF
{
  "ServiceName": "deal-deck-api",
  "SourceConfiguration": {
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/YOUR_USERNAME/deal-deck-api",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "REPOSITORY"
      }
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
  },
  "NetworkConfiguration": {
    "EgressConfiguration": {
      "EgressType": "DEFAULT"
    }
  }
}
EOF

# Create the service
aws apprunner create-service \
  --cli-input-json file://apprunner-service.json

# Add environment variables (after service is created)
aws apprunner update-service \
  --service-arn <your-service-arn> \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/YOUR_USERNAME/deal-deck-api",
      "SourceCodeVersion": {"Type": "BRANCH", "Value": "main"},
      "CodeConfiguration": {"ConfigurationSource": "REPOSITORY"}
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }'
```

### Method 2: Container-Based Deployment (Advanced)

Build and push to ECR first, then deploy.

#### Step 1: Build and Push to ECR

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository (if doesn't exist)
aws ecr create-repository --repository-name deal-deck-api --region us-east-1

# Build the image
docker build -t deal-deck-api .

# Tag the image
docker tag deal-deck-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/deal-deck-api:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/deal-deck-api:latest
```

#### Step 2: Deploy from ECR

In App Runner console:
1. Choose **"Container image"** as source
2. Select your ECR image
3. Configure service settings
4. Deploy

## Important Notes

### Port Configuration
- Your Dockerfile exposes port `8000`
- App Runner automatically sets `PORT` environment variable
- Your CMD uses `${PORT:-8000}` to handle this
- In App Runner service config, set port to `8000`

### Environment Variables
Set these in App Runner console under "Configuration" → "Environment variables":
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `DATABASE_URL`
- `SUPABASE_ANON_KEY` (if needed)

### Health Checks
App Runner needs a health check endpoint. Your FastAPI app should have:
- Root endpoint: `/` or `/health`
- Or use: `/api/docs` (which FastAPI provides automatically)

### Auto-Deployment
- **Automatic**: App Runner rebuilds on every push to your branch
- **Manual**: You trigger deployments from the console

## Troubleshooting

### Build Fails
- Check build logs in App Runner console → "Logs" tab
- Ensure `poetry.lock` exists (run `poetry lock` if missing)
- Verify Dockerfile syntax is correct

### Service Won't Start
- Check runtime logs in App Runner console
- Verify environment variables are set correctly
- Ensure port matches (8000)

### "Source not found"
- Verify repository connection in App Runner
- Check branch name matches
- Ensure Dockerfile is in repository root

## Updating Your Service

### Automatic Updates
If auto-deploy is enabled:
```bash
# Just push to your branch
git push origin main
# App Runner will automatically rebuild and deploy
```

### Manual Updates
1. Go to App Runner console
2. Select your service
3. Click "Deploy" → "Deploy latest revision"

## Monitoring

- **Logs**: View in CloudWatch Logs (linked from App Runner console)
- **Metrics**: CPU, Memory, Request count in App Runner console
- **Health**: Check service status and health check results

## Cost

- **Free tier**: First 750 hours/month free
- **Pricing**: ~$0.007 per vCPU-hour, ~$0.0008 per GB-hour
- Start with 1 vCPU, 2 GB and scale as needed

