"""
Coach Context Service

Builds a structured snapshot of the athlete's current training context from the DB
and renders it as a formatted string for injection into LLM prompts.

This gives the coach awareness of:
- Current training block and phase
- Last 2 weeks of workout history (completions, skips, notes)
- User preferences (available days, mileage comfort, experience level)
- Reserved slot for future Strava data
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_


def build_context_snapshot(
    db: Session,
    user_id: uuid.UUID,
    week_offset: int = 0
) -> Dict[str, Any]:
    """
    Build a structured context snapshot from the DB for a given user.

    Args:
        db: Database session
        user_id: User UUID
        week_offset: Week offset for calculating history window (0=current week)

    Returns:
        Dict with block, phase, recent_workouts, preferences, strava_data keys
    """
    from models.user import User
    from models.workout import Workout
    from models.training_block import TrainingBlock

    # Fetch user preferences
    user = db.query(User).filter(User.id == user_id).first()
    prefs = user.preferences or {} if user else {}

    # Get active training block
    block = db.query(TrainingBlock).filter(
        TrainingBlock.status == 'active',
        TrainingBlock.user_id == user_id
    ).first()

    block_snapshot = None
    phase_snapshot = None

    if block and block.start_date:
        today = date.today()
        current_week_number = (today - block.start_date).days // 7 + 1
        current_week_number = max(1, min(current_week_number, block.total_weeks))

        # Find current phase and week-in-phase
        current_phase = None
        week_in_phase = None
        if block.phase_map:
            for phase_name, weeks in block.phase_map.items():
                if current_week_number in weeks:
                    current_phase = phase_name
                    # week_in_phase is the index within the phase (1-based)
                    sorted_weeks = sorted(weeks)
                    week_in_phase = sorted_weeks.index(current_week_number) + 1
                    break

        weeks_until_race = block.get_weeks_until_race()

        block_snapshot = {
            "event_name": block.event_name,
            "event_distance": block.event_distance,
            "target_date": block.target_date.isoformat() if block.target_date else None,
            "start_date": block.start_date.isoformat(),
            "total_weeks": block.total_weeks,
            "current_week_number": current_week_number,
            "weeks_until_race": weeks_until_race,
        }

        if current_phase:
            from services.training_block_service import TrainingBlockService
            phase_focus = TrainingBlockService.PHASE_FOCUS.get(current_phase, "")
            phase_weeks = block.phase_map.get(current_phase, [])
            phase_snapshot = {
                "name": current_phase,
                "focus": phase_focus,
                "week_in_phase": week_in_phase,
                "phase_total_weeks": len(phase_weeks),
            }

    # Fetch recent workouts: last 2 calendar weeks relative to week_offset
    recent_workouts = []
    if block:
        today = date.today() + timedelta(weeks=week_offset)
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        history_start = week_start - timedelta(weeks=2)
        history_end = week_start - timedelta(days=1)  # up to (not including) current week

        workouts = db.query(Workout).filter(
            and_(
                Workout.training_block_id == block.id,
                Workout.scheduled_date >= history_start,
                Workout.scheduled_date <= history_end
            )
        ).order_by(Workout.scheduled_date).all()

        for w in workouts:
            recent_workouts.append({
                "date": w.scheduled_date.isoformat() if w.scheduled_date else None,
                "type": w.type,
                "distance_km": w.distance_km,
                "duration_minutes": w.duration_minutes,
                "is_completed": w.is_completed,
                "notes": w.notes,
                "actuals": w.actuals,
            })

    return {
        "block": block_snapshot,
        "phase": phase_snapshot,
        "recent_workouts": recent_workouts[:14],  # max 14 entries for token budget
        "preferences": {
            "experience_level": prefs.get("experience_level", "intermediate"),
            "available_days": prefs.get("available_days", []),
            "weekly_mileage_comfort": prefs.get("weekly_mileage_comfort"),
            "distance_unit": prefs.get("distance_unit", "mi"),
        },
        "strava_data": None,  # reserved for future Strava integration
    }


def render_context_prompt(snapshot: Dict[str, Any]) -> str:
    """
    Render a structured context snapshot as a formatted string for LLM injection.

    Returns "" if there is no meaningful context to inject.
    """
    block = snapshot.get("block")
    phase = snapshot.get("phase")
    prefs = snapshot.get("preferences") or {}
    recent_workouts = snapshot.get("recent_workouts") or []

    # Only inject if we have something meaningful
    has_prefs = any([
        prefs.get("experience_level"),
        prefs.get("available_days"),
        prefs.get("weekly_mileage_comfort"),
    ])
    if not block and not has_prefs:
        return ""

    lines = ["=== ATHLETE CONTEXT ==="]

    # Training block info
    if block:
        event_name = block.get("event_name", "")
        event_distance = block.get("event_distance", "")
        target_date = block.get("target_date", "")
        weeks_until_race = block.get("weeks_until_race")
        current_week = block.get("current_week_number")
        total_weeks = block.get("total_weeks")

        race_line = f"Race: {event_name} ({event_distance}) on {target_date}"
        if weeks_until_race is not None:
            race_line += f" — {weeks_until_race} weeks out"
        lines.append(race_line)

        training_line = f"Training: Week {current_week} of {total_weeks}"
        if phase:
            phase_name = phase.get("name", "")
            week_in_phase = phase.get("week_in_phase")
            phase_total = phase.get("phase_total_weeks")
            training_line += f" | Phase: {phase_name}"
            if week_in_phase and phase_total:
                training_line += f" (week {week_in_phase}/{phase_total} of phase)"
        lines.append(training_line)

    # Athlete preferences
    exp = prefs.get("experience_level", "")
    available_days = prefs.get("available_days") or []
    mileage = prefs.get("weekly_mileage_comfort")
    unit = prefs.get("distance_unit", "mi")

    pref_parts = []
    if exp:
        pref_parts.append(f"Experience: {exp}")
    if available_days:
        day_abbrevs = {
            "mon": "Mon", "tue": "Tue", "wed": "Wed", "thu": "Thu",
            "fri": "Fri", "sat": "Sat", "sun": "Sun"
        }
        formatted_days = ",".join(day_abbrevs.get(d.lower(), d) for d in available_days)
        pref_parts.append(f"Available days: {formatted_days}")
    if mileage is not None:
        pref_parts.append(f"Mileage comfort: {mileage} {unit}/week")
    if pref_parts:
        lines.append(" | ".join(pref_parts))

    # Recent workout history
    if recent_workouts:
        lines.append("")
        lines.append("Recent workouts (last 2 weeks):")
        for w in recent_workouts:
            if not w.get("date"):
                continue
            parts = [f"- {w['date']} {w.get('type', '')}"]
            if w.get("distance_km"):
                parts[0] += f" {w['distance_km']}km"
            if w.get("duration_minutes"):
                parts[0] += f" {w['duration_minutes']}min"

            status = "COMPLETED" if w.get("is_completed") else "SKIPPED"
            parts[0] += f" — {status}"

            # Add actuals if different from planned
            actuals = w.get("actuals")
            if actuals and isinstance(actuals, dict):
                actual_parts = []
                if actuals.get("distance"):
                    actual_parts.append(f"actual: {actuals['distance']}km")
                if actuals.get("duration"):
                    actual_parts.append(f"{actuals['duration']}min")
                if actual_parts:
                    parts[0] += f" ({', '.join(actual_parts)})"

            # Add notes
            notes = w.get("notes")
            if notes:
                # Truncate long notes
                notes_str = notes[:80] + "..." if len(notes) > 80 else notes
                parts[0] += f' (notes: "{notes_str}")'

            lines.append(parts[0])

        # Compute adherence advisory for most recent week
        if recent_workouts:
            # Find workouts from the most recent week in the history
            # (last 7 days of the history window)
            last_date_str = max(
                w["date"] for w in recent_workouts if w.get("date")
            )
            from datetime import date as date_type
            last_date = date_type.fromisoformat(last_date_str)
            recent_week_start = last_date - timedelta(days=last_date.weekday())

            last_week_workouts = [
                w for w in recent_workouts
                if w.get("date") and date_type.fromisoformat(w["date"]) >= recent_week_start
            ]
            skipped_non_rest = sum(
                1 for w in last_week_workouts
                if not w.get("is_completed") and w.get("type", "") != "rest"
            )
            completed_all = all(
                w.get("is_completed") or w.get("type", "") == "rest"
                for w in last_week_workouts
            )

            lines.append("")
            if skipped_non_rest >= 2:
                lines.append(f"Consider: athlete skipped {skipped_non_rest} workouts last week — adjust load accordingly.")
            elif completed_all and last_week_workouts:
                lines.append("Consider: athlete completed all workouts last week — maintain or slightly increase load.")
    else:
        lines.append("")
        lines.append("No recent workout history available.")

    lines.append("=== END CONTEXT ===")
    return "\n".join(lines)
