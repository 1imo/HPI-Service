import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class MOTHistoryRetriever:
    def __init__(self):
        # API credentials and endpoints
        self.client_id = os.getenv('DVSA_CLIENT_ID')
        self.client_secret = os.getenv('DVSA_CLIENT_SECRET')
        self.api_key = os.getenv('DVSA_API_KEY')
        self.token_url = os.getenv('DVSA_TOKEN_URL')
        self.api_base_url = os.getenv('DVSA_API_BASE_URL')

    def get_access_token(self):
        # Request an access token using client credentials
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://tapi.dvsa.gov.uk/.default'
        }
        response = requests.post(self.token_url, data=token_data)
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    
    def fetch_mot_history(self, registration):
        # Fetch MOT history for a given vehicle registration
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to obtain access token."}

        url = f"{self.api_base_url}/v1/trade/vehicles/registration/{registration}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data. Status code: {response.status_code}"}

    def process_mot_history(self, data):
        # Process the raw MOT history data into a more usable format
        if "error" in data:
            return data

        vehicle_data = data[0] if isinstance(data, list) and len(data) > 0 else data
        mot_tests = vehicle_data.get("motTests", [])

        return {'motTests': mot_tests}

    
if __name__ == "__main__":
    # Example usage of the MOTHistoryRetriever
    retriever = MOTHistoryRetriever()
    registration_plate = "PN12BWU"
    mot_history = retriever.fetch_mot_history(registration_plate)
    processed_history = retriever.process_mot_history(mot_history)
    print(json.dumps(processed_history, indent=2))