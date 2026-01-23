# LOC-7: AWS Lightsail Deployment Guide

Step-by-step guide for deploying Workout Coach to AWS Lightsail using GitHub Actions (no local Docker required).

## Overview

This guide uses **GitHub Actions** to build and deploy automatically when you push to `main`. You only need:
- AWS CLI configured locally (for initial setup)
- GitHub repository with secrets configured

**No local Docker needed** - GitHub builds the images on their servers.

---

## Prerequisites

- AWS account with billing enabled
- GitHub repository for this project
- ~15 minutes for initial setup

---

## Step 7: Set Up AWS Lightsail Backend

### 7.1 Install & Configure AWS CLI

**Install AWS CLI (Windows):**
1. Download: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run installer (defaults are fine)
3. Close and reopen terminal
4. Verify: `aws --version`

**Create IAM User:**
1. Go to https://console.aws.amazon.com/iam/
2. Click **Users** → **Create user**
3. Username: `workout-coach-deploy`
4. Click **Next** → **Attach policies directly**
5. Search and check: `AmazonLightsailFullAccess` and `AmazonS3FullAccess`
6. Click **Next** → **Create user**
7. Click on the user → **Security credentials** tab
8. Click **Create access key** → **Command Line Interface (CLI)**
9. **Save both keys** (you'll need them twice - for CLI and GitHub)

**Configure CLI:**
```powershell
aws configure
# AWS Access Key ID: <your-access-key>
# AWS Secret Access Key: <your-secret-key>
# Default region name: us-east-1
# Default output format: json
```

**Verify:**
```powershell
aws lightsail get-regions
```

### 7.2 Create Lightsail Container Service

```powershell
aws lightsail create-container-service --service-name workout-coach-backend --power micro --scale 1 --region us-east-1
```

Wait 2-5 minutes, then check status:
```powershell
aws lightsail get-container-services --service-name workout-coach-backend --query "containerServices[0].state" --output text
```

Should return `READY`.

### 7.3 Get Backend URL (for later)

```powershell
aws lightsail get-container-services --service-name workout-coach-backend --query "containerServices[0].url" --output text
```

Save this URL - you'll need it for GitHub secrets.

---

## Step 8: Set Up Frontend Hosting (S3)

### 8.1 Create S3 Bucket

```powershell
aws s3 mb s3://workoutcoach-frontend --region us-east-1
```

### 8.2 Configure for Static Website Hosting

```powershell
aws s3 website s3://workoutcoach-frontend --index-document index.html --error-document index.html
```

### 8.3 Set Bucket Policy (Public Read)

Create a file called `bucket-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::workoutcoach-frontend/*"
  }]
}
```

Apply it:
```powershell
aws s3api put-bucket-policy --bucket workoutcoach-frontend --policy file://bucket-policy.json
```

### 8.4 Disable Block Public Access

```powershell
aws s3api put-public-access-block --bucket workoutcoach-frontend --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

---

## Step 9: Configure GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your IAM access key |
| `AWS_SECRET_ACCESS_KEY` | Your IAM secret key |
| `DATABASE_URL` | Your Neon connection string |
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `AUTH_USERNAME` | Your login username |
| `AUTH_PASSWORD` | Your login password |
| `LLM_PROVIDER` | `gemini` |
| `GEMINI_API_KEY` | Your Gemini API key |
| `STRAVA_CLIENT_ID` | Your Strava client ID (or dummy value) |
| `STRAVA_CLIENT_SECRET` | Your Strava client secret (or dummy value) |
| `FRONTEND_URL` | `https://workoutcoach.liamocasey.com` |
| `CORS_ORIGINS` | `https://workoutcoach.liamocasey.com` |
| `BACKEND_URL` | URL from Step 7.3 (e.g., `https://xxx.us-east-1.cs.amazonlightsail.com`) |

---

## Step 10: Deploy via GitHub Actions

### 10.1 Push to GitHub

```powershell
git add .
git commit -m "Add GitHub Actions deployment workflow"
git push origin main
```

### 10.2 Monitor Deployment

1. Go to your GitHub repo → **Actions** tab
2. Click on the running workflow
3. Watch the logs for both jobs:
   - `deploy-backend` - Builds Docker, pushes to Lightsail
   - `deploy-frontend` - Builds React, uploads to S3

### 10.3 Verify Deployment

**Backend health check:**
```powershell
curl https://<your-lightsail-url>/api/health
# Should return: {"status":"ok"}
```

**Frontend (S3 direct):**
```
http://workoutcoach-frontend.s3-website-us-east-1.amazonaws.com
```

---

## Step 11: Configure DNS & SSL

### 11.1 Option A: Use CloudFront (Recommended for SSL)

1. Go to AWS Console → CloudFront → Create Distribution
2. Origin domain: `workoutcoach-frontend.s3-website-us-east-1.amazonaws.com`
3. Viewer protocol policy: **Redirect HTTP to HTTPS**
4. Alternate domain name (CNAME): `workoutcoach.liamocasey.com`
5. Custom SSL certificate: **Request certificate** (follow ACM wizard)
6. Default root object: `index.html`
7. Create distribution

After creation, add the CloudFront distribution ID to GitHub secrets:
- `CLOUDFRONT_DISTRIBUTION_ID` = Your distribution ID

### 11.2 Configure DNS

At your domain registrar, add:

**For frontend (CloudFront):**
- Type: CNAME
- Host: `workoutcoach`
- Value: `<distribution-id>.cloudfront.net`

**For backend API (if using custom domain):**
- You can keep using the Lightsail URL directly, or set up a separate subdomain like `api.workoutcoach.liamocasey.com`

### 11.3 Update CORS_ORIGINS

If your frontend URL changes, update the `CORS_ORIGINS` secret in GitHub and re-run the workflow.

---

## Step 12: Run Database Migrations

Your Neon database should already have tables. Verify locally:

```powershell
cd backend
# Activate venv first
alembic current
alembic upgrade head
```

---

## Step 13: Final Testing

### Security Tests
```powershell
# Should return 401 Unauthorized
curl https://<backend-url>/api/workout-plans
curl https://<backend-url>/api/workouts/week
```

### Functional Tests
1. Open `https://workoutcoach.liamocasey.com`
2. Login with your AUTH_USERNAME/AUTH_PASSWORD
3. Test:
   - [ ] Generate workout plan via chat
   - [ ] View week ahead
   - [ ] View month calendar
   - [ ] Toggle workout completion
   - [ ] Export to Excel
   - [ ] Logout

---

## Redeployment

After initial setup, deployments are automatic:

```powershell
git add .
git commit -m "Your changes"
git push origin main
# GitHub Actions handles the rest
```

Or trigger manually: GitHub repo → Actions → Deploy to AWS Lightsail → Run workflow

---

## Troubleshooting

### GitHub Actions Failing

Check the Actions tab for error logs. Common issues:
- **Missing secrets**: Verify all secrets are set correctly
- **IAM permissions**: Ensure the IAM user has `AmazonLightsailFullAccess` and `AmazonS3FullAccess`

### Container Won't Start

```powershell
aws lightsail get-container-log --service-name workout-coach-backend --container-name backend
```

### Health Check Failing

- Verify `DATABASE_URL` secret is correct
- Check Neon dashboard for connection issues

### CORS Errors

- Verify `CORS_ORIGINS` matches your frontend domain exactly (include `https://`)
- Redeploy after changing secrets

---

## Cost Summary

| Service | Monthly Cost |
|---------|-------------|
| Lightsail Container (micro) | $7 (free 3 months) |
| S3 Static Hosting | ~$0.50 |
| CloudFront | ~$1-2 |
| Neon Database | Free tier |
| **Total** | **~$8-10/month** |
