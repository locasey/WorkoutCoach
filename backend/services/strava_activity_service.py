from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Tuple
import uuid
import secrets
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.strava_activity import StravaActivity
from models.strava_session import StravaSession
from models.workout import Workout


class StravaActivityService:
    """Service for managing Strava activities and sessions in the database"""

    # ========================================================================
    # Session Management
    # ========================================================================

    @staticmethod
    def create_session(
        db: Session,
        access_token: str,
        refresh_token: str = None,
        expires_at: datetime = None,
        athlete_id: str = None,
        athlete_firstname: str = None,
        athlete_lastname: str = None,
        user_id: int = None
    ) -> StravaSession:
        """
        Create a new Strava session with server-side token storage.

        Returns:
            StravaSession object with a unique session_token for the client
        """
        # Generate a secure session token for the client
        session_token = secrets.token_urlsafe(48)

        session = StravaSession(
            user_id=user_id,
            session_token=session_token,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            athlete_id=athlete_id,
            athlete_firstname=athlete_firstname,
            athlete_lastname=athlete_lastname
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def get_session_by_token(db: Session, session_token: str) -> Optional[StravaSession]:
        """Get a Strava session by its session token"""
        return db.query(StravaSession).filter(
            StravaSession.session_token == session_token
        ).first()

    @staticmethod
    def get_access_token(db: Session, session_token: str) -> Optional[str]:
        """Get the Strava access token for a given session token"""
        session = StravaActivityService.get_session_by_token(db, session_token)
        if session:
            return session.access_token
        return None

    @staticmethod
    def update_session_tokens(
        db: Session,
        session_token: str,
        access_token: str,
        refresh_token: str = None,
        expires_at: datetime = None
    ) -> Optional[StravaSession]:
        """Update tokens for an existing session (after token refresh)"""
        session = StravaActivityService.get_session_by_token(db, session_token)
        if not session:
            return None

        session.access_token = access_token
        if refresh_token:
            session.refresh_token = refresh_token
        if expires_at:
            session.expires_at = expires_at

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_token: str) -> bool:
        """Delete a Strava session (logout)"""
        session = StravaActivityService.get_session_by_token(db, session_token)
        if not session:
            return False

        db.delete(session)
        db.commit()
        return True

    @staticmethod
    def get_session_for_user(db: Session, user_id: int = None) -> Optional[StravaSession]:
        """Get the active Strava session for a user (MVP: user_id is None)"""
        return db.query(StravaSession).filter(
            StravaSession.user_id == user_id
        ).order_by(StravaSession.created_at.desc()).first()

    # ========================================================================
    # Activity Management
    # ========================================================================

    @staticmethod
    def import_activity(
        db: Session,
        strava_data: dict,
        user_id: int = None
    ) -> StravaActivity:
        """
        Import a single activity from Strava data.
        Updates existing activity if strava_id already exists.
        """
        strava_id = str(strava_data.get('id') or strava_data.get('strava_id'))

        # Check if activity already exists
        existing = db.query(StravaActivity).filter(
            StravaActivity.strava_id == strava_id
        ).first()

        if existing:
            # Update existing activity
            existing.name = strava_data.get('name', existing.name)
            existing.activity_type = strava_data.get('type') or strava_data.get('activity_type', existing.activity_type)
            existing.distance_km = strava_data.get('distance_km') or (strava_data.get('distance', 0) / 1000)
            existing.moving_time_minutes = strava_data.get('moving_time_minutes') or (strava_data.get('moving_time', 0) / 60)
            existing.elapsed_time_minutes = strava_data.get('elapsed_time_minutes') or (strava_data.get('elapsed_time', 0) / 60)
            existing.average_speed_kmh = strava_data.get('average_speed_kmh') or (strava_data.get('average_speed', 0) * 3.6)
            existing.average_heartrate = strava_data.get('average_heartrate')
            existing.max_heartrate = strava_data.get('max_heartrate')
            existing.total_elevation_gain = strava_data.get('total_elevation_gain')
            existing.raw_data = json.dumps(strava_data)

            # Parse start_date
            start_date_str = strava_data.get('start_date_local') or strava_data.get('start_date')
            if start_date_str and isinstance(start_date_str, str):
                try:
                    existing.start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                except ValueError:
                    pass

            db.commit()
            db.refresh(existing)
            return existing

        # Create new activity
        activity = StravaActivity(
            user_id=user_id,
            strava_id=strava_id,
            name=strava_data.get('name', 'Untitled'),
            activity_type=strava_data.get('type') or strava_data.get('activity_type', 'Run'),
            distance_km=strava_data.get('distance_km') or (strava_data.get('distance', 0) / 1000),
            moving_time_minutes=strava_data.get('moving_time_minutes') or (strava_data.get('moving_time', 0) / 60),
            elapsed_time_minutes=strava_data.get('elapsed_time_minutes') or (strava_data.get('elapsed_time', 0) / 60),
            average_speed_kmh=strava_data.get('average_speed_kmh') or (strava_data.get('average_speed', 0) * 3.6),
            average_heartrate=strava_data.get('average_heartrate'),
            max_heartrate=strava_data.get('max_heartrate'),
            total_elevation_gain=strava_data.get('total_elevation_gain'),
            raw_data=json.dumps(strava_data)
        )

        # Parse start_date
        start_date_str = strava_data.get('start_date_local') or strava_data.get('start_date')
        if start_date_str and isinstance(start_date_str, str):
            try:
                activity.start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                pass

        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def import_activities(
        db: Session,
        strava_activities: List[dict],
        user_id: int = None
    ) -> List[StravaActivity]:
        """Import multiple activities from Strava"""
        imported = []
        for activity_data in strava_activities:
            activity = StravaActivityService.import_activity(db, activity_data, user_id)
            imported.append(activity)
        return imported

    @staticmethod
    def get_activity(db: Session, activity_id: uuid.UUID) -> Optional[StravaActivity]:
        """Get a single activity by ID"""
        return db.query(StravaActivity).filter(StravaActivity.id == activity_id).first()

    @staticmethod
    def get_activity_by_strava_id(db: Session, strava_id: str) -> Optional[StravaActivity]:
        """Get activity by Strava's activity ID"""
        return db.query(StravaActivity).filter(StravaActivity.strava_id == strava_id).first()

    @staticmethod
    def get_all_activities(
        db: Session,
        user_id: int = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StravaActivity]:
        """Get all activities for a user, ordered by start_date descending"""
        query = db.query(StravaActivity)
        if user_id is not None:
            query = query.filter(StravaActivity.user_id == user_id)
        return query.order_by(StravaActivity.start_date.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_activities_by_date_range(
        db: Session,
        start_date: date,
        end_date: date,
        user_id: int = None
    ) -> List[StravaActivity]:
        """Get activities within a date range"""
        # Convert dates to datetime for comparison
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        query = db.query(StravaActivity).filter(
            and_(
                StravaActivity.start_date >= start_datetime,
                StravaActivity.start_date <= end_datetime
            )
        )
        if user_id is not None:
            query = query.filter(StravaActivity.user_id == user_id)
        return query.order_by(StravaActivity.start_date.desc()).all()

    @staticmethod
    def get_unlinked_activities(db: Session, user_id: int = None) -> List[StravaActivity]:
        """Get activities that are not linked to any workout"""
        query = db.query(StravaActivity).filter(StravaActivity.linked_workout_id == None)
        if user_id is not None:
            query = query.filter(StravaActivity.user_id == user_id)
        return query.order_by(StravaActivity.start_date.desc()).all()

    @staticmethod
    def link_activity_to_workout(
        db: Session,
        activity_id: uuid.UUID,
        workout_id: uuid.UUID
    ) -> StravaActivity:
        """Link a Strava activity to a planned workout"""
        activity = db.query(StravaActivity).filter(StravaActivity.id == activity_id).first()
        if not activity:
            raise ValueError(f"Activity with id {activity_id} not found")

        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            raise ValueError(f"Workout with id {workout_id} not found")

        activity.linked_workout_id = workout_id
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def unlink_activity(db: Session, activity_id: uuid.UUID) -> StravaActivity:
        """Remove the link between an activity and a workout"""
        activity = db.query(StravaActivity).filter(StravaActivity.id == activity_id).first()
        if not activity:
            raise ValueError(f"Activity with id {activity_id} not found")

        activity.linked_workout_id = None
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def delete_activity(db: Session, activity_id: uuid.UUID) -> bool:
        """Delete an activity"""
        activity = db.query(StravaActivity).filter(StravaActivity.id == activity_id).first()
        if not activity:
            return False

        db.delete(activity)
        db.commit()
        return True

    @staticmethod
    def get_activity_count(db: Session, user_id: int = None) -> int:
        """Get total count of imported activities"""
        query = db.query(func.count(StravaActivity.id))
        if user_id is not None:
            query = query.filter(StravaActivity.user_id == user_id)
        return query.scalar()

    # ========================================================================
    # Activity Matching
    # ========================================================================

    @staticmethod
    def find_matching_activities_for_workout(
        db: Session,
        workout: Workout,
        tolerance_days: int = 1
    ) -> List[StravaActivity]:
        """
        Find Strava activities that might match a planned workout.
        Matches based on scheduled date (with tolerance) and activity type.
        """
        if not workout.scheduled_date:
            return []

        start_date = workout.scheduled_date - timedelta(days=tolerance_days)
        end_date = workout.scheduled_date + timedelta(days=tolerance_days)

        # Get activities in the date range
        activities = StravaActivityService.get_activities_by_date_range(
            db, start_date, end_date
        )

        # Filter by activity type if workout type suggests a specific activity
        workout_type_lower = workout.type.lower() if workout.type else ''
        matching = []

        for activity in activities:
            activity_type_lower = activity.activity_type.lower() if activity.activity_type else ''

            # Match running workouts to Run activities
            if any(t in workout_type_lower for t in ['run', 'tempo', 'interval', 'easy', 'long', 'fartlek', 'hill']):
                if activity_type_lower == 'run':
                    matching.append(activity)
            # Match cross-training to various activity types
            elif 'cross' in workout_type_lower:
                if activity_type_lower in ['ride', 'swim', 'walk', 'hike', 'yoga']:
                    matching.append(activity)
            # Match rest days - no activities expected
            elif 'rest' in workout_type_lower:
                continue
            # Default: include if types seem related
            else:
                matching.append(activity)

        return matching

    @staticmethod
    def auto_link_activities_to_workouts(
        db: Session,
        user_id: int = None,
        tolerance_days: int = 0
    ) -> int:
        """
        Automatically link unlinked activities to matching workouts.
        Returns the number of activities linked.
        """
        from models.workout_plan import WorkoutPlan

        # Get unlinked activities
        unlinked = StravaActivityService.get_unlinked_activities(db, user_id)

        # Get workouts from active plan that don't have linked activities
        active_plan = db.query(WorkoutPlan).filter(WorkoutPlan.is_active == True).first()
        if not active_plan:
            return 0

        workouts = db.query(Workout).filter(
            Workout.workout_plan_id == active_plan.id
        ).all()

        linked_count = 0
        for activity in unlinked:
            if not activity.start_date:
                continue

            activity_date = activity.start_date.date()

            for workout in workouts:
                if not workout.scheduled_date:
                    continue

                # Check if dates match (with tolerance)
                date_diff = abs((activity_date - workout.scheduled_date).days)
                if date_diff > tolerance_days:
                    continue

                # Check if workout already has a linked activity
                existing_link = db.query(StravaActivity).filter(
                    StravaActivity.linked_workout_id == workout.id
                ).first()
                if existing_link:
                    continue

                # Check activity type compatibility
                workout_type = workout.type.lower() if workout.type else ''
                activity_type = activity.activity_type.lower() if activity.activity_type else ''

                # Skip rest days
                if 'rest' in workout_type:
                    continue

                # Match running activities
                if activity_type == 'run' and any(t in workout_type for t in ['run', 'tempo', 'interval', 'easy', 'long', 'fartlek', 'hill', 'recovery']):
                    activity.linked_workout_id = workout.id
                    linked_count += 1
                    break

        db.commit()
        return linked_count
