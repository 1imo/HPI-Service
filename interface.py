from datetime import datetime, timedelta
import json
from CarGuide.index import get_car_details
from VehicleScore.index import get_vehicle_score
from Carly.index import get_carly_vehicle_history
from TotalCarCheck.index import get_total_car_check
from AutoTrader.index import get_autotrader_listings
from DVSA.index import get_mot_history
from Utils.database import Database

class VehicleDataInterface:
    def __init__(self, database):
        self.db = database

    def get_vehicle_data(self, vrm):
        existing_data = self.db.readReg(vrm)

        if existing_data:
            last_updated = datetime.fromisoformat(existing_data['updated_at'])
            if datetime.now() - last_updated < timedelta(days=1):
                return existing_data

        # Fetch new data
        vehicle_data = self._fetch_all_vehicle_data(vrm)
        
        # Write new data to the database
        self.db.write(vrm, vehicle_data)

        return vehicle_data

    def _fetch_all_vehicle_data(self, vrm):
        vehicle_data = {}

        print("Calling get_car_details")
        vehicle_data.update(get_car_details(vrm))
        print("Calling get_vehicle_score")
        vehicle_data.update(get_vehicle_score(vrm))
        print("Calling get_carly_vehicle_history")
        vehicle_data.update(get_carly_vehicle_history(vrm))

        if 'vin' in vehicle_data:
            print("Calling get_total_car_check")
            vehicle_data.update(get_total_car_check(vrm, vehicle_data['vin']))

        # Uncomment the following lines if you want to include AutoTrader listings
        # if 'make' in vehicle_data and 'model' in vehicle_data and 'year' in vehicle_data:
        #     vehicle_data.update(get_autotrader_listings(vrm, vehicle_data['make'], vehicle_data['model'], vehicle_data['year']))

        return vehicle_data
    

if __name__ == "__main__":
    database = Database()
    interface = VehicleDataInterface(database)
    
    vrm = input("Enter the vehicle registration number: ")

    vehicle_data = interface.get_vehicle_data(vrm)
    
    # Print a summary of the vehicle data
    print(f"\nVehicle Data Summary for {vrm}:")
    print(json.dumps(vehicle_data, indent=2))

    mot_history = get_mot_history(vrm)

    
    print("\nFull data is stored in the database.")
