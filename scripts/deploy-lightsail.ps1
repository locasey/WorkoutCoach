# AWS Lightsail Deployment Script for Step 7
# Run this from the project root directory

param(
    [string]$ServiceName = "workoutcoach-backend",
    [string]$Region = "us-east-1",
    [string]$Power = "nano",  # nano = 0.25 vCPU, 0.5 GB RAM (free tier eligible)
    [int]$Scale = 1
)

Write-Host "=== AWS Lightsail Deployment Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if AWS CLI is installed
Write-Host "Checking AWS CLI installation..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version
    Write-Host "✓ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ AWS CLI not found. Install from: https://aws.amazon.com/cli/" -ForegroundColor Red
    exit 1
}

# Check if AWS credentials are configured
Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✓ AWS credentials configured" -ForegroundColor Green
} catch {
    Write-Host "✗ AWS credentials not configured. Run: aws configure" -ForegroundColor Red
    Write-Host "  You'll need your AWS Access Key ID and Secret Access Key" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== Step 1: Create Lightsail Container Service ===" -ForegroundColor Cyan
Write-Host "Service Name: $ServiceName" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host "Power: $Power" -ForegroundColor White
Write-Host ""

# Check if service already exists
Write-Host "Checking if service already exists..." -ForegroundColor Yellow
$existingService = aws lightsail get-container-services --service-name $ServiceName 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Service '$ServiceName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating container service..." -ForegroundColor Yellow
    aws lightsail create-container-service `
        --service-name $ServiceName `
        --power $Power `
        --scale $Scale `
        --region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Container service created successfully" -ForegroundColor Green
        Write-Host "  Waiting for service to be ready (this may take 1-2 minutes)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    } else {
        Write-Host "✗ Failed to create container service" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Step 2: Build and Push Docker Image ===" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop" -ForegroundColor Red
    exit 1
}

# Navigate to backend directory
Push-Location backend

# Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t $ServiceName:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker build failed" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "✓ Docker image built successfully" -ForegroundColor Green

# Push to Lightsail
Write-Host "Pushing image to Lightsail..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Yellow

$pushOutput = aws lightsail push-container-image `
    --service-name $ServiceName `
    --label backend `
    --image "$ServiceName:latest" `
    --region $Region

if ($LASTEXITCODE -eq 0) {
    # Extract image name from output
    $imageName = ($pushOutput | ConvertFrom-Json).image.image
    Write-Host "✓ Image pushed successfully: $imageName" -ForegroundColor Green
    $env:LIGHTSAIL_IMAGE = $imageName
} else {
    Write-Host "✗ Failed to push image" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

Write-Host ""
Write-Host "=== Step 3: Configure Environment Variables ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠ MANUAL STEP REQUIRED ⚠" -ForegroundColor Yellow
Write-Host ""
Write-Host "You need to create a deployment with environment variables." -ForegroundColor White
Write-Host "The image name is: $env:LIGHTSAIL_IMAGE" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can either:" -ForegroundColor White
Write-Host "  1. Use the AWS Console to configure environment variables" -ForegroundColor White
Write-Host "  2. Use the AWS CLI command below (replace values with your actual env vars):" -ForegroundColor White
Write-Host ""
Write-Host "Example AWS CLI command:" -ForegroundColor Cyan
Write-Host @"
aws lightsail create-container-service-deployment `
  --service-name $ServiceName `
  --containers '{
    \"backend\": {
      \"image\": \"$env:LIGHTSAIL_IMAGE\",
      \"ports\": {
        \"5000\": \"HTTP\"
      },
      \"environment\": {
        \"DATABASE_URL\": \"your-neon-connection-string\",
        \"SECRET_KEY\": \"your-secret-key\",
        \"FLASK_ENV\": \"production\",
        \"AUTH_USERNAME\": \"your-username\",
        \"AUTH_PASSWORD\": \"your-password\",
        \"LLM_PROVIDER\": \"gemini\",
        \"GEMINI_API_KEY\": \"your-key\",
        \"STRAVA_CLIENT_ID\": \"your-id\",
        \"STRAVA_CLIENT_SECRET\": \"your-secret\",
        \"STRAVA_REDIRECT_URI\": \"http://localhost:5000/api/strava/callback\",
        \"FRONTEND_URL\": \"https://workoutcoach.liamocasey.com\",
        \"CORS_ORIGINS\": \"https://workoutcoach.liamocasey.com\",
        \"MAX_WORKOUT_PLANS\": \"5\"
      }
    }
  }' `
  --public-endpoint '{
    \"containerName\": \"backend\",
    \"containerPort\": 5000,
    \"healthCheck\": {
      \"healthyThreshold\": 2,
      \"unhealthyThreshold\": 2,
      \"timeoutSeconds\": 5,
      \"intervalSeconds\": 30,
      \"path\": \"/api/health\",
      \"successCodes\": \"200\"
    }
  }' `
  --region $Region
"@ -ForegroundColor Gray

Write-Host ""
Write-Host "=== Step 4: Get Service Endpoint ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "After deployment, get your endpoint URL:" -ForegroundColor White
Write-Host "  aws lightsail get-container-services --service-name $ServiceName --region $Region" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then test the health endpoint:" -ForegroundColor White
Write-Host "  curl https://your-endpoint-url/api/health" -ForegroundColor Cyan
Write-Host ""

