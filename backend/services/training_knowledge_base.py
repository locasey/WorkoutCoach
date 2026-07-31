"""
Curated, evidence-based training principles for maintenance-mode workout generation.

Original synthesis of well-established aerobic/running training science (polarized
training, aerobic base building, progressive-overload/injury-prevention heuristics,
etc.) — these are widely-taught concepts, not text sourced from any single
copyrighted book or paper.

DRAFT — LOC-156: review for accuracy before this ships as real coaching advice
that affects people's actual training. Ideally reviewed by someone with exercise
science / coaching background, not just for code correctness.
"""

PRINCIPLES = [
    {
        "id": "polarized-8020",
        "topic": "intensity_distribution",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 2, "max_days": 7,
        "text": "Aim for roughly 80% of weekly running at an easy, conversational effort and "
                "20% at moderate-to-hard effort. Most runners maintaining general fitness benefit "
                "from far more easy running than they think — intensity should be the exception, "
                "not the rule."
    },
    {
        "id": "hard-easy-alternation",
        "topic": "intensity_distribution",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 3, "max_days": 7,
        "text": "Never schedule two hard efforts (tempo, intervals, or a long run) back to back. "
                "Follow any hard day with at least one easy or rest day so the body can absorb "
                "the stress before the next quality session."
    },
    {
        "id": "mileage-progression-cap",
        "topic": "mileage_progression",
        "experience_levels": ["beginner", "intermediate"],
        "min_days": 1, "max_days": 7,
        "text": "When increasing weekly volume, avoid raising total mileage by more than about "
                "10% from one week to the next. Sudden jumps in volume are one of the most common "
                "drivers of overuse injury, especially for less experienced runners."
    },
    {
        "id": "maintenance-no-progression-needed",
        "topic": "mileage_progression",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 1, "max_days": 7,
        "text": "Maintenance mode is not a training block — weekly mileage does not need to "
                "increase over time. Holding volume steady week to week is not just acceptable, "
                "it's often the more sustainable choice when there's no race to build toward."
    },
    {
        "id": "long-run-scaling",
        "topic": "long_run_guidance",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 3, "max_days": 7,
        "text": "One weekly long run at an easy effort — typically 20-30% of total weekly volume — "
                "builds and maintains aerobic capacity without requiring race-specific structure. "
                "It doesn't need to grow week over week in maintenance mode; holding it steady is fine."
    },
    {
        "id": "long-run-optional-low-days",
        "topic": "long_run_guidance",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 1, "max_days": 2,
        "text": "With only one or two days available, a dedicated 'long run' is optional — "
                "consistency across the available days matters more than any single session's "
                "length. Keep both runs moderate rather than making one very long and one very short."
    },
    {
        "id": "recovery-day-cadence",
        "topic": "recovery_cadence",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 4, "max_days": 7,
        "text": "Include at least one full rest day per week regardless of experience level, and "
                "two or more for beginners or anyone training 6-7 days. Rest days are when aerobic "
                "adaptation actually happens, not just when training stops."
    },
    {
        "id": "recovery-week-checkin",
        "topic": "recovery_cadence",
        "experience_levels": ["intermediate", "advanced"],
        "min_days": 4, "max_days": 7,
        "text": "Even without a periodized plan, consider an easier week every 4-6 weeks — reduced "
                "volume and no hard efforts — to let the body fully recover before resuming normal "
                "maintenance training."
    },
    {
        "id": "injury-prevention-warning-signs",
        "topic": "injury_prevention",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 1, "max_days": 7,
        "text": "Sharp or localized pain (as opposed to general muscle fatigue) is a signal to skip "
                "or modify a workout, not push through it. Persistent pain across multiple sessions "
                "warrants a full rest day or two, not just easier running."
    },
    {
        "id": "injury-prevention-surface-variety",
        "topic": "injury_prevention",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 3, "max_days": 7,
        "text": "Where possible, vary running surfaces (road, trail, track) and avoid running the "
                "same route at the same effort every day — repetitive identical loading on the same "
                "joints and tissues is a known contributor to overuse injury."
    },
    {
        "id": "low-days-prioritization",
        "topic": "low_days_scaling",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 1, "max_days": 1,
        "text": "With only one day available per week, prioritize a moderate, sustainable effort "
                "over anything intense — the goal with a single weekly session is maintaining the "
                "habit and baseline aerobic fitness, not producing a hard training stimulus."
    },
    {
        "id": "low-days-two-day-split",
        "topic": "low_days_scaling",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 2, "max_days": 2,
        "text": "With two days available, one easy run and one slightly longer or moderately "
                "harder effort covers most of the aerobic benefit a maintenance runner needs — "
                "there's rarely a reason to make both days equally hard."
    },
    {
        "id": "workout-variety-not-progression",
        "topic": "workout_variety",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 3, "max_days": 7,
        "text": "Vary workout types (easy runs, one moderate tempo effort, occasional short "
                "intervals) for enjoyment and well-rounded fitness, but don't feel obligated to "
                "make each session harder than the last — variety, not progression, is the goal "
                "outside of a training block."
    },
    {
        "id": "cross-training-substitution",
        "topic": "workout_variety",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 3, "max_days": 7,
        "text": "Swapping one running day for low-impact cross-training (cycling, swimming, "
                "elliptical) at a similar effort level maintains aerobic fitness while reducing "
                "cumulative impact load on joints — a reasonable substitution once or twice a week."
    },
    {
        "id": "beginner-effort-over-pace",
        "topic": "beginner_guidance",
        "experience_levels": ["beginner"],
        "min_days": 1, "max_days": 7,
        "text": "For newer runners, train by perceived effort (able to hold a conversation on "
                "easy days) rather than fixed pace targets. Pace is highly variable day to day due "
                "to fatigue, weather, and terrain, but effort is a more reliable and less "
                "discouraging guide."
    },
    {
        "id": "beginner-walk-run-acceptable",
        "topic": "beginner_guidance",
        "experience_levels": ["beginner"],
        "min_days": 1, "max_days": 7,
        "text": "Walk-run intervals are a legitimate and effective way to build aerobic base for "
                "newer runners — there's no requirement to run continuously for a workout to count "
                "toward maintaining fitness."
    },
    {
        "id": "advanced-effort-ceiling",
        "topic": "advanced_guidance",
        "experience_levels": ["advanced"],
        "min_days": 5, "max_days": 7,
        "text": "Experienced runners maintaining fitness without a race goal should still cap hard "
                "efforts at 1-2 sessions per week — high weekly mileage alone doesn't require "
                "proportionally more intensity, and most of the aerobic benefit still comes from "
                "consistent easy volume."
    },
    {
        "id": "consistency-over-intensity",
        "topic": "general_philosophy",
        "experience_levels": ["beginner", "intermediate", "advanced"],
        "min_days": 1, "max_days": 7,
        "text": "For general fitness maintenance, showing up consistently week after week at a "
                "sustainable effort produces better long-term results than sporadic hard efforts "
                "followed by burnout or injury layoffs."
    },
]


def select_relevant_principles(experience_level: str, days_per_week: int, max_principles: int = 6) -> list[str]:
    """
    Filter corpus by experience level + days/week, then pick a topic-diverse subset.
    Returns rendered text strings ready for prompt injection.
    """
    matches = [
        p for p in PRINCIPLES
        if experience_level in p["experience_levels"]
        and p["min_days"] <= days_per_week <= p["max_days"]
    ]

    by_topic = {}
    for p in matches:
        by_topic.setdefault(p["topic"], []).append(p)

    selected = []
    topics = list(by_topic.keys())
    i = 0
    while len(selected) < max_principles and any(by_topic.values()):
        topic = topics[i % len(topics)]
        if by_topic[topic]:
            selected.append(by_topic[topic].pop(0))
        i += 1

    return [p["text"] for p in selected]
