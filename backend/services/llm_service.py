import os
import json
from datetime import datetime

# Tier → provider → model ID
MODEL_TIERS = {
    'super_admin': {
        'gemini':    'gemini-2.5-pro',
        'openai':    'gpt-4o',
        'anthropic': 'claude-opus-4-6',
    },
    'admin': {
        'gemini':    'gemini-2.5-flash',
        'openai':    'gpt-4o',
        'anthropic': 'claude-sonnet-4-6',
    },
    'beta_tester': {
        'gemini':    'gemini-2.5-flash-lite',
        'openai':    'gpt-4o-mini',
        'anthropic': 'claude-haiku-4-5-20251001',
    },
}

# Tier rank for access checks (higher = more access)
TIER_RANK = {'super_admin': 3, 'admin': 2, 'beta_tester': 1}

# Full model catalog — shown in the UI model selector
ALL_MODELS = [
    {'id': 'gemini-2.5-pro',            'label': 'Gemini 2.5 Pro',       'provider': 'gemini',    'tier': 'super_admin'},
    {'id': 'gemini-2.5-flash',          'label': 'Gemini 2.5 Flash',     'provider': 'gemini',    'tier': 'admin'},
    {'id': 'gemini-2.5-flash-lite',     'label': 'Gemini 2.5 Flash Lite','provider': 'gemini',    'tier': 'beta_tester'},
    {'id': 'claude-opus-4-6',           'label': 'Claude Opus 4.6',      'provider': 'anthropic', 'tier': 'super_admin'},
    {'id': 'claude-sonnet-4-6',         'label': 'Claude Sonnet 4.6',    'provider': 'anthropic', 'tier': 'admin'},
    {'id': 'claude-haiku-4-5-20251001', 'label': 'Claude Haiku 4.5',     'provider': 'anthropic', 'tier': 'beta_tester'},
    {'id': 'gpt-4o',                    'label': 'GPT-4o',               'provider': 'openai',    'tier': 'admin'},
    {'id': 'gpt-4o-mini',               'label': 'GPT-4o Mini',          'provider': 'openai',    'tier': 'beta_tester'},
]

# model_id → provider for dispatch routing
MODEL_PROVIDER_MAP = {m['id']: m['provider'] for m in ALL_MODELS}


class LLMService:
    def __init__(self):
        # Primary provider (used when no specific model is requested)
        self.provider = os.getenv('LLM_PROVIDER', 'gemini').lower()

        # Initialize all providers that have API keys present
        self._init_gemini()
        self._init_openai()
        self._init_anthropic()

        # Verify primary provider is usable
        if not self._is_provider_available(self.provider):
            raise ValueError(
                f"Primary provider '{self.provider}' is not configured. "
                f"Set the matching API key (GEMINI_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY)."
            )

    # ------------------------------------------------------------------
    # Provider initialisation (each is a no-op if the key is absent)
    # ------------------------------------------------------------------

    def _init_gemini(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return
        try:
            import google.generativeai as genai
        except ImportError:
            if self.provider == 'gemini':
                raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
            return
        genai.configure(api_key=api_key)
        self.genai = genai
        self._default_gemini_model = os.getenv('GEMINI_MODEL', MODEL_TIERS['beta_tester']['gemini'])

    def _init_openai(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return
        try:
            from openai import OpenAI
        except ImportError:
            if self.provider == 'openai':
                raise ImportError("openai not installed. Run: pip install openai")
            return
        self.openai_client = OpenAI(api_key=api_key)
        self._default_openai_model = MODEL_TIERS['beta_tester']['openai']

    def _init_anthropic(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return
        try:
            import anthropic
        except ImportError:
            if self.provider == 'anthropic':
                raise ImportError("anthropic not installed. Run: pip install anthropic")
            return
        self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        self._default_anthropic_model = MODEL_TIERS['beta_tester']['anthropic']

    def _is_provider_available(self, provider: str) -> bool:
        if provider == 'gemini':    return hasattr(self, 'genai')
        if provider == 'openai':    return hasattr(self, 'openai_client')
        if provider == 'anthropic': return hasattr(self, 'anthropic_client')
        return False

    # ------------------------------------------------------------------
    # Tier / model helpers
    # ------------------------------------------------------------------

    def _model_for_role(self, user_role: str, preferred_model: str = None) -> str:
        """Return the model ID for the given role, honoring preferred_model if accessible."""
        role = user_role if user_role in MODEL_TIERS else 'beta_tester'
        if preferred_model:
            model_entry = next((m for m in ALL_MODELS if m['id'] == preferred_model), None)
            if model_entry:
                user_rank = TIER_RANK.get(role, TIER_RANK['beta_tester'])
                model_rank = TIER_RANK.get(model_entry['tier'], 1)
                if user_rank >= model_rank and self._is_provider_available(model_entry['provider']):
                    return preferred_model
        return MODEL_TIERS[role].get(self.provider, MODEL_TIERS['beta_tester'][self.provider])

    def get_active_model_name(self, user_role: str = None) -> str:
        return self._model_for_role(user_role or 'beta_tester')

    @staticmethod
    def get_models_for_role(user_role: str, provider: str = None) -> list:
        """Return all catalog models with an `available` flag for the given role."""
        user_rank = TIER_RANK.get(user_role, TIER_RANK['beta_tester'])
        result = []
        for model in ALL_MODELS:
            if provider and model['provider'] != provider:
                continue
            model_rank = TIER_RANK.get(model['tier'], 1)
            result.append({**model, 'available': user_rank >= model_rank})
        return result

    # ------------------------------------------------------------------
    # Dispatch — routes to the correct provider API based on model ID
    # ------------------------------------------------------------------

    def _dispatch(self, prompt: str, model_id: str) -> dict:
        provider = MODEL_PROVIDER_MAP.get(model_id, self.provider)
        if provider == 'gemini':
            if not self._is_provider_available('gemini'):
                raise ValueError("Gemini not configured — set GEMINI_API_KEY")
            return self._generate_with_gemini(prompt, model_id)
        if provider == 'openai':
            if not self._is_provider_available('openai'):
                raise ValueError("OpenAI not configured — set OPENAI_API_KEY")
            return self._generate_with_openai(prompt, model_id)
        if provider == 'anthropic':
            if not self._is_provider_available('anthropic'):
                raise ValueError("Anthropic not configured — set ANTHROPIC_API_KEY")
            return self._generate_with_anthropic(prompt, model_id)
        raise ValueError(f"Unknown provider for model '{model_id}'")

    # ------------------------------------------------------------------
    # Provider-specific generation
    # ------------------------------------------------------------------

    def _generate_with_gemini(self, prompt: str, model_name: str = None) -> dict:
        use_model = model_name or self._default_gemini_model
        full_prompt = "You are an expert running coach. Always respond with valid JSON only.\n\n" + prompt
        model = self.genai.GenerativeModel(use_model)
        try:
            response = model.generate_content(
                full_prompt,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
        except Exception as e:
            if any(s in str(e).lower() for s in ("response_mime_type", "not supported", "not found")):
                response = model.generate_content(
                    full_prompt,
                    generation_config=self.genai.types.GenerationConfig(temperature=0.7)
                )
            else:
                raise

        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"):     text = text[3:]
        if text.endswith("```"):       text = text[:-3]
        return json.loads(text.strip())

    def _generate_with_openai(self, prompt: str, model_name: str = None) -> dict:
        use_model = model_name or self._default_openai_model
        response = self.openai_client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": "You are an expert running coach. Always respond with valid JSON only."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _generate_with_anthropic(self, prompt: str, model_name: str = None) -> dict:
        use_model = model_name or self._default_anthropic_model
        response = self.anthropic_client.messages.create(
            model=use_model,
            max_tokens=8096,
            system="You are an expert running coach. Always respond with valid JSON only.",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"):     text = text[3:]
        if text.endswith("```"):       text = text[:-3]
        return json.loads(text.strip())

    # ------------------------------------------------------------------
    # Public generation methods
    # ------------------------------------------------------------------

    def generate_workout_plan(self, user_request: str, user_role: str = None, preferred_model: str = None) -> dict:
        """Generate a structured workout plan. Returns a workout plan dict."""
        prompt = f"""You are an expert running coach. Create a detailed, structured workout plan based on this request: {user_request}

Please provide a workout plan in the following JSON format:
{{
    "goal": "description of the goal",
    "duration_weeks": number of weeks,
    "workouts": [
        {{
            "week": week number (1-based),
            "day": day of week (1-7, where 1 is Monday),
            "type": "long_run" | "tempo" | "intervals" | "easy_run" | "rest" | "cross_training",
            "distance_km": distance in kilometers (null for rest/cross_training),
            "duration_minutes": duration in minutes (null if distance is specified),
            "pace": "target pace description (e.g., 'easy pace', '5:00/km', 'marathon pace')",
            "notes": "detailed instructions and tips for this workout"
        }}
    ]
}}

Make the plan realistic, progressive, and tailored to the user's goal. Include proper rest days and build up gradually."""

        model_id = self._model_for_role(user_role, preferred_model)
        try:
            plan_json = self._dispatch(prompt, model_id)
            plan_json['created_at'] = datetime.now().isoformat()
            plan_json['user_request'] = user_request
            plan_json['provider'] = MODEL_PROVIDER_MAP.get(model_id, self.provider)
            plan_json['model'] = model_id
            return plan_json
        except Exception as e:
            raise Exception(f"Failed to generate workout plan: {str(e)}")

    def generate_periodized_workouts(
        self,
        event_distance: str,
        phase_name: str,
        phase_focus: str,
        week_numbers: list,
        total_weeks: int,
        experience_level: str = "intermediate",
        user_role: str = None,
        preferred_model: str = None
    ) -> list:
        """
        Generate workouts for a single phase of a periodized training plan.

        Returns list of workout dicts: week, day, type, distance_km, duration_minutes, pace, notes
        """
        weeks_str = ", ".join(str(w) for w in week_numbers)
        num_weeks = len(week_numbers)

        prompt = f"""You are an expert running coach creating a periodized {event_distance} training plan.

This is the **{phase_name}** phase (weeks {weeks_str} of {total_weeks} total weeks).
Runner experience level: {experience_level}

Phase focus: {phase_focus}

Generate workouts for each day of each week in this phase. Return a JSON object with a "workouts" array.

Each workout should have:
- "week": week number ({weeks_str})
- "day": day of week (1=Monday through 7=Sunday)
- "type": one of "long_run", "tempo", "intervals", "easy_run", "rest", "cross_training"
- "distance_km": distance in km (null for rest/cross_training)
- "duration_minutes": duration in minutes (null if distance given, required for cross_training)
- "pace": target pace description (e.g., "easy pace", "5:00/km", "marathon pace", null for rest)
- "notes": brief coaching notes for the workout

Rules:
- EXACTLY ONE workout per day, 7 workouts per week (no more, no less)
- Do NOT assign multiple workouts to the same day
- Include 7 days per week (include rest days as type "rest")
- Rest days should have no distance, no duration, and notes like "Full rest day"
- Long runs on weekends (day 6 or 7)
- {num_weeks} weeks total in this phase
- Progressive overload within the phase
- For {experience_level} runners training for {event_distance}

Return ONLY a JSON object: {{"workouts": [...]}}"""

        model_id = self._model_for_role(user_role, preferred_model)
        try:
            result = self._dispatch(prompt, model_id)
            if isinstance(result, dict) and "workouts" in result:
                return result["workouts"]
            if isinstance(result, list):
                return result
            raise ValueError("Unexpected LLM response format: expected 'workouts' array")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON for {phase_name} phase: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate {phase_name} phase workouts: {str(e)}")
