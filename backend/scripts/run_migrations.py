"""
Production Migration Script
===========================
Runs Alembic migrations against the configured database.

Usage:
    # Against local database (uses .env)
    python scripts/run_migrations.py

    # Against production (set DATABASE_URL in environment)
    DATABASE_URL=<production-url> python scripts/run_migrations.py

    # Check current status only (no changes)
    python scripts/run_migrations.py --status

    # Show migration history
    python scripts/run_migrations.py --history
"""

import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text


def get_alembic_config():
    """Get Alembic config with DATABASE_URL from environment."""
    # Load .env file if it exists (for local development)
    load_dotenv()

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Set it in .env file or export it directly")
        sys.exit(1)

    # Mask URL for logging (hide password)
    masked_url = mask_database_url(database_url)
    print(f"Database: {masked_url}")

    # Create Alembic config
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    return alembic_cfg, database_url


def mask_database_url(url):
    """Mask password in database URL for safe logging."""
    try:
        # postgresql://user:password@host:port/db
        if '@' in url and ':' in url:
            prefix, rest = url.split('://', 1)
            if '@' in rest:
                auth, hostpart = rest.rsplit('@', 1)
                if ':' in auth:
                    user, _ = auth.split(':', 1)
                    return f"{prefix}://{user}:****@{hostpart}"
        return url
    except Exception:
        return "****"


def verify_connection(database_url):
    """Verify we can connect to the database."""
    print("\nVerifying database connection...")
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✓ Connection successful")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def show_current_status(alembic_cfg):
    """Show current migration status."""
    print("\n--- Current Migration Status ---")
    command.current(alembic_cfg, verbose=True)


def show_history(alembic_cfg):
    """Show migration history."""
    print("\n--- Migration History ---")
    command.history(alembic_cfg, verbose=True)


def run_migrations(alembic_cfg):
    """Run all pending migrations."""
    print("\n--- Running Migrations ---")
    print("Upgrading to head...")
    command.upgrade(alembic_cfg, "head")
    print("✓ Migrations completed successfully")


def verify_tables(database_url):
    """Verify expected tables exist after migration."""
    print("\n--- Verifying Tables ---")

    expected_tables = [
        'workout_plans',
        'workouts',
        'strava_sessions',
        'strava_activities',
        'auth_sessions',
        'alembic_version'
    ]

    engine = create_engine(database_url)
    with engine.connect() as conn:
        # Query information_schema for table names
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        existing_tables = {row[0] for row in result}

    all_found = True
    for table in expected_tables:
        if table in existing_tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} (MISSING)")
            all_found = False

    if all_found:
        print("\n✓ All expected tables exist")
    else:
        print("\n✗ Some tables are missing!")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument('--status', action='store_true',
                        help="Show current migration status only")
    parser.add_argument('--history', action='store_true',
                        help="Show migration history only")
    parser.add_argument('--verify', action='store_true',
                        help="Verify tables exist (no migrations)")
    args = parser.parse_args()

    print("=" * 50)
    print("Workout Coach - Database Migration Tool")
    print("=" * 50)

    alembic_cfg, database_url = get_alembic_config()

    # Verify connection first
    if not verify_connection(database_url):
        sys.exit(1)

    if args.status:
        show_current_status(alembic_cfg)
    elif args.history:
        show_history(alembic_cfg)
    elif args.verify:
        verify_tables(database_url)
    else:
        # Run full migration workflow
        show_current_status(alembic_cfg)
        run_migrations(alembic_cfg)
        show_current_status(alembic_cfg)
        verify_tables(database_url)

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
