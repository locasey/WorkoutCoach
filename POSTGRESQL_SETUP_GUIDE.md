# PostgreSQL Setup Guide with pgAdmin

This guide will help you set up PostgreSQL with a visual database management tool (pgAdmin).

## Prerequisites

1. **Docker Desktop** must be installed and running
   - Download from: https://www.docker.com/products/docker-desktop/
   - Make sure Docker Desktop is running (you'll see the Docker icon in your system tray)

## Step 1: Start Docker Desktop

1. Open Docker Desktop application
2. Wait for it to fully start (the icon should be steady, not animating)
3. You should see "Docker Desktop is running" in the status

## Step 2: Start PostgreSQL and pgAdmin

Once Docker Desktop is running, open a terminal in the project root and run:

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database on port 5432
- Start pgAdmin (database management tool) on port 5050
- Create a persistent volume for your data

## Step 3: Access pgAdmin (Database Management Tool)

1. Open your web browser
2. Go to: **http://localhost:5050**
3. Login with:
   - **Email**: `admin@workoutcoach.local`
   - **Password**: `admin`

## Step 4: Connect to PostgreSQL in pgAdmin

After logging into pgAdmin:

1. **Right-click on "Servers"** in the left sidebar
2. Select **"Register" → "Server"**
3. In the **General** tab:
   - **Name**: `WorkoutCoach DB` (or any name you prefer)
4. In the **Connection** tab:
   - **Host name/address**: `postgres` (this is the Docker service name)
   - **Port**: `5432`
   - **Maintenance database**: `workoutcoach`
   - **Username**: `postgres`
   - **Password**: `postgres`
   - ✅ **Check "Save password"** (optional, for convenience)
5. Click **"Save"**

You should now see your database in the left sidebar!

## Step 5: Configure Backend Environment

1. Navigate to the `backend` directory
2. Copy the environment template:
   ```bash
   cd backend
   copy env.template .env
   ```
   (On Windows PowerShell, use `copy` instead of `cp`)

3. Open `.env` file and verify the database URL:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workoutcoach
   ```

## Step 6: Install Python Dependencies

```bash
cd backend

# Activate virtual environment (if you have one)
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 7: Initialize Database Tables

```bash
# Still in the backend directory
python scripts/init_db.py
```

You should see:
```
✅ Database connection successful
✅ Database tables created successfully
✅ Database initialization complete!
```

## Step 8: Verify in pgAdmin

1. In pgAdmin, expand: **Servers → WorkoutCoach DB → Databases → workoutcoach → Schemas → public → Tables**
2. You should see two tables:
   - `workout_plans`
   - `workouts`

3. Right-click on a table and select **"View/Edit Data" → "All Rows"** to see the data

## Step 9: Test with Sample Data (Optional)

```bash
# Still in the backend directory
python scripts/seed_data.py
```

This will create a sample workout plan that you can view in pgAdmin!

## Useful Commands

### Check if containers are running:
```bash
docker-compose ps
```

### View logs:
```bash
docker-compose logs postgres
docker-compose logs pgadmin
```

### Stop containers:
```bash
docker-compose down
```

### Stop and remove all data (⚠️ deletes database):
```bash
docker-compose down -v
```

### Restart containers:
```bash
docker-compose restart
```

## Troubleshooting

### Docker Desktop not running
- Make sure Docker Desktop is installed and running
- Check the system tray for the Docker icon
- Restart Docker Desktop if needed

### Port already in use
- If port 5432 is already in use, you may have PostgreSQL installed locally
- Either stop the local PostgreSQL service or change the port in `docker-compose.yml`

### Can't connect to database
- Make sure containers are running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`
- Verify DATABASE_URL in `.env` file

### pgAdmin connection fails
- Make sure you're using `postgres` as the hostname (not `localhost`)
- This is because pgAdmin is running in the same Docker network
- The hostname `postgres` refers to the PostgreSQL service name

## Benefits of Using pgAdmin

✅ **Visual Database Management**: Browse tables, view data, run queries
✅ **Easy Testing**: Quickly check if data is being saved correctly
✅ **Query Editor**: Write and test SQL queries
✅ **Data Inspection**: See workout plans and workouts in a user-friendly interface
✅ **Schema Visualization**: Understand your database structure

## Next Steps

Once everything is set up:
1. Start your backend: `python backend/app.py`
2. Generate a workout plan via the chat interface
3. Check pgAdmin to see the data in the database!

