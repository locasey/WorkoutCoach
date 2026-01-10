#!/usr/bin/env python3
"""
Database initialization script.
Creates the database tables and optionally seeds with test data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, engine
from models import WorkoutPlan, Workout
from sqlalchemy import inspect

def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            result.fetchone()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is set correctly")
        return False

def create_tables():
    """Create all database tables"""
    try:
        init_db()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")
        return False

def check_tables_exist():
    """Check if tables exist"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    required_tables = ['workout_plans', 'workouts']
    
    for table in required_tables:
        if table in tables:
            print(f"✅ Table '{table}' exists")
        else:
            print(f"❌ Table '{table}' does not exist")
    
    return all(table in tables for table in required_tables)

if __name__ == '__main__':
    print("=" * 50)
    print("Database Initialization Script")
    print("=" * 50)
    
    if not check_database_connection():
        sys.exit(1)
    
    if check_tables_exist():
        print("\n✅ All tables already exist. No action needed.")
    else:
        print("\n📦 Creating database tables...")
        if create_tables():
            print("\n✅ Database initialization complete!")
        else:
            print("\n❌ Database initialization failed!")
            sys.exit(1)

