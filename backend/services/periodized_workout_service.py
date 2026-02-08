"""
Periodized Workout Service

Orchestrates phase-by-phase LLM workout generation for a training block.
Each phase (base, build, peak, taper) gets a separate LLM call to generate
workouts tailored to that phase's focus.
"""

from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Dict, List, Any
import uuid

from models.training_block import TrainingBlock
from models.workout import Workout
from services.llm_service import LLMService


class PeriodizedWorkoutService:
    """Generates periodized workouts for a training block using LLM."""

    # Phase ordering for generation
    PHASE_ORDER = ["base", "build", "peak", "taper"]

    # Phase focus descriptions for LLM prompting
    PHASE_FOCUS = {
        "base": "Aerobic base building. Focus on easy-effort runs, gradual mileage increases, and building consistency. Include easy runs, long runs at conversational pace, and optional cross-training.",
        "build": "Threshold and tempo work. Introduce tempo runs, longer intervals, and progressive long runs. Increase intensity while maintaining aerobic base. Include tempo runs, cruise intervals, and marathon-pace work.",
        "peak": "Race-specific sharpening. High-intensity intervals, race-pace workouts, and tune-up efforts. Volume slightly reduced from build phase. Include VO2max intervals, race-pace long runs, and speed work.",
        "taper": "Reduced volume, maintain some intensity. Sharp reduction in mileage (40-60% of peak). Short, crisp workouts to stay sharp. Include easy runs, short intervals at race pace, and plenty of rest."
    }

    @staticmethod
    def generate_workouts_for_block(
        db: Session,
        block_id: uuid.UUID,
        experience_level: str = "intermediate",
        llm_service: LLMService = None
    ) -> Dict[str, Any]:
        """
        Generate all workouts for a training block, phase by phase.

        Args:
            db: Database session
            block_id: Training block UUID
            experience_level: "beginner", "intermediate", or "advanced"
            llm_service: Optional LLMService instance (creates one if not provided)

        Returns:
            Dict with workouts_created count and block_id

        Raises:
            ValueError: If block not found or already has workouts
        """
        block = db.query(TrainingBlock).filter(TrainingBlock.id == block_id).first()
        if not block:
            raise ValueError(f"Training block {block_id} not found")

        if block.status != 'active':
            raise ValueError(f"Training block is not active (status: {block.status})")

        # Check if block already has workouts
        existing_count = db.query(Workout).filter(
            Workout.training_block_id == block_id
        ).count()
        if existing_count > 0:
            raise ValueError(f"Training block already has {existing_count} workouts. Delete them first to regenerate.")

        if not llm_service:
            llm_service = LLMService()

        all_workouts = []

        # Generate workouts phase by phase
        for phase_name in PeriodizedWorkoutService.PHASE_ORDER:
            week_numbers = block.phase_map.get(phase_name, [])
            if not week_numbers:
                continue

            phase_focus = PeriodizedWorkoutService.PHASE_FOCUS.get(phase_name, "")

            try:
                phase_workouts = llm_service.generate_periodized_workouts(
                    event_distance=block.event_distance,
                    phase_name=phase_name,
                    phase_focus=phase_focus,
                    week_numbers=week_numbers,
                    total_weeks=block.total_weeks,
                    experience_level=experience_level
                )
            except Exception as e:
                # If a phase fails, commit what we have so far and report
                if all_workouts:
                    db.commit()
                raise ValueError(
                    f"LLM generation failed for {phase_name} phase: {str(e)}. "
                    f"{len(all_workouts)} workouts created from earlier phases."
                )

            # Convert LLM output to Workout models
            for workout_data in phase_workouts:
                week_num = workout_data.get("week")
                day_num = workout_data.get("day")  # 1=Monday, 7=Sunday

                # Calculate scheduled_date
                scheduled_date = None
                if block.start_date and week_num and day_num:
                    # week 1 day 1 = start_date (a Monday)
                    days_offset = (week_num - 1) * 7 + (day_num - 1)
                    scheduled_date = block.start_date + timedelta(days=days_offset)

                workout = Workout(
                    training_block_id=block_id,
                    week=week_num,
                    day=day_num,
                    phase=phase_name,
                    type=workout_data.get("type", "easy_run"),
                    distance_km=workout_data.get("distance_km"),
                    duration_minutes=workout_data.get("duration_minutes"),
                    pace=workout_data.get("pace"),
                    notes=workout_data.get("notes"),
                    scheduled_date=scheduled_date,
                    is_completed=False
                )
                db.add(workout)
                all_workouts.append(workout)

        db.commit()

        return {
            "workouts_created": len(all_workouts),
            "block_id": str(block_id)
        }
