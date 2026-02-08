import os
import json
from datetime import datetime

class LLMService:
    def __init__(self):
        # Get provider preference (default to 'gemini')
        self.provider = os.getenv('LLM_PROVIDER', 'gemini').lower()
        
        if self.provider == 'gemini':
            self._init_gemini()
        elif self.provider == 'openai':
            self._init_openai()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Use 'gemini' or 'openai'")
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Model names: 'gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-2.5-flash-lite'
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite')
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            # Fallback to gemini-pro if the specified model fails
            if model_name != 'gemini-pro':
                print(f"Warning: Model {model_name} not available, falling back to gemini-pro")
                self.model = genai.GenerativeModel('gemini-pro')
            else:
                raise
        self.genai = genai
    
    def _init_openai(self):
        """Initialize OpenAI"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = "gpt-4o-mini"  # Using mini for cost efficiency
    
    def generate_workout_plan(self, user_request):
        """
        Generate a structured workout plan based on user request.
        Returns a structured workout plan dictionary.
        """
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

        try:
            if self.provider == 'gemini':
                plan_json = self._generate_with_gemini(prompt)
            elif self.provider == 'openai':
                plan_json = self._generate_with_openai(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Add metadata
            plan_json['created_at'] = datetime.now().isoformat()
            plan_json['user_request'] = user_request
            plan_json['provider'] = self.provider  # Track which provider was used
            
            return plan_json
        
        except Exception as e:
            raise Exception(f"Failed to generate workout plan: {str(e)}")
    
    def _generate_with_gemini(self, prompt):
        """Generate workout plan using Google Gemini"""
        # Gemini uses a different prompt format - combine system and user messages
        full_prompt = f"""You are an expert running coach. Always respond with valid JSON only.

{prompt}"""

        try:
            # Try with JSON response format first (for newer models)
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
        except Exception as e:
            # Fallback if response_mime_type is not supported (older models like gemini-pro)
            if "response_mime_type" in str(e).lower() or "not supported" in str(e).lower() or "not found" in str(e).lower():
                # Try without response_mime_type constraint
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=self.genai.types.GenerationConfig(
                        temperature=0.7
                    )
                )
            else:
                raise
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Sometimes Gemini wraps JSON in markdown code blocks, extract if needed
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]   # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()
        
        return json.loads(response_text)
    
    def _generate_with_openai(self, prompt):
        """Generate workout plan using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are an expert running coach. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        # Parse the JSON response
        return json.loads(response.choices[0].message.content)

    def generate_periodized_workouts(
        self,
        event_distance,
        phase_name,
        phase_focus,
        week_numbers,
        total_weeks,
        experience_level="intermediate"
    ):
        """
        Generate workouts for a single phase of a periodized training plan.

        Args:
            event_distance: Race distance (e.g., "marathon", "half", "10k", "5k")
            phase_name: Phase name ("base", "build", "peak", "taper")
            phase_focus: Description of what this phase focuses on
            week_numbers: List of week numbers in this phase (e.g., [1, 2, 3, 4])
            total_weeks: Total weeks in the full training block
            experience_level: "beginner", "intermediate", or "advanced"

        Returns:
            List of workout dicts with: week, day, type, distance_km, duration_minutes, pace, notes
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

        try:
            if self.provider == 'gemini':
                result = self._generate_with_gemini(prompt)
            elif self.provider == 'openai':
                result = self._generate_with_openai(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            # Extract workouts array from response
            if isinstance(result, dict) and "workouts" in result:
                return result["workouts"]
            elif isinstance(result, list):
                return result
            else:
                raise ValueError(f"Unexpected LLM response format: expected 'workouts' array")

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON for {phase_name} phase: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate {phase_name} phase workouts: {str(e)}")

