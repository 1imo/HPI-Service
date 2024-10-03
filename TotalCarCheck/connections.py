import os
from curl_cffi import requests
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path='../.env')

class TotalCarCheck:
    def __init__(self, vrm, vin):
        self.url = f"https://totalcarcheck.co.uk/CheckVin?vrm={vrm}&vin={vin}"
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.9",
            "Connection": "keep-alive",
            "Cookie": os.getenv('TCC_AUTH_COOKIE'),
            "Host": "totalcarcheck.co.uk",
            "Referer": "https://totalcarcheck.co.uk/VinCheck",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": os.getenv('USER_AGENT')
        }

    def check_vin(self):
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()

if __name__ == "__main__":
    vrm = os.getenv('TEST_VRM')
    vin = os.getenv('TEST_VIN')
    checker = TotalCarCheck(vrm, vin)
    response = checker.check_vin()
