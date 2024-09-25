from curl_cffi import requests
import json

class VehicleScoreConnector:
    def __init__(self):
        self.base_url = "https://vehiclescore.co.uk/_next/data/Ze-I3S0FoZSrff8HbIUwn/en/score.json"

    def fetch_data(self, registration):
        url = f"{self.base_url}?registration={registration}"
        response = requests.get(url)
        return response.json()

if __name__ == "__main__":
    connector = VehicleScoreConnector()

    # Test data
    test_registrations = ["fp64OOY", "SV08HVW"]

    for reg in test_registrations:
        print(f"\nFetching data for registration: {reg}")
        try:
            data = connector.fetch_data(reg)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error fetching data: {str(e)}")