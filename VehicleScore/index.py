from .connections import VehicleScoreConnector
from datetime import datetime

def get_vehicle_score(vehicle_data):
    score_api = VehicleScoreConnector()
    api_response = score_api.fetch_data(vehicle_data.vehicle_info.registration)

    print("VEHICLE DATA", vehicle_data)
    
    page_props = api_response.get('pageProps', {})
    print(page_props)
    brand_new_scores = page_props.get('brandNewScores', {})
    scores = page_props.get('scores', {})
    vehicle_info = page_props.get('vehicle', {})
    specs = vehicle_info.get('specs', {})

    # Update VehicleScore
    vehicle_data.score.overall_score = brand_new_scores.get('score')
    vehicle_data.score.age_score = brand_new_scores.get('age')
    vehicle_data.score.mileage_score = brand_new_scores.get('mileage')
    vehicle_data.score.mot_history_score = brand_new_scores.get('motHistory')
    vehicle_data.score.average_score = scores.get('averageScore')

    # Update VehicleInfo
    vehicle_data.vehicle_info.year = int(vehicle_info.get('year', 0))
    vehicle_data.vehicle_info.price = specs.get('price')

    # Update RegistrationInfo
    vehicle_data.registration_info.mot_due_date = parse_date(vehicle_info.get('mot', {}).get('motExpiryDate'), "%Y-%m-%d")
    vehicle_data.registration_info.tax_due_date = parse_date(vehicle_info.get('tax', {}).get('taxDueDate'), "%Y-%m-%d")

    # Update VehicleStatus
    vehicle_data.vehicle_status.type_approval_category = specs.get('typeApproval')
    vehicle_data.vehicle_status.co2_emissions = specs.get('co2Emissions')
    vehicle_data.vehicle_status.average_miles_per_year = float(vehicle_info.get('averageMilesPy', 0))
    vehicle_data.vehicle_status.mot_valid = vehicle_info.get('mot', {}).get('motStatus') == 'Valid'
    vehicle_data.vehicle_status.tax_valid = vehicle_info.get('tax', {}).get('taxStatus') != 'Untaxed'


    return vehicle_data

def parse_date(date_string, format_string):
    if date_string:
        try:
            return datetime.strptime(date_string, format_string).year
        except ValueError:
            return None
    return None

__all__ = ['get_vehicle_score']
