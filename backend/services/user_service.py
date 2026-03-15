"""
User Service for Workout Coach

Handles user CRUD operations for Google OAuth multi-user support.
"""

import uuid
from sqlalchemy.orm import Session
from models.user import User


class UserService:

    @staticmethod
    def get_by_google_id(db: Session, google_id: str) -> User | None:
        return db.query(User).filter(User.google_id == google_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_or_create_by_google(db: Session, google_id: str, email: str, name: str = None) -> tuple[User, bool]:
        """
        Find user by google_id, or link pending account by email, or return None.

        Returns:
            (user, created) tuple. created=True if a new user was created.
            Returns (None, False) if no existing user found (caller must handle invite code flow).
        """
        # 1. Direct match by google_id
        user = UserService.get_by_google_id(db, google_id)
        if user:
            return user, False

        # 2. Check for PENDING_GOOGLE_LINK (seed user matched by email)
        user = db.query(User).filter(
            User.email == email,
            User.google_id == 'PENDING_GOOGLE_LINK'
        ).first()
        if user:
            user.google_id = google_id
            if name:
                user.name = name
            db.commit()
            db.refresh(user)
            return user, False

        # 3. No existing user found
        return None, False

    @staticmethod
    def create_user(db: Session, google_id: str, email: str, name: str = None,
                    role: str = 'beta_tester', invite_code_used: str = None) -> User:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            role=role,
            invite_code_used=invite_code_used
        )
        db.add(user)
        db.flush()  # Assigns ID without committing — caller controls transaction
        return user

    VALID_DAYS = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}
    VALID_EXPERIENCE_LEVELS = {'beginner', 'intermediate', 'advanced'}
    VALID_DISTANCE_UNITS = {'mi', 'km'}

    @staticmethod
    def update_preferences(db: Session, user_id: uuid.UUID, preferences: dict) -> User:
        """
        Validate and merge preferences into the user's existing JSONB.

        Supported keys:
            available_days: list of 'mon'-'sun'
            experience_level: 'beginner' | 'intermediate' | 'advanced'
            weekly_mileage_comfort: positive number
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        errors = {}

        if 'available_days' in preferences:
            days = preferences['available_days']
            if not isinstance(days, list) or not all(d in UserService.VALID_DAYS for d in days):
                errors['available_days'] = f"Must be a list from: {', '.join(sorted(UserService.VALID_DAYS))}"

        if 'experience_level' in preferences:
            level = preferences['experience_level']
            if level not in UserService.VALID_EXPERIENCE_LEVELS:
                errors['experience_level'] = f"Must be one of: {', '.join(sorted(UserService.VALID_EXPERIENCE_LEVELS))}"

        if 'weekly_mileage_comfort' in preferences:
            mileage = preferences['weekly_mileage_comfort']
            if mileage is not None:
                try:
                    mileage = float(mileage)
                    if mileage < 0:
                        errors['weekly_mileage_comfort'] = "Must be a non-negative number"
                except (TypeError, ValueError):
                    errors['weekly_mileage_comfort'] = "Must be a valid number"

        if 'distance_unit' in preferences:
            if preferences['distance_unit'] not in UserService.VALID_DISTANCE_UNITS:
                errors['distance_unit'] = f"Must be one of: {', '.join(sorted(UserService.VALID_DISTANCE_UNITS))}"

        if 'preferred_model' in preferences:
            model_id = preferences['preferred_model']
            if model_id is not None:
                from services.llm_service import ALL_MODELS
                valid_model_ids = {m['id'] for m in ALL_MODELS}
                if model_id not in valid_model_ids:
                    errors['preferred_model'] = f"Invalid model ID: {model_id}"

        if errors:
            raise ValueError(f"Validation errors: {'; '.join(f'{k}: {v}' for k, v in errors.items())}")

        # Merge into existing preferences
        current = dict(user.preferences) if user.preferences else {}
        allowed_keys = {'available_days', 'experience_level', 'weekly_mileage_comfort', 'distance_unit', 'preferred_model'}
        for key in allowed_keys:
            if key in preferences:
                current[key] = preferences[key]

        user.preferences = current
        db.commit()
        db.refresh(user)
        return user
