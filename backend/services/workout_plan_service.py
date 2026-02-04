from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date, timedelta
from typing import Tuple
import sys
import os
import calendar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.workout_plan import WorkoutPlan
from models.workout import Workout
import uuid


class WorkoutPlanService:
    """Service for managing workout plans and workouts in the database"""
    
    @staticmethod
    def get_week_start_end(target_date: date = None) -> Tuple[date, date]:
        """
        Get the start (Monday) and end (Sunday) dates for a calendar week.
        
        Args:
            target_date: Date within the week (defaults to today)
            
        Returns:
            Tuple of (week_start, week_end) dates
        """
        if target_date is None:
            target_date = date.today()
        
        # Get Monday of the week (weekday() returns 0=Monday, 6=Sunday)
        days_since_monday = target_date.weekday()
        week_start = target_date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        return week_start, week_end
    
    @staticmethod
    def get_week_by_offset(week_offset: int = 0) -> Tuple[date, date]:
        """
        Get week start/end dates by offset from current week.
        
        Args:
            week_offset: 0=current week, -1=last week, +1=next week, etc.
            
        Returns:
            Tuple of (week_start, week_end) dates
        """
        today = date.today()
        target_date = today + timedelta(weeks=week_offset)
        return WorkoutPlanService.get_week_start_end(target_date)
    
    @staticmethod
    def get_month_start_end(year: int, month: int) -> Tuple[date, date]:
        """
        Get the start and end dates for a calendar month.
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            
        Returns:
            Tuple of (month_start, month_end) dates
        """
        month_start = date(year, month, 1)
        # Get last day of month
        last_day = calendar.monthrange(year, month)[1]
        month_end = date(year, month, last_day)
        
        return month_start, month_end
    
    @staticmethod
    def create_workout_plan(db: Session, plan_data: dict, user_id: int = None) -> WorkoutPlan:
        """
        Create a new workout plan from LLM-generated plan data.

        Args:
            db: Database session
            plan_data: Dictionary containing workout plan data from LLM
            user_id: Optional user ID (nullable for MVP)

        Returns:
            Created WorkoutPlan object
        """
        # Extract plan metadata
        goal = plan_data.get('goal', '')
        duration_weeks = plan_data.get('duration_weeks', 0)
        user_request = plan_data.get('user_request', '')

        # Calculate start_date (default to today if not provided)
        start_date = date.today()
        if 'start_date' in plan_data and plan_data['start_date']:
            if isinstance(plan_data['start_date'], str):
                start_date = datetime.fromisoformat(plan_data['start_date']).date()
            else:
                start_date = plan_data['start_date']

        # Auto-generate plan name from goal
        plan_name = WorkoutPlanService.generate_plan_name(goal)

        # Create workout plan
        workout_plan = WorkoutPlan(
            user_id=user_id,
            name=plan_name,
            goal=goal,
            duration_weeks=duration_weeks,
            start_date=start_date,
            user_request=user_request,
            plan_data=plan_data,
            is_active=False  # New plans are not active by default
        )
        
        db.add(workout_plan)
        db.flush()  # Flush to get the plan ID
        
        # Create workouts
        workouts_data = plan_data.get('workouts', [])
        for workout_data in workouts_data:
            workout = WorkoutPlanService._create_workout(
                db, workout_plan.id, workout_data, start_date
            )
            db.add(workout)
        
        db.commit()
        db.refresh(workout_plan)
        
        return workout_plan
    
    @staticmethod
    def _create_workout(db: Session, plan_id: uuid.UUID, workout_data: dict, plan_start_date: date) -> Workout:
        """Create a workout from workout data"""
        week = workout_data.get('week', 1)
        day = workout_data.get('day', 1)
        
        # Calculate scheduled_date: plan_start_date + (week-1)*7 + (day-1) days
        scheduled_date = plan_start_date + timedelta(days=(week - 1) * 7 + (day - 1))
        
        workout = Workout(
            workout_plan_id=plan_id,
            week=week,
            day=day,
            type=workout_data.get('type', 'rest'),
            distance_km=workout_data.get('distance_km'),
            duration_minutes=workout_data.get('duration_minutes'),
            pace=workout_data.get('pace'),
            notes=workout_data.get('notes'),
            scheduled_date=scheduled_date,
            is_completed=False
        )
        
        return workout
    
    @staticmethod
    def get_workout_plan(db: Session, plan_id: uuid.UUID) -> WorkoutPlan:
        """Get a workout plan by ID"""
        return db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    
    @staticmethod
    def get_all_workout_plans(db: Session, user_id: int = None) -> list[WorkoutPlan]:
        """Get all workout plans, optionally filtered by user_id"""
        query = db.query(WorkoutPlan)
        if user_id is not None:
            query = query.filter(WorkoutPlan.user_id == user_id)
        return query.order_by(WorkoutPlan.created_at.desc()).all()
    
    @staticmethod
    def get_active_workout_plan(db: Session, user_id: int = None) -> WorkoutPlan:
        """Get the currently active workout plan"""
        query = db.query(WorkoutPlan).filter(WorkoutPlan.is_active == True)
        if user_id is not None:
            query = query.filter(WorkoutPlan.user_id == user_id)
        return query.first()
    
    @staticmethod
    def set_active_workout_plan(db: Session, plan_id: uuid.UUID, user_id: int = None) -> WorkoutPlan:
        """
        Set a workout plan as active. Deactivates all other plans.
        
        Args:
            db: Database session
            plan_id: ID of plan to activate
            user_id: Optional user ID filter
        
        Returns:
            Activated WorkoutPlan object
        """
        # Deactivate all other plans
        query = db.query(WorkoutPlan).filter(WorkoutPlan.is_active == True)
        if user_id is not None:
            query = query.filter(WorkoutPlan.user_id == user_id)
        
        for plan in query.all():
            plan.is_active = False
        
        # Activate the specified plan
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Workout plan with id {plan_id} not found")
        
        plan.is_active = True
        db.commit()
        db.refresh(plan)
        
        return plan
    
    @staticmethod
    def get_workouts_for_week(db: Session, week_start: date, week_end: date, user_id: int = None) -> list[Workout]:
        """
        Get workouts for a specific week (date range).
        
        Args:
            db: Database session
            week_start: Start date of the week (Monday)
            week_end: End date of the week (Sunday)
            user_id: Optional user ID filter
            
        Returns:
            List of Workout objects
        """
        query = db.query(Workout).join(WorkoutPlan).filter(
            and_(
                Workout.scheduled_date >= week_start,
                Workout.scheduled_date <= week_end,
                WorkoutPlan.is_active == True
            )
        )
        
        if user_id is not None:
            query = query.filter(WorkoutPlan.user_id == user_id)

        # Order by date, then slot (NULL first = single workout, then AM=1, PM=2)
        return query.order_by(Workout.scheduled_date, Workout.slot.nullsfirst()).all()

    @staticmethod
    def get_workouts_for_month(db: Session, year: int, month: int, user_id: int = None) -> list[Workout]:
        """
        Get workouts for a specific calendar month.
        
        Args:
            db: Database session
            year: Year (e.g., 2024)
            month: Month (1-12)
            user_id: Optional user ID filter
            
        Returns:
            List of Workout objects
        """
        month_start, month_end = WorkoutPlanService.get_month_start_end(year, month)
        
        query = db.query(Workout).join(WorkoutPlan).filter(
            and_(
                Workout.scheduled_date >= month_start,
                Workout.scheduled_date <= month_end,
                WorkoutPlan.is_active == True
            )
        )
        
        if user_id is not None:
            query = query.filter(WorkoutPlan.user_id == user_id)

        # Order by date, then slot (NULL first = single workout, then AM=1, PM=2)
        return query.order_by(Workout.scheduled_date, Workout.slot.nullsfirst()).all()

    @staticmethod
    def get_week_progress(db: Session, week_start: date, week_end: date, user_id: int = None) -> dict:
        """
        Get progress summary for a specific week.
        
        Args:
            db: Database session
            week_start: Start date of the week (Monday)
            week_end: End date of the week (Sunday)
            user_id: Optional user ID filter
            
        Returns:
            Dictionary with progress statistics
        """
        workouts = WorkoutPlanService.get_workouts_for_week(db, week_start, week_end, user_id)
        
        total_workouts = len(workouts)
        completed_workouts = sum(1 for w in workouts if w.is_completed)
        completion_percentage = (completed_workouts / total_workouts * 100) if total_workouts > 0 else 0
        
        # Group by day
        workouts_by_day = {}
        for workout in workouts:
            day_key = workout.scheduled_date.isoformat() if workout.scheduled_date else None
            if day_key:
                if day_key not in workouts_by_day:
                    workouts_by_day[day_key] = []
                workouts_by_day[day_key].append(workout.to_dict())
        
        return {
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'total_workouts': total_workouts,
            'completed_workouts': completed_workouts,
            'incomplete_workouts': total_workouts - completed_workouts,
            'completion_percentage': round(completion_percentage, 1),
            'workouts_by_day': workouts_by_day
        }
    
    @staticmethod
    def get_workout(db: Session, workout_id: uuid.UUID) -> Workout:
        """Get a workout by ID"""
        return db.query(Workout).filter(Workout.id == workout_id).first()
    
    @staticmethod
    def toggle_workout_completion(db: Session, workout_id: uuid.UUID) -> Workout:
        """Toggle workout completion status"""
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            raise ValueError(f"Workout with id {workout_id} not found")
        
        workout.is_completed = not workout.is_completed
        if workout.is_completed:
            workout.completed_at = datetime.now()
        else:
            workout.completed_at = None
        
        db.commit()
        db.refresh(workout)
        
        return workout
    
    @staticmethod
    def _validate_workout_type(workout_type: str) -> bool:
        """Validate workout type"""
        valid_types = [
            'long_run', 'tempo', 'intervals', 'easy_run', 'rest', 
            'cross_training', 'recovery', 'fartlek', 'hill_repeats'
        ]
        return workout_type.lower() in valid_types
    
    @staticmethod
    def _validate_workout_data(update_data: dict) -> dict:
        """
        Validate workout update data.
        
        Args:
            update_data: Dictionary with fields to update
            
        Returns:
            Dictionary with validation errors (empty if valid)
        """
        errors = {}
        
        # Validate type
        if 'type' in update_data:
            workout_type = update_data['type']
            if not isinstance(workout_type, str) or not workout_type.strip():
                errors['type'] = "Workout type must be a non-empty string"
            elif not WorkoutPlanService._validate_workout_type(workout_type):
                errors['type'] = f"Invalid workout type. Valid types: long_run, tempo, intervals, easy_run, rest, cross_training, recovery, fartlek, hill_repeats"
        
        # Validate distance_km
        if 'distance_km' in update_data:
            distance = update_data['distance_km']
            if distance is not None:
                try:
                    distance_float = float(distance)
                    if distance_float < 0:
                        errors['distance_km'] = "Distance must be non-negative"
                except (ValueError, TypeError):
                    errors['distance_km'] = "Distance must be a valid number"
        
        # Validate duration_minutes
        if 'duration_minutes' in update_data:
            duration = update_data['duration_minutes']
            if duration is not None:
                try:
                    duration_int = int(duration)
                    if duration_int < 0:
                        errors['duration_minutes'] = "Duration must be non-negative"
                except (ValueError, TypeError):
                    errors['duration_minutes'] = "Duration must be a valid integer"
        
        # Validate pace (must be string if provided)
        if 'pace' in update_data:
            pace = update_data['pace']
            if pace is not None and not isinstance(pace, str):
                errors['pace'] = "Pace must be a string"
        
        # Validate notes (must be string if provided)
        if 'notes' in update_data:
            notes = update_data['notes']
            if notes is not None and not isinstance(notes, str):
                errors['notes'] = "Notes must be a string"
        
        return errors
    
    @staticmethod
    def update_workout(db: Session, workout_id: uuid.UUID, update_data: dict) -> Workout:
        """
        Update workout details. Only updates fields provided in update_data.
        
        Args:
            db: Database session
            workout_id: ID of workout to update
            update_data: Dictionary with fields to update (partial updates supported)
            
        Returns:
            Updated Workout object
            
        Raises:
            ValueError: If workout not found or validation fails
        """
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            raise ValueError(f"Workout with id {workout_id} not found")
        
        # Validate update data
        validation_errors = WorkoutPlanService._validate_workout_data(update_data)
        if validation_errors:
            error_message = "; ".join([f"{k}: {v}" for k, v in validation_errors.items()])
            raise ValueError(f"Validation errors: {error_message}")
        
        # Update only provided fields (partial update)
        updatable_fields = ['type', 'distance_km', 'duration_minutes', 'pace', 'notes']
        
        for field in updatable_fields:
            if field in update_data:
                value = update_data[field]
                # Handle None values (allow clearing fields)
                if value is None or (isinstance(value, str) and value.strip() == ''):
                    setattr(workout, field, None)
                else:
                    # Type conversion for numeric fields
                    if field == 'distance_km':
                        setattr(workout, field, float(value))
                    elif field == 'duration_minutes':
                        setattr(workout, field, int(value))
                    else:
                        setattr(workout, field, value)
        
        # updated_at is automatically set by SQLAlchemy's onupdate
        db.commit()
        db.refresh(workout)

        return workout

    @staticmethod
    def validate_workout_slot(
        db: Session,
        workout_plan_id: uuid.UUID,
        scheduled_date: date,
        slot: int = None,
        exclude_workout_id: uuid.UUID = None
    ) -> bool:
        """
        Validate that a workout slot is available for a given day.
        Max 2 workouts per day allowed.

        Args:
            db: Database session
            workout_plan_id: ID of the workout plan
            scheduled_date: Date to check
            slot: Requested slot (1=AM, 2=PM, or None for auto-assign)
            exclude_workout_id: Workout ID to exclude (for updates)

        Returns:
            True if slot is available

        Raises:
            ValueError: If slot is not available or max workouts exceeded
        """
        query = db.query(Workout).filter(
            Workout.workout_plan_id == workout_plan_id,
            Workout.scheduled_date == scheduled_date
        )

        if exclude_workout_id:
            query = query.filter(Workout.id != exclude_workout_id)

        existing = query.all()

        # Check max 2 per day
        if len(existing) >= 2:
            raise ValueError("Maximum 2 workouts per day allowed")

        # Check if specific slot is requested and already occupied
        if slot and any(w.slot == slot for w in existing):
            slot_name = "AM" if slot == 1 else "PM"
            raise ValueError(f"{slot_name} slot already occupied for this day")

        return True

    @staticmethod
    def get_workouts_for_day(
        db: Session,
        workout_plan_id: uuid.UUID,
        scheduled_date: date
    ) -> list:
        """
        Get all workouts for a specific day in a plan.

        Args:
            db: Database session
            workout_plan_id: ID of the workout plan
            scheduled_date: Date to get workouts for

        Returns:
            List of Workout objects ordered by slot
        """
        return db.query(Workout).filter(
            Workout.workout_plan_id == workout_plan_id,
            Workout.scheduled_date == scheduled_date
        ).order_by(Workout.slot.nullsfirst()).all()

    @staticmethod
    def add_workout_to_day(
        db: Session,
        workout_plan_id: uuid.UUID,
        scheduled_date: date,
        workout_data: dict,
        user_id: int = None
    ) -> Workout:
        """
        Add a workout to a day that may already have one workout.
        Handles slot assignment automatically:
        - If day is empty: new workout gets slot=NULL (single)
        - If day has 1 workout: existing gets slot=1 (AM), new gets slot=2 (PM)
        - If day has 2 workouts: raises error

        Args:
            db: Database session
            workout_plan_id: ID of the workout plan
            scheduled_date: Date to add workout to (ISO string or date object)
            workout_data: Dictionary with workout fields (type, distance_km, etc.)
            user_id: Optional user ID filter

        Returns:
            Created Workout object

        Raises:
            ValueError: If plan not found, max workouts exceeded, or validation fails
        """
        # Convert string date to date object if needed
        if isinstance(scheduled_date, str):
            scheduled_date = datetime.fromisoformat(scheduled_date).date()

        # Verify plan exists and is active
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == workout_plan_id).first()
        if not plan:
            raise ValueError(f"Workout plan with id {workout_plan_id} not found")

        if user_id is not None and plan.user_id != user_id:
            raise ValueError(f"Workout plan with id {workout_plan_id} not found")

        # Get existing workouts for this day
        existing = WorkoutPlanService.get_workouts_for_day(db, workout_plan_id, scheduled_date)

        if len(existing) >= 2:
            raise ValueError("Maximum 2 workouts per day allowed")

        # Determine week/day numbers from scheduled_date
        # Calculate week number: (date - start_date).days // 7 + 1
        if plan.start_date:
            days_diff = (scheduled_date - plan.start_date).days
            week_number = days_diff // 7 + 1
            # Day of week: 1=Monday, 7=Sunday
            day_of_week = scheduled_date.weekday() + 1
        else:
            week_number = 1
            day_of_week = scheduled_date.weekday() + 1

        # Validate workout data
        validation_errors = WorkoutPlanService._validate_workout_data(workout_data)
        if validation_errors:
            error_message = "; ".join([f"{k}: {v}" for k, v in validation_errors.items()])
            raise ValueError(f"Validation errors: {error_message}")

        # Handle slot assignment
        new_slot = None
        if len(existing) == 1:
            # Upgrade existing workout to AM slot if it has no slot
            if existing[0].slot is None:
                existing[0].slot = 1
            # New workout gets PM slot
            new_slot = 2

        # Create new workout
        new_workout = Workout(
            workout_plan_id=workout_plan_id,
            week=week_number,
            day=day_of_week,
            slot=new_slot,
            type=workout_data.get('type', 'rest'),
            distance_km=float(workout_data['distance_km']) if workout_data.get('distance_km') else None,
            duration_minutes=int(workout_data['duration_minutes']) if workout_data.get('duration_minutes') else None,
            pace=workout_data.get('pace'),
            notes=workout_data.get('notes'),
            scheduled_date=scheduled_date,
            is_completed=False
        )

        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)

        return new_workout

    @staticmethod
    def delete_workout(db: Session, workout_id: uuid.UUID, user_id: int = None) -> bool:
        """
        Delete a workout. If this leaves only one workout on the day,
        demote that workout's slot back to NULL.

        Args:
            db: Database session
            workout_id: ID of workout to delete
            user_id: Optional user ID filter

        Returns:
            True if deleted

        Raises:
            ValueError: If workout not found
        """
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            raise ValueError(f"Workout with id {workout_id} not found")

        # Check user_id if provided (via workout plan)
        if user_id is not None:
            plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == workout.workout_plan_id).first()
            if plan and plan.user_id != user_id:
                raise ValueError(f"Workout with id {workout_id} not found")

        # Store date and plan_id before deletion
        scheduled_date = workout.scheduled_date
        workout_plan_id = workout.workout_plan_id

        # Delete the workout
        db.delete(workout)
        db.flush()

        # Check if there's now only one workout left on this day
        remaining = db.query(Workout).filter(
            Workout.workout_plan_id == workout_plan_id,
            Workout.scheduled_date == scheduled_date
        ).all()

        # If exactly one workout remains with a slot, demote it to NULL
        if len(remaining) == 1 and remaining[0].slot is not None:
            remaining[0].slot = None

        db.commit()
        return True

    @staticmethod
    def check_plan_limit(db: Session, max_plans: int = 5) -> dict:
        """
        Check if the plan limit has been reached.
        
        Args:
            db: Database session
            max_plans: Maximum number of plans allowed
            
        Returns:
            Dictionary with limit status and existing plans if at limit
        """
        current_count = db.query(WorkoutPlan).count()
        
        if current_count >= max_plans:
            existing_plans = WorkoutPlanService.get_all_workout_plans(db)
            return {
                "at_limit": True,
                "current_count": current_count,
                "max_allowed": max_plans,
                "existing_plans": [plan.to_dict() for plan in existing_plans]
            }
        
        return {
            "at_limit": False,
            "current_count": current_count,
            "max_allowed": max_plans
        }
    
    @staticmethod
    def generate_plan_name(goal: str, created_at: datetime = None) -> str:
        """
        Generate a default name for a workout plan.

        Uses first 50 chars of goal if available, otherwise generates
        a date-based name like "Plan - Jan 2026".

        Args:
            goal: The workout plan goal text
            created_at: Plan creation timestamp (defaults to now)

        Returns:
            Generated plan name string
        """
        if goal and goal.strip():
            # Truncate goal to 50 chars, add ellipsis if needed
            truncated = goal.strip()[:50]
            if len(goal.strip()) > 50:
                truncated = truncated.rstrip() + "..."
            return truncated

        # Fallback: date-based name
        if created_at is None:
            created_at = datetime.now()
        return f"Plan - {created_at.strftime('%b %Y')}"

    @staticmethod
    def update_workout_plan_name(db: Session, plan_id: uuid.UUID, name: str, user_id: int = None) -> WorkoutPlan:
        """
        Update the name of a workout plan.

        Args:
            db: Database session
            plan_id: ID of the plan to update
            name: New name for the plan (max 255 chars)
            user_id: Optional user ID filter

        Returns:
            Updated WorkoutPlan object

        Raises:
            ValueError: If plan not found or name is invalid
        """
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()

        if not plan:
            raise ValueError(f"Workout plan with id {plan_id} not found")

        # Validate name
        if name is None or not name.strip():
            raise ValueError("Plan name cannot be empty")

        if len(name) > 255:
            raise ValueError("Plan name cannot exceed 255 characters")

        # Check user_id if provided
        if user_id is not None and plan.user_id != user_id:
            raise ValueError(f"Workout plan with id {plan_id} not found")

        plan.name = name.strip()
        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def delete_workout_plan(db: Session, plan_id: uuid.UUID, user_id: int = None) -> bool:
        """
        Delete a workout plan. Cannot delete active plan.

        Args:
            db: Database session
            plan_id: ID of plan to delete
            user_id: Optional user ID filter

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If trying to delete active plan
        """
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()

        if not plan:
            return False

        # Check user_id if provided
        if user_id is not None and plan.user_id != user_id:
            return False

        # Cannot delete active plan
        if plan.is_active:
            raise ValueError("Cannot delete active workout plan. Please deactivate it first.")

        # Delete plan (workouts will be cascade deleted)
        db.delete(plan)
        db.commit()

        return True

