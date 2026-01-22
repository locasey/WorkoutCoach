# Step 7: AWS Lightsail Setup - CLI Guide

This guide walks you through Step 7 using AWS CLI commands in your terminal.

## Prerequisites

1. **Install AWS CLI** (if not already installed):
   ```powershell
   winget install Amazon.AWSCLI
   # Or download from: https://aws.amazon.com/cli/
   ```

2. **Configure AWS credentials**:
   ```powershell
   aws configure
   ```
   - Enter your AWS Access Key ID
   - Enter your AWS Secret Access Key  
   - Default region: `us-east-1` (or your preferred region)
   - Default output format: `json`

3. **Verify credentials**:
   ```powershell
   aws sts get-caller-identity
   ```

## Step-by-Step CLI Commands

### 1. Create Lightsail Container Service

```powershell
aws lightsail create-container-service `
  --service-name workoutcoach-backend `
  --power nano `
  --scale 1 `
  --region us-east-1
```

**Note:** `nano` = 0.25 vCPU, 0.5 GB RAM (free tier eligible). Wait 1-2 minutes for service to be ready.

### 2. Build Docker Image

First, make sure you're in the backend directory and have a Dockerfile (from Step 4):

```powershell
cd backend
docker build -t workoutcoach-backend:latest .
```

### 3. Push Image to Lightsail

```powershell
aws lightsail push-container-image `
  --service-name workoutcoach-backend `
  --label backend `
  --image workoutcoach-backend:latest `
  --region us-east-1
```

**Important:** This command will output an image name like `workoutcoach-backend:backend-1234567890`. **Copy this image name** - you'll need it in the next step.

### 4. Create Deployment with Environment Variables

Replace `YOUR_IMAGE_NAME` with the image name from Step 3, and replace all the placeholder values with your actual environment variables:

```powershell
aws lightsail create-container-service-deployment `
  --service-name workoutcoach-backend `
  --containers '{
    "backend": {
      "image": "YOUR_IMAGE_NAME",
      "ports": {
        "5000": "HTTP"
      },
      "environment": {
        "DATABASE_URL": "postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require",
        "SECRET_KEY": "your-32-char-secret-key-here",
        "FLASK_ENV": "production",
        "AUTH_USERNAME": "your-username",
        "AUTH_PASSWORD": "your-password",
        "LLM_PROVIDER": "gemini",
        "GEMINI_API_KEY": "your-gemini-key",
        "STRAVA_CLIENT_ID": "your-strava-id",
        "STRAVA_CLIENT_SECRET": "your-strava-secret",
        "STRAVA_REDIRECT_URI": "http://localhost:5000/api/strava/callback",
        "FRONTEND_URL": "https://workoutcoach.liamocasey.com",
        "CORS_ORIGINS": "https://workoutcoach.liamocasey.com",
        "MAX_WORKOUT_PLANS": "5"
      }
    }
  }' `
  --public-endpoint '{
    "containerName": "backend",
    "containerPort": 5000,
    "healthCheck": {
      "healthyThreshold": 2,
      "unhealthyThreshold": 2,
      "timeoutSeconds": 5,
      "intervalSeconds": 30,
      "path": "/api/health",
      "successCodes": "200"
    }
  }' `
  --region us-east-1
```

**Note:** The deployment will take 2-5 minutes to complete.

### 5. Get Service Endpoint URL

```powershell
aws lightsail get-container-services `
  --service-name workoutcoach-backend `
  --region us-east-1
```

Look for the `url` field in the output - this is your backend endpoint.

### 6. Verify Health Endpoint

```powershell
curl https://your-endpoint-url/api/health
```

Or open in browser: `https://your-endpoint-url/api/health`

Expected response:
```json
{"status": "ok", "message": "Workout Coach API is running"}
```

## Alternative: Use the Automated Script

You can also use the provided PowerShell script:

```powershell
.\scripts\deploy-lightsail.ps1
```

This script automates steps 1-3, but you'll still need to manually run step 4 (deployment with env vars) since those are sensitive.

## Troubleshooting

### Check Service Status
```powershell
aws lightsail get-container-services --service-name workoutcoach-backend
```

### View Logs
```powershell
aws lightsail get-container-log --service-name workoutcoach-backend --container-name backend --start-time $(Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
```

### Update Deployment (if you need to change env vars)
```powershell
# Use the same command as step 4, but it will update the existing deployment
aws lightsail create-container-service-deployment ...
```

### Delete Service (if you need to start over)
```powershell
aws lightsail delete-container-service --service-name workoutcoach-backend
```

## Next Steps

After Step 7 is complete:
- ✅ Backend is deployed and accessible
- ⏭️ Step 8: Deploy frontend static files
- ⏭️ Step 9: Configure DNS & SSL

