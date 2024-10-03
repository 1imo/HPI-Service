from datetime import datetime, timedelta
import json
import logging
from CarGuide.index import get_car_details
from VehicleScore.index import get_vehicle_score
from Carly.index import get_carly_vehicle_history
from TotalCarCheck.index import get_total_car_check
from AutoTrader.index import get_autotrader_listings
from DVSA.index import get_mot_history
from Utils.database import Database
from AI.index import AI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VehicleDataInterface:
    def __init__(self, database):
        self.db = database
        self.ai = AI()
        logger.info("VehicleDataInterface initialized")

    def get_vehicle_data(self, vrm):
        logger.info(f"Processing VRM: {vrm}")
        existing_data = self.db.readReg(vrm)
        logger.info(f"Existing data for {vrm}: {json.dumps(existing_data)}")
        mot_history = get_mot_history(vrm)
        logger.info(f"MOT history for {vrm}: {json.dumps(mot_history)}")

        if existing_data:
            combined_data = {**existing_data, 'mot_history': mot_history}
            logger.info(f"Combined existing data for {vrm}: {json.dumps(combined_data)}")
        else:
            logger.info(f"No existing data found for {vrm}. Fetching new data.")
            vehicle_data = self._fetch_all_vehicle_data(vrm)
            logger.info(f"Fetched vehicle data for {vrm}: {json.dumps(vehicle_data)}")
            self.db.write(vrm, vehicle_data)
            logger.info(f"Wrote new data to DB for {vrm}")
            combined_data = {**vehicle_data, 'mot_history': mot_history}
            logger.info(f"Combined new data for {vrm}: {json.dumps(combined_data)}")

        ai_analysis = self._process_with_ai(combined_data)
        logger.info(f"AI analysis for {vrm}: {json.dumps(ai_analysis)}")

        return ai_analysis

    def _print_data_info(self, data, data_name):
        if isinstance(data, dict):
            logger.info(f"Number of key-value pairs in {data_name}: {len(data)}")
        else:
            logger.info(f"{data_name} is not a dict")

    def _fetch_all_vehicle_data(self, vrm):
        vehicle_data = {}

        logger.info(f"Calling get_car_details for {vrm}")
        car_details = get_car_details(vrm)
        if isinstance(car_details, dict):
            vehicle_data.update(car_details)
            logger.info(f"Car details for {vrm}: {json.dumps(car_details)}")
        else:
            logger.warning(f"get_car_details did not return a dict for {vrm}")

        logger.info(f"Calling get_vehicle_score for {vrm}")
        vehicle_score = get_vehicle_score(vrm)
        if isinstance(vehicle_score, dict):
            vehicle_data.update(vehicle_score)
            logger.info(f"Vehicle score for {vrm}: {json.dumps(vehicle_score)}")
        else:
            logger.warning(f"get_vehicle_score did not return a dict for {vrm}")

        logger.info(f"Calling get_carly_vehicle_history for {vrm}")
        carly_history = get_carly_vehicle_history(vrm)
        if isinstance(carly_history, dict):
            vehicle_data.update(carly_history)
            logger.info(f"Carly vehicle history for {vrm}: {json.dumps(carly_history)}")
        else:
            logger.warning(f"get_carly_vehicle_history did not return a dict for {vrm}")

        if 'vin' in vehicle_data:
            logger.info(f"Calling get_total_car_check for {vrm} with VIN: {vehicle_data['vin']}")
            total_car_check_data = get_total_car_check(vrm, vehicle_data['vin'])
            if isinstance(total_car_check_data, dict):
                vehicle_data.update(total_car_check_data)
                logger.info(f"Total car check data for {vrm}: {json.dumps(total_car_check_data)}")
            else:
                logger.warning(f"get_total_car_check did not return a dict for {vrm}")
        else:
            logger.warning(f"VIN not found for {vrm}, skipping get_total_car_check")

        # if 'make' in vehicle_data and 'model' in vehicle_data and 'year' in vehicle_data:
        #     logger.info(f"Calling get_autotrader_listings for {vrm}")
        #     autotrader_listings = get_autotrader_listings(vrm, vehicle_data['make'], vehicle_data['model'], vehicle_data['year'])
        #     if isinstance(autotrader_listings, dict):
        #         vehicle_data.update(autotrader_listings)
        #         logger.info(f"AutoTrader listings for {vrm}: {json.dumps(autotrader_listings)}")
        #     else:
        #         logger.warning(f"get_autotrader_listings did not return a dict for {vrm}")
        # else:
        #     logger.warning(f"Missing make, model, or year for {vrm}, skipping get_autotrader_listings")

        return vehicle_data
    
    def _process_with_ai(self, data):
        logger.info("Processing data with AI")
        res = self.ai.process_input(str(data))
        logger.info(f"AI processing complete. Result: {json.dumps(res)}")
        return res

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch vehicle data for a given registration number.")
    parser.add_argument("vrm", help="Vehicle Registration Number")
    args = parser.parse_args()

    logger.info(f"Starting vehicle data fetch for VRM: {args.vrm}")

    database = Database()
    interface = VehicleDataInterface(database)

    vehicle_data = interface.get_vehicle_data(args.vrm)
    
    logger.info(f"Vehicle Data Summary for {args.vrm}:")
    logger.info(json.dumps(vehicle_data['vehicle_data'], indent=2))
    
    logger.info("AI Analysis:")
    logger.info(vehicle_data['ai_analysis'])

    logger.info("Full data is stored in the database.")