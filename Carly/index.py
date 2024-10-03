from .connections import CarlyVehicleHistory as CarlyAPI
from Utils.utils import flatten_dict
from Utils.logging import logger

def get_carly_vehicle_history(vrm):
    try:
        carly_api = CarlyAPI()
        carly_data = carly_api.get_vehicle_history(vrm)
        carly_data = carly_api.extract_vehicle_info(carly_data, vrm)
        
        # Flatten the carly_data dictionary
        flattened_data = flatten_dict(carly_data)
        
        return flattened_data
    except Exception as e:
        logger.write(f"Error in get_carly_vehicle_history for VRM {vrm}: {str(e)}", is_exception=True)
        

__all__ = ['get_carly_vehicle_history']