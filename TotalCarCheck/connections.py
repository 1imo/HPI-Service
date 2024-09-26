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
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            print('URL', self.url)
            print('TCC AUTH COOKIE', os.getenv('TCC_AUTH_COOKIE'))
            print('User Agent', os.getenv('USER_AGENT'))
            print('RESPONSE', response.text)
            return response.json()
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None
        except ValueError as e:  # includes JSONDecodeError
            print(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error in check_vin: {str(e)}")
            return None

if __name__ == "__main__":
    try:
        vrm = os.getenv('TEST_VRM')
        vin = os.getenv('TEST_VIN')
        checker = TotalCarCheck(vrm, vin)
        response = checker.check_vin()
        if response:
            print(f"Response Body: {response}")
        else:
            print("Failed to get car check information.")
    except Exception as e:
        print(f"An error occurred in the main execution: {str(e)}")
