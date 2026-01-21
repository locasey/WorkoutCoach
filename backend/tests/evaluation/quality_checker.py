"""
Quality checker for generated workout plans.

Performs automated validation and scoring of workout plans
to ensure they meet safety and quality standards.
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict


class QualityChecker:
    """Automated quality checker for workout plans."""

    # Weights for each check (must sum to 100)
    WEIGHTS = {
        'completeness': 20,
        'duration_match': 15,
        'rest_days': 15,
        'workout_variety': 15,
        'taper_present': 15,
        'progressive_build': 20
    }

    def __init__(self, plan: Dict[str, Any], expected: Dict[str, Any] = None):
        """
        Initialize the quality checker.

        Args:
            plan: The generated workout plan dictionary
            expected: Expected values from test prompt (optional)
        """
        self.plan = plan
        self.expected = expected or {}
        self.issues: List[str] = []
        self.check_results: Dict[str, Tuple[float, str]] = {}

    def check_all(self) -> Dict[str, Any]:
        """
        Run all quality checks and return a comprehensive report.

        Returns:
            Dictionary with overall score, individual check scores, and issues
        """
        self.issues = []
        self.check_results = {}

        # Run all checks
        self.check_results['completeness'] = self._check_completeness()
        self.check_results['duration_match'] = self._check_duration_match()
        self.check_results['rest_days'] = self._check_rest_days()
        self.check_results['workout_variety'] = self._check_workout_variety()
        self.check_results['taper_present'] = self._check_taper_present()
        self.check_results['progressive_build'] = self._check_progressive_build()

        # Calculate weighted overall score
        overall_score = sum(
            self.check_results[check][0] * self.WEIGHTS[check] / 100
            for check in self.check_results
        )

        return {
            'overall_score': round(overall_score, 1),
            'checks': {
                name: {
                    'score': round(result[0], 1),
                    'weight': self.WEIGHTS[name],
                    'detail': result[1]
                }
                for name, result in self.check_results.items()
            },
            'issues': self.issues,
            'passed': overall_score >= 70
        }

    def _check_completeness(self) -> Tuple[float, str]:
        """
        Check that the plan has all required fields and workouts for each week.

        Returns:
            Tuple of (score 0-100, detail message)
        """
        required_fields = ['goal', 'duration_weeks', 'workouts']
        missing_fields = []

        for field in required_fields:
            if field not in self.plan or self.plan[field] is None:
                missing_fields.append(field)
                self.issues.append(f"Missing required field: {field}")

        if missing_fields:
            return (0.0, f"Missing fields: {', '.join(missing_fields)}")

        # Check workouts exist
        workouts = self.plan.get('workouts', [])
        if not workouts:
            self.issues.append("No workouts in plan")
            return (0.0, "No workouts found")

        # Check each week has workouts
        duration = self.plan.get('duration_weeks', 0)
        weeks_with_workouts = set()
        for workout in workouts:
            week = workout.get('week')
            if week:
                weeks_with_workouts.add(week)

        missing_weeks = []
        for week in range(1, duration + 1):
            if week not in weeks_with_workouts:
                missing_weeks.append(week)

        if missing_weeks:
            self.issues.append(f"Missing workouts for weeks: {missing_weeks}")
            coverage = (duration - len(missing_weeks)) / duration * 100 if duration > 0 else 0
            return (coverage, f"Missing {len(missing_weeks)} weeks")

        return (100.0, "All fields and weeks present")

    def _check_duration_match(self) -> Tuple[float, str]:
        """
        Check that duration_weeks matches the expected value.

        Returns:
            Tuple of (score 0-100, detail message)
        """
        expected_duration = self.expected.get('duration_weeks')
        actual_duration = self.plan.get('duration_weeks')

        if expected_duration is None:
            return (100.0, "No expected duration specified")

        if actual_duration is None:
            self.issues.append("Plan missing duration_weeks field")
            return (0.0, "Missing duration_weeks")

        if actual_duration == expected_duration:
            return (100.0, f"Duration matches: {actual_duration} weeks")

        # Partial credit for close values
        diff = abs(actual_duration - expected_duration)
        if diff <= 1:
            self.issues.append(f"Duration off by 1 week (expected {expected_duration}, got {actual_duration})")
            return (75.0, f"Expected {expected_duration}, got {actual_duration}")
        elif diff <= 2:
            self.issues.append(f"Duration off by {diff} weeks (expected {expected_duration}, got {actual_duration})")
            return (50.0, f"Expected {expected_duration}, got {actual_duration}")
        else:
            self.issues.append(f"Duration significantly off (expected {expected_duration}, got {actual_duration})")
            return (0.0, f"Expected {expected_duration}, got {actual_duration}")

    def _check_rest_days(self) -> Tuple[float, str]:
        """
        Check that each week has at least 1 rest day.

        Returns:
            Tuple of (score 0-100, detail message)
        """
        workouts = self.plan.get('workouts', [])
        duration = self.plan.get('duration_weeks', 0)

        if not workouts or duration == 0:
            return (0.0, "No workouts to check")

        # Count rest days per week
        rest_days_per_week = defaultdict(int)
        workout_days_per_week = defaultdict(set)

        for workout in workouts:
            week = workout.get('week', 0)
            day = workout.get('day', 0)
            workout_type = workout.get('type', '').lower()

            workout_days_per_week[week].add(day)
            if workout_type == 'rest':
                rest_days_per_week[week] += 1

        # Check each week
        weeks_without_rest = []
        for week in range(1, duration + 1):
            days_used = len(workout_days_per_week.get(week, set()))
            rest_count = rest_days_per_week.get(week, 0)

            # Consider implicit rest days (if fewer than 7 days scheduled)
            implicit_rest = 7 - days_used
            total_rest = rest_count + implicit_rest

            if total_rest < 1:
                weeks_without_rest.append(week)

        if weeks_without_rest:
            self.issues.append(f"Weeks without rest days: {weeks_without_rest}")
            score = (duration - len(weeks_without_rest)) / duration * 100 if duration > 0 else 0
            return (score, f"{len(weeks_without_rest)} weeks without rest")

        return (100.0, "All weeks have rest days")

    def _check_workout_variety(self) -> Tuple[float, str]:
        """
        Check that the plan has a mix of workout types.

        Returns:
            Tuple of (score 0-100, detail message)
        """
        workouts = self.plan.get('workouts', [])
        if not workouts:
            return (0.0, "No workouts to check")

        # Get expected workout types
        expected_types = set(self.expected.get('should_have_types', []))
        if not expected_types:
            expected_types = {'easy_run', 'long_run'}  # Minimum expected

        # Count actual workout types
        actual_types = set()
        for workout in workouts:
            workout_type = workout.get('type', '').lower()
            if workout_type and workout_type != 'rest':
                actual_types.add(workout_type)

        # Check coverage
        found_expected = expected_types.intersection(actual_types)
        missing_types = expected_types - actual_types

        if missing_types:
            self.issues.append(f"Missing expected workout types: {list(missing_types)}")

        if not found_expected:
            return (0.0, f"None of expected types found: {list(expected_types)}")

        # Score based on coverage
        coverage = len(found_expected) / len(expected_types) * 100

        # Bonus for having extra variety
        extra_types = actual_types - expected_types
        if extra_types:
            coverage = min(100.0, coverage + 10)

        return (coverage, f"Found {len(found_expected)}/{len(expected_types)} expected types")

    def _check_taper_present(self) -> Tuple[float, str]:
        """
        Check that the final 1-2 weeks show reduced volume (taper).

        Returns:
            Tuple of (score 0-100, detail message)
        """
        workouts = self.plan.get('workouts', [])
        duration = self.plan.get('duration_weeks', 0)

        if not workouts or duration < 3:
            return (100.0, "Plan too short for taper check")

        # Calculate volume per week (sum of distances or durations)
        volume_per_week = defaultdict(float)
        for workout in workouts:
            week = workout.get('week', 0)
            workout_type = workout.get('type', '').lower()

            if workout_type == 'rest':
                continue

            distance = workout.get('distance_km') or 0
            duration_min = workout.get('duration_minutes') or 0

            # Prefer distance, fall back to duration
            volume = distance if distance > 0 else duration_min / 10
            volume_per_week[week] += volume

        if not volume_per_week:
            self.issues.append("Could not calculate weekly volumes")
            return (50.0, "Unable to calculate volumes")

        # Get peak volume (excluding last 2 weeks)
        pre_taper_weeks = [w for w in range(1, duration - 1)]
        if not pre_taper_weeks:
            return (100.0, "Plan too short for meaningful taper check")

        peak_volume = max(volume_per_week.get(w, 0) for w in pre_taper_weeks)
        final_week_volume = volume_per_week.get(duration, 0)
        second_last_volume = volume_per_week.get(duration - 1, 0)

        if peak_volume == 0:
            return (50.0, "No volume data to compare")

        # Check if final weeks show reduction
        final_reduction = (peak_volume - final_week_volume) / peak_volume if peak_volume > 0 else 0
        second_last_reduction = (peak_volume - second_last_volume) / peak_volume if peak_volume > 0 else 0

        # Final week should be at least 30% reduced, second-to-last at least 15%
        has_final_taper = final_reduction >= 0.30
        has_gradual_taper = second_last_reduction >= 0.15

        if has_final_taper and has_gradual_taper:
            return (100.0, f"Good taper: {int(final_reduction*100)}% reduction in final week")
        elif has_final_taper:
            return (80.0, f"Final week tapered ({int(final_reduction*100)}%), but no gradual reduction")
        elif final_reduction >= 0.15:
            self.issues.append(f"Taper may be insufficient: only {int(final_reduction*100)}% reduction")
            return (60.0, f"Weak taper: {int(final_reduction*100)}% reduction")
        else:
            self.issues.append("No taper detected - final weeks have similar volume to peak")
            return (20.0, "No taper detected")

    def _check_progressive_build(self) -> Tuple[float, str]:
        """
        Check that there's an overall trend of increasing volume until taper.

        Returns:
            Tuple of (score 0-100, detail message)
        """
        workouts = self.plan.get('workouts', [])
        duration = self.plan.get('duration_weeks', 0)

        if not workouts or duration < 4:
            return (100.0, "Plan too short for progression check")

        # Calculate volume per week
        volume_per_week = defaultdict(float)
        for workout in workouts:
            week = workout.get('week', 0)
            workout_type = workout.get('type', '').lower()

            if workout_type == 'rest':
                continue

            distance = workout.get('distance_km') or 0
            duration_min = workout.get('duration_minutes') or 0
            volume = distance if distance > 0 else duration_min / 10
            volume_per_week[week] += volume

        if not volume_per_week:
            return (50.0, "Unable to calculate volumes")

        # Get volumes for pre-taper weeks (exclude last 2)
        taper_start = max(1, duration - 1)
        pre_taper_volumes = [volume_per_week.get(w, 0) for w in range(1, taper_start)]

        if len(pre_taper_volumes) < 3:
            return (100.0, "Not enough weeks to check progression")

        # Check for overall upward trend
        # Compare first half average to second half average
        mid = len(pre_taper_volumes) // 2
        first_half_avg = sum(pre_taper_volumes[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(pre_taper_volumes[mid:]) / (len(pre_taper_volumes) - mid) if (len(pre_taper_volumes) - mid) > 0 else 0

        if first_half_avg == 0:
            return (50.0, "First half has no volume data")

        progression_ratio = second_half_avg / first_half_avg if first_half_avg > 0 else 0

        # Count increasing week-over-week transitions
        increases = 0
        decreases = 0
        for i in range(1, len(pre_taper_volumes)):
            if pre_taper_volumes[i] > pre_taper_volumes[i-1]:
                increases += 1
            elif pre_taper_volumes[i] < pre_taper_volumes[i-1] * 0.9:  # Allow 10% variation
                decreases += 1

        # Score based on progression
        if progression_ratio >= 1.2:
            return (100.0, f"Good progression: {int((progression_ratio-1)*100)}% volume increase")
        elif progression_ratio >= 1.1:
            return (85.0, f"Moderate progression: {int((progression_ratio-1)*100)}% increase")
        elif progression_ratio >= 1.0:
            return (70.0, "Slight progression detected")
        elif progression_ratio >= 0.9:
            self.issues.append("Volume is relatively flat - consider more progression")
            return (50.0, "Flat progression")
        else:
            self.issues.append("Volume decreases over time - plan may be regressive")
            return (20.0, "Regressive volume pattern")


def check_plan_quality(plan: Dict[str, Any], expected: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience function to check plan quality.

    Args:
        plan: The generated workout plan
        expected: Expected values from test prompt (optional)

    Returns:
        Quality check report dictionary
    """
    checker = QualityChecker(plan, expected)
    return checker.check_all()
