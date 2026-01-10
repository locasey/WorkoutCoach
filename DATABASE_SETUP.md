# Database Setup Guide

This guide will help you set up PostgreSQL for the Workout Coach application.

## Option 1: Using Docker (Recommended)

The easiest way to set up PostgreSQL is using Docker Compose:

```bash
# Start PostgreSQL container
docker-compose up -d

# Check if it's running
docker-compose ps
```

The database will be available at:
- Host: `localhost`
- Port: `5432`
- Database: `workoutcoach`
- Username: `postgres`
- Password: `postgres`

## Option 2: Local PostgreSQL Installation

### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install PostgreSQL (remember the password you set for the `postgres` user)
3. Create a database:
   ```sql
   CREATE DATABASE workoutcoach;
   ```

### macOS
```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb workoutcoach
```

### Linux (Ubuntu/Debian)
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres createdb workoutcoach
```

## Configuration

1. Copy the environment template:
   ```bash
   cd backend
   cp env.template .env
   ```

2. Update `.env` with your database connection string:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workoutcoach
   ```
   
   Adjust the username, password, and database name if different.

## Initialize Database

After setting up PostgreSQL and configuring the connection:

```bash
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Initialize database tables
python scripts/init_db.py
```

Or use Alembic migrations:

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Verify Setup

Check that the database is working:

```bash
# Run the initialization script
python scripts/init_db.py
```

You should see:
```
✅ Database connection successful
✅ Table 'workout_plans' exists
✅ Table 'workouts' exists
✅ Database initialization complete!
```

## Troubleshooting

### Connection Refused
- Make sure PostgreSQL is running
- Check that the port (5432) is correct
- Verify firewall settings

### Authentication Failed
- Check username and password in DATABASE_URL
- Verify PostgreSQL user permissions

### Database Does Not Exist
- Create the database: `CREATE DATABASE workoutcoach;`
- Or update DATABASE_URL to use an existing database

## Next Steps

Once the database is set up, you can:
1. Start the backend server: `python app.py`
2. Generate workout plans via the chat interface
3. Plans will be automatically saved to the database

