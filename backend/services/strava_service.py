import os
import requests
from urllib.parse import urlencode

class StravaService:
    def __init__(self):
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.redirect_uri = os.getenv('STRAVA_REDIRECT_URI', 'http://localhost:5000/api/strava/callback')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Strava API credentials not found in environment variables")
        
        self.base_url = 'https://www.strava.com'
        self.api_url = 'https://www.strava.com/api/v3'
    
    def get_authorization_url(self):
        """Generate Strava OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'activity:read_all',
            'approval_prompt': 'force'
        }
        
        auth_url = f"{self.base_url}/oauth/authorize?{urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        url = f"{self.base_url}/oauth/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data.get('access_token')
    
    def get_activities(self, access_token, per_page=30):
        """
        Fetch user activities from Strava.
        Returns a list of activity dictionaries.
        """
        url = f"{self.api_url}/athlete/activities"
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        params = {
            'per_page': per_page
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        activities = response.json()
        
        # Transform to our format
        formatted_activities = []
        for activity in activities:
            formatted_activity = {
                'id': str(activity.get('id')),
                'name': activity.get('name', 'Untitled'),
                'type': activity.get('type', 'Run'),
                'distance': activity.get('distance', 0) / 1000,  # Convert meters to km
                'moving_time': activity.get('moving_time', 0) / 60,  # Convert seconds to minutes
                'elapsed_time': activity.get('elapsed_time', 0) / 60,  # Convert seconds to minutes
                'start_date': activity.get('start_date_local', ''),
                'average_speed': activity.get('average_speed', 0) * 3.6,  # Convert m/s to km/h
                'average_heartrate': activity.get('average_heartrate'),
                'strava_id': str(activity.get('id'))
            }
            formatted_activities.append(formatted_activity)
        
        return formatted_activities

