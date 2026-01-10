from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.workout_plan import WorkoutPlan
from models.workout import Workout
import uuid


class WorkoutPlanService:
    """Service for managing workout plans and workouts in the database"""
    
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
        
        # Create workout plan
        workout_plan = WorkoutPlan(
            user_id=user_id,
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
        
        return query.order_by(Workout.scheduled_date, Workout.day).all()
    
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

