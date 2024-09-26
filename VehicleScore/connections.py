from curl_cffi import requests
import json

class VehicleScoreConnector:
    def __init__(self):
        self.base_url = "https://vehiclescore.co.uk/_next/data/Yt2AEr4rfqBXon8I5o1d8/en/score.json"
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
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            "x-nextjs-data": "1"
        }
        self.cookies = {
            "cwr_s": "eyJzZXNzaW9uSWQiOiI5YjI0ZDY3ZC1iZDAzLTQyYmUtYjc2NC1iYjkyZTQzZDNhMTAiLCJyZWNvcmQiOnRydWUsImV2ZW50Q291bnQiOjksInBhZ2UiOnsicGFnZUlkIjoiLyIsInBhcmVudFBhZ2VJZCI6Ii9zY29yZSIsImludGVyYWN0aW9uIjoyLCJyZWZlcnJlciI6IiIsInJlZmVycmVyRG9tYWluIjoiIiwic3RhcnQiOjE3MjczNzk3NDU4Mzh9fQ==",
            "cwr_u": "78f2c137-0881-4d85-a048-8ed5a09fcd88",
            "userId": "66f299418fff4aa2d7166f36",
            # Add other cookies here
        }

    def fetch_data(self, registration):
        try:
            url = f"{self.base_url}?registration={registration}"
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request error for {registration}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {registration}: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error in fetch_data for {registration}: {str(e)}")
            return None

if __name__ == "__main__":
    try:
        connector = VehicleScoreConnector()

        # Test data
        test_registrations = ["fp64OOY", "SV08HVW"]

        for reg in test_registrations:
            print(f"\nFetching data for registration: {reg}")
            data = connector.fetch_data(reg)
            if data:
                print(json.dumps(data, indent=2))
            else:
                print(f"Failed to fetch data for {reg}")
    except Exception as e:
        print(f"An error occurred in the main execution: {str(e)}")