# LOC-7 Deployment - Session Handoff

**Last Updated:** Session closed after AWS CLI installation

## Current State

- **Progress:** 60% complete (Steps 1-7 done)
- **AWS CLI:** Just installed, needs configuration
- **Next Step:** Step 8 - Set Up AWS Infrastructure

## What's Been Done

1. Steps 1-6: Auth, login UI, env-driven URLs, Dockerfiles, production templates
2. Step 7: GitHub Actions workflow created at `.github/workflows/deploy.yml`
3. Deployment guide rewritten to use GitHub Actions (no local Docker needed)
4. Helper files created: `infra/bucket-policy.json`

## What User Needs To Do Next

### Immediate (Step 8.1 - Configure AWS CLI)

User just installed AWS CLI. Next commands to run:

```powershell
# 1. Verify installation
aws --version

# 2. Configure credentials (user needs to create IAM user first in AWS Console)
aws configure
# Access Key ID: <from IAM>
# Secret Access Key: <from IAM>
# Region: us-east-1
# Output: json

# 3. Verify it works
aws lightsail get-regions
```

### Then Continue With

1. **Create IAM User** (AWS Console):
   - Go to https://console.aws.amazon.com/iam/
   - Create user `workout-coach-deploy`
   - Attach policies: `AmazonLightsailFullAccess`, `AmazonS3FullAccess`
   - Create access key, save both keys

2. **Create Lightsail Container Service:**
   ```powershell
   aws lightsail create-container-service --service-name workout-coach-backend --power micro --scale 1 --region us-east-1
   ```

3. **Create S3 Bucket:**
   ```powershell
   aws s3 mb s3://workoutcoach-frontend --region us-east-1
   ```

4. **Configure GitHub Secrets** (see guide for full list)

5. **Push to main** to trigger deployment

## Key Files

| File | Purpose |
|------|---------|
| `docs/LOC-7_DEPLOYMENT_PLAN.md` | Master tracking document |
| `docs/LOC-7_STEP7_CLI_GUIDE.md` | Full CLI commands guide |
| `.github/workflows/deploy.yml` | GitHub Actions deployment |
| `infra/bucket-policy.json` | S3 bucket policy |

## User Context

- Windows machine, using PowerShell
- Had RAM issues with Docker locally (that's why we use GitHub Actions)
- Domain: `workoutcoach.liamocasey.com`
- Database: Neon PostgreSQL (already configured)
