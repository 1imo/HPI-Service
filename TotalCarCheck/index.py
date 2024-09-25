from .connections import TotalCarCheck as TotalCarCheckAPI

def get_total_car_check(vehicle_data):
    tcc_api = TotalCarCheckAPI(vehicle_data.vehicle_info.registration, vehicle_data.vehicle_info.vin)
    tcc_data = tcc_api.check_vin()
    
    # Update vehicle status
    vehicle_data.vehicle_status.has_plate_changes = tcc_data.get("plate_changes", False)
    vehicle_data.vehicle_status.has_colour_changes = tcc_data.get("colour_changes", False)
    vehicle_data.vehicle_status.has_salvage_records = tcc_data.get("salvage_records", False)
    vehicle_data.vehicle_status.is_exported = tcc_data.get("exported", False)
    vehicle_data.vehicle_status.is_stolen = tcc_data.get("stolen", False)
    vehicle_data.vehicle_status.has_outstanding_finance = tcc_data.get("outstanding_finance", False)
    
    # Update other relevant fields
    vehicle_data.vehicle_status.type_approval_category = tcc_data.get("type_approval_category")
    vehicle_data.vehicle_status.euro_status = tcc_data.get("euro_status")
    vehicle_data.vehicle_status.previous_owners = tcc_data.get("previous_owners")

    return vehicle_data

__all__ = ['get_total_car_check']
