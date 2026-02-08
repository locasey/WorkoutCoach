from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.training_block import TrainingBlock
from models.workout import Workout


class TrainingBlockService:
    """Service for managing training blocks and the new weekly view"""

    # Phase focus descriptions for LLM context
    PHASE_FOCUS = {
        "base": "Aerobic base building, easy runs, building mileage",
        "build": "Tempo and threshold work, increasing intensity",
        "peak": "Race-specific workouts, sharpening",
        "taper": "Reduced volume, maintaining intensity, rest"
    }

    @staticmethod
    def get_active_block(db: Session, user_id: int = None) -> Optional[TrainingBlock]:
        """Get the user's active training block (or None if in maintenance mode)."""
        query = db.query(TrainingBlock).filter(
            TrainingBlock.status == 'active'  # Use string value for PostgreSQL enum
        )
        if user_id is not None:
            query = query.filter(TrainingBlock.user_id == user_id)
        return query.first()

    @staticmethod
    def get_block_by_id(db: Session, block_id: uuid.UUID) -> Optional[TrainingBlock]:
        """Get a training block by ID."""
        return db.query(TrainingBlock).filter(TrainingBlock.id == block_id).first()

    @staticmethod
    def create_training_block(
        db: Session,
        event_name: str,
        event_distance: str,
        target_date: date,
        total_weeks: int,
        phase_map: Dict[str, List[int]],
        start_date: date = None,
        user_id: int = None
    ) -> TrainingBlock:
        """
        Create a new training block.

        Args:
            db: Database session
            event_name: Name of the event (e.g., "Boston Marathon")
            event_distance: Distance type ("marathon", "half", "10k", "5k", or custom)
            target_date: Race day
            total_weeks: Total weeks in the training plan
            phase_map: Dict mapping phase names to week numbers
            start_date: When training begins (defaults to calculated from target_date - total_weeks)
            user_id: Optional user ID

        Returns:
            Created TrainingBlock instance
        """
        # Deactivate any existing active block for this user
        existing = TrainingBlockService.get_active_block(db, user_id)
        if existing:
            existing.status = 'abandoned'

        # Calculate start_date if not provided
        if start_date is None:
            start_date = target_date - timedelta(weeks=total_weeks)

        block = TrainingBlock(
            user_id=user_id,
            event_name=event_name,
            event_distance=event_distance,
            target_date=target_date,
            start_date=start_date,
            total_weeks=total_weeks,
            phase_map=phase_map,
            status='active'
        )

        db.add(block)
        db.commit()
        db.refresh(block)
        return block

    @staticmethod
    def update_training_block(
        db: Session,
        block_id: uuid.UUID,
        **updates
    ) -> Optional[TrainingBlock]:
        """Update a training block's fields."""
        block = TrainingBlockService.get_block_by_id(db, block_id)
        if not block:
            return None

        allowed_fields = ['event_name', 'event_distance', 'target_date', 'start_date', 'total_weeks']
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(block, field, value)

        db.commit()
        db.refresh(block)
        return block

    @staticmethod
    def update_phases(
        db: Session,
        block_id: uuid.UUID,
        phase_map: Dict[str, List[int]]
    ) -> Optional[TrainingBlock]:
        """Update the phase structure of a training block."""
        block = TrainingBlockService.get_block_by_id(db, block_id)
        if not block:
            return None

        block.phase_map = phase_map
        db.commit()
        db.refresh(block)
        return block

    @staticmethod
    def end_training_block(
        db: Session,
        block_id: uuid.UUID,
        completed: bool = False
    ) -> Optional[TrainingBlock]:
        """End a training block (mark as completed or abandoned)."""
        block = TrainingBlockService.get_block_by_id(db, block_id)
        if not block:
            return None

        block.status = 'completed' if completed else 'abandoned'
        db.commit()
        db.refresh(block)
        return block

    @staticmethod
    def get_week_context(db: Session, week_offset: int = 0, user_id: int = None) -> Dict[str, Any]:
        """
        Get the weekly view context for the frontend.

        Returns different shapes based on training vs maintenance mode.

        Args:
            db: Database session
            week_offset: 0=current week, -1=last week, +1=next week
            user_id: Optional user ID

        Returns:
            Dict with mode, week info, and workouts
        """
        # Calculate target week dates
        today = date.today()
        target_date = today + timedelta(weeks=week_offset)
        days_since_monday = target_date.weekday()
        week_start = target_date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)

        # Get active training block
        block = TrainingBlockService.get_active_block(db, user_id)

        # Get workouts for this week
        workout_query = db.query(Workout).filter(
            and_(
                Workout.scheduled_date >= week_start,
                Workout.scheduled_date <= week_end
            )
        )
        if user_id is not None:
            # Filter by training_block's user_id or workout_plan's user_id
            # For now, we'll get all workouts since user_id isn't on Workout directly
            pass

        workouts = workout_query.order_by(
            Workout.scheduled_date,
            Workout.slot.nullsfirst()
        ).all()

        if block:
            # Training mode
            current_week = block.get_current_week()
            current_phase = block.get_current_phase()

            # Calculate week number for the target week (not just current)
            if block.start_date:
                days_from_start = (week_start - block.start_date).days
                target_week_number = (days_from_start // 7) + 1
                if target_week_number < 1:
                    target_week_number = None
                elif target_week_number > block.total_weeks:
                    target_week_number = None
            else:
                target_week_number = current_week

            # Get phase for target week
            target_phase = None
            if target_week_number and block.phase_map:
                for phase_name, weeks in block.phase_map.items():
                    if target_week_number in weeks:
                        target_phase = phase_name
                        break

            return {
                "mode": "training",
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "week_number": target_week_number,
                "total_weeks": block.total_weeks,
                "phase": target_phase,
                "phase_focus": TrainingBlockService.PHASE_FOCUS.get(target_phase) if target_phase else None,
                "weeks_until_race": block.get_weeks_until_race(),
                "event_name": block.event_name,
                "event_distance": block.event_distance,
                "target_date": block.target_date.isoformat() if block.target_date else None,
                "block_id": str(block.id),
                "workouts": [w.to_dict() for w in workouts]
            }
        else:
            # Maintenance mode
            return {
                "mode": "maintenance",
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "week_number": None,
                "total_weeks": None,
                "phase": None,
                "phase_focus": None,
                "weeks_until_race": None,
                "event_name": None,
                "event_distance": None,
                "target_date": None,
                "block_id": None,
                "workouts": [w.to_dict() for w in workouts]
            }

    @staticmethod
    def get_block_overview(db: Session, block_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get full training block overview for visualization."""
        block = TrainingBlockService.get_block_by_id(db, block_id)
        if not block:
            return None

        current_week = block.get_current_week()

        # Build phase status
        phases = []
        if block.phase_map:
            for phase_name in ["base", "build", "peak", "taper"]:
                weeks = block.phase_map.get(phase_name, [])
                if weeks:
                    if current_week and max(weeks) < current_week:
                        status = "completed"
                    elif current_week and min(weeks) <= current_week <= max(weeks):
                        status = "current"
                    else:
                        status = "upcoming"

                    phases.append({
                        "name": phase_name,
                        "weeks": weeks,
                        "status": status
                    })

        # Get completion stats
        workouts = db.query(Workout).filter(
            Workout.training_block_id == block_id
        ).all()

        total_workouts = len([w for w in workouts if w.type != 'rest'])
        completed_workouts = len([w for w in workouts if w.is_completed and w.type != 'rest'])
        completion_rate = completed_workouts / total_workouts if total_workouts > 0 else 0

        total_distance = sum(w.distance_km or 0 for w in workouts if w.is_completed)

        return {
            "block": block.to_dict(),
            "phases": phases,
            "current_week": current_week,
            "completion_rate": round(completion_rate, 2),
            "total_distance_km": round(total_distance, 1),
            "completed_workouts": completed_workouts,
            "total_workouts": total_workouts
        }
