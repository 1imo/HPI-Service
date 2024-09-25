import json
from CarGuide.index import get_car_details
from VehicleScore.index import get_vehicle_score
from Carly.index import get_carly_vehicle_history
from TotalCarCheck.index import get_total_car_check
from AutoTrader.index import get_autotrader_listings
from DVSA.index import get_mot_history
from Models.vehicle import VehicleDataModel, VehicleInfo, VehicleSpecifications, RegistrationInfo, VehicleStatus, VehicleScore, MarketData, ChassisSpecs, EngineSpecs, TransmissionSpecs, PerformanceSpecs, DimensionSpecs, FuelSpecs

class VehicleDataInterface:
    def __init__(self):
        pass

    def get_all_vehicle_data(self, vrm):
        # Initialize with basic info
        vehicle_data = VehicleDataModel(
            vehicle_info=VehicleInfo(registration=vrm, make="", model="", year=0, vin="", color="", series_description=None),
            specifications=VehicleSpecifications(
                engine=EngineSpecs(engine_size=0),
                transmission=TransmissionSpecs(),
                performance=PerformanceSpecs(),
                dimensions=DimensionSpecs(),
                chassis=ChassisSpecs(doors=0),
                fuel=FuelSpecs(fuel_type="")
            ),
            registration_info=RegistrationInfo(manufacture_date=None, first_registration_date=None, last_v5c_issue_date=None),
            vehicle_status=VehicleStatus(has_plate_changes=False, has_colour_changes=False, has_salvage_records=False, 
                                         has_mileage_anomaly=False, is_exported=False, is_possible_taxi=False, 
                                         is_stolen=False, has_outstanding_finance=False, has_been_written_off=False),
            score=VehicleScore(overall_score=0, age_score=0, mileage_score=0, mot_history_score=0, average_score=0),
            mot_history=[],
            market_data=MarketData(estimated_value=0.0, price_range=(0, 0), days_to_sell=0, similar_listings=0)
        )

        vehicle_data = get_car_details(vehicle_data)
        vehicle_data = get_vehicle_score(vehicle_data)
        vehicle_data = get_carly_vehicle_history(vehicle_data)
        vehicle_data = get_mot_history(vehicle_data)

        if vehicle_data.vehicle_info.vin:
            vehicle_data = get_total_car_check(vehicle_data)

        # if vehicle_data.vehicle_info.make and vehicle_data.vehicle_info.model and vehicle_data.vehicle_info.year:
        #     vehicle_data = get_autotrader_listings(vehicle_data)

        return vehicle_data

def main():
    interface = VehicleDataInterface()
    
    vrm = input("Enter the vehicle registration number: ")

    vehicle_data = interface.get_all_vehicle_data(vrm)
    
    # Write the data to a JSON file
    output_filename = f"{vrm}_vehicle_data.json"
    with open(output_filename, 'w') as json_file:
        json.dump(vehicle_data.__dict__, json_file, indent=2, default=str)
    
    print(f"Vehicle data has been saved to {output_filename}")

if __name__ == "__main__":
    main()
