import os
import json
from datetime import datetime
from openai import OpenAI

class LLMService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Using mini for cost efficiency, can upgrade to gpt-4
    
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert running coach. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            plan_json = json.loads(response.choices[0].message.content)
            
            # Add metadata
            plan_json['created_at'] = datetime.now().isoformat()
            plan_json['user_request'] = user_request
            
            return plan_json
        
        except Exception as e:
            raise Exception(f"Failed to generate workout plan: {str(e)}")

