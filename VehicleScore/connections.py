from curl_cffi import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class VehicleScoreConnector:
    def __init__(self):
        self.base_url = os.getenv('VEHICLE_SCORE_BASE_URL')
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "vehiclescore.co.uk",
            "Referer": "https://vehiclescore.co.uk/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": os.getenv('VEHICLE_SCORE_USER_AGENT'),
            "x-nextjs-data": "1"
        }
        self.cookies = {
            "cwr_s": os.getenv('VEHICLE_SCORE_CWR_S'),
            "cwr_u": os.getenv('VEHICLE_SCORE_CWR_U'),
            "userId": os.getenv('VEHICLE_SCORE_USER_ID'),
        }

    def fetch_data(self, registration):
        url = f"{self.base_url}?registration={registration}"
        response = requests.get(url, headers=self.headers, cookies=self.cookies)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    connector = VehicleScoreConnector()

    # Test data
    test_registrations = ["fp64OOY", "SV08HVW"]

    for reg in test_registrations:
        data = connector.fetch_data(reg)