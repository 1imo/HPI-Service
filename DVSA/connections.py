import requests
import json
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../.env')
class MOTHistoryRetriever:
    def __init__(self):
        
        # API credentials and endpoints
        self.client_id = os.getenv('DVSA_CLIENT_ID')
        self.client_secret = os.getenv('DVSA_CLIENT_SECRET')
        self.api_key = os.getenv('DVSA_API_KEY')
        self.token_url = os.getenv('DVSA_TOKEN_URL')
        self.api_base_url = os.getenv('DVSA_API_BASE_URL')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

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
            self.logger.debug(f"Raw API response: {response.text}")
            return response.json()
        else:
            return {"error": f"Failed to fetch data. Status code: {response.status_code}"}

    def process_mot_history(self, data):
        # Process the raw MOT history data into a more usable format
        if "error" in data:
            return data

        self.logger.debug(f"Processing MOT history data: {json.dumps(data, indent=2)}")
        vehicle_data = data[0] if isinstance(data, list) and len(data) > 0 else data
        mot_tests = vehicle_data.get("motTests", [])
        
        processed_history = []
        for test in mot_tests:
            test_result = test.get("testResult", "").upper()
            color = self.get_result_color(test_result)
            
            processed_test = {
                "testDate": self.parse_date(test.get("completedDate", "")),
                "testResult": test_result,
                "color": color,
                "mileage": test.get("odometerValue", "N/A"),
                "expiryDate": self.parse_date(test.get("expiryDate", "")),
                "defects": []
            }
            
            # Process defects and RFR (Reason for Rejection) items
            for defect in test.get("defects", []):
                processed_defect = {
                    "type": "DANGEROUS" if defect.get("dangerous") else defect.get("type", "").upper(),
                    "text": defect.get("text", ""),
                    "dangerous": defect.get("dangerous", False)
                }
                processed_test["defects"].append(processed_defect)
            
            for rfr in test.get("rfrAndComments", []):
                processed_defect = {
                    "type": rfr.get("type", "").upper(),
                    "text": rfr.get("text", ""),
                    "dangerous": False
                }
                processed_test["defects"].append(processed_defect)
            
            processed_history.append(processed_test)

        self.logger.debug(f"Processed MOT history: {json.dumps(processed_history, indent=2)}")
        return processed_history

    def parse_date(self, date_string):
        # Parse various date formats and return a standardized format
        if not date_string:
            return "N/A"
        
        self.logger.debug(f"Parsing date: {date_string}")
        
        date_formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format
            "%Y.%m.%d %H:%M:%S",      # Original format
            "%d/%m/%Y",               # New observed format
            "%Y-%m-%d",               # YYYY-MM-DD format
            "%d/%m/%Y %H:%M:%S",      # Another possible format
        ]

        for date_format in date_formats:
            try:
                dt = datetime.strptime(date_string, date_format)
                formatted_date = dt.strftime("%d/%m/%Y")
                self.logger.debug(f"Successfully parsed date {date_string} with format {date_format}. Result: {formatted_date}")
                return formatted_date
            except ValueError:
                self.logger.debug(f"Failed to parse date {date_string} with format {date_format}")
                continue

        self.logger.warning(f"Unable to parse date: {date_string}. Returning original string.")
        return date_string

    def get_result_color(self, result):
        # Return a color code based on the test result
        if result == "PASSED":
            return 0x00FF00  # Green
        elif result == "FAILED":
            return 0xFF0000  # Red
        else:
            return 0xFFFFFF  # White (default)

    def get_rfr_color(self, rfr_type):
        # Return a color code based on the RFR (Reason for Rejection) type
        if rfr_type == "FAIL":
            return 0xFF0000  # Red
        elif rfr_type == "ADVISORY":
            return 0xFFA500  # Orange
        elif rfr_type == "MINOR":
            return 0xFFFF00  # Yellow
        else:
            return 0xFFFFFF  # White (default)

if __name__ == "__main__":
    # Example usage of the MOTHistoryRetriever
    retriever = MOTHistoryRetriever()
    registration_plate = "AK03 EWW"
    mot_history = retriever.fetch_mot_history(registration_plate)
    processed_history = retriever.process_mot_history(mot_history)
    print(json.dumps(processed_history, indent=2))