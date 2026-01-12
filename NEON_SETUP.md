# Neon Cloud Database Setup Guide

This guide will help you migrate from local Docker PostgreSQL to Neon cloud database to reduce local resource usage.

## Why Neon?

- ✅ **No local resource usage** - Runs in the cloud
- ✅ **Free tier available** - Perfect for development
- ✅ **Easy setup** - Just a connection string
- ✅ **Automatic backups** - Your data is safe
- ✅ **Accessible anywhere** - Works from any device

## Step 1: Create Neon Account

1. Go to https://neon.tech
2. Click "Sign Up" (you can use GitHub, Google, or email)
3. Complete the signup process

## Step 2: Create a Project

1. Once logged in, click "New Project"
2. Choose a project name (e.g., "WorkoutCoach")
3. Select a region (choose closest to you)
4. Click "Create Project"

## Step 3: Get Connection String

1. After creating the project, you'll see the connection details
2. Look for the "Connection string" section
3. You'll see something like:
   ```
   postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
4. **Copy this connection string** - you'll need it in the next step

## Step 4: Update Your .env File

1. Open `backend/.env` file
2. Find the `DATABASE_URL` line
3. Replace it with your Neon connection string:
   ```env
   DATABASE_URL=postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
4. Save the file

## Step 5: Run Database Migrations

Run the Alembic migrations to create tables in Neon:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
alembic upgrade head
```

This will create all the necessary tables in your Neon database.

## Step 6: Test the Connection

Start your backend server:

```powershell
python app.py
```

If it starts without errors, you're connected! You should see:
```
 * Running on http://0.0.0.0:5000
```

## Step 7: Migrate Existing Data (Optional)

If you have data in your local Docker database that you want to keep:

1. Export data from local database (if needed)
2. Or just start fresh - your workout plans will be saved as you create them

## Step 8: Stop Docker (Optional)

Once you've confirmed Neon is working:

1. Stop Docker containers:
   ```powershell
   docker-compose down
   ```
2. You can remove the Docker Compose file if you want, or keep it as backup

## Troubleshooting

### Connection Issues

- **SSL Required**: Make sure your connection string includes `?sslmode=require`
- **Wrong Credentials**: Double-check your connection string from Neon console
- **Network Issues**: Check your internet connection

### Migration Issues

- **Tables Already Exist**: If you get errors about existing tables, you can:
  - Drop and recreate: `alembic downgrade base` then `alembic upgrade head`
  - Or just continue if tables exist

### Connection String Format

Neon connection strings look like:
```
postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

Make sure:
- No spaces in the connection string
- `sslmode=require` is included
- The entire string is on one line

## Benefits You'll See

- ✅ No Docker running = Less CPU/RAM usage
- ✅ Database accessible from anywhere
- ✅ Automatic backups
- ✅ Easy to share with team members
- ✅ Ready for production deployment

## Next Steps

Once Neon is set up:
1. Test creating a workout plan
2. Verify data is being saved
3. Continue with Phase 2 of development

Your database is now in the cloud! 🎉

