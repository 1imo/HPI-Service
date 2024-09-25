from .connections import CarLookup
from datetime import datetime, timezone
from Models.vehicle import VehicleStatus, EngineSpecs, TransmissionSpecs, PerformanceSpecs, DimensionSpecs, ChassisSpecs, FuelSpecs, RegistrationInfo

def get_car_details(vehicle_data):
    car_lookup = CarLookup(vehicle_data.vehicle_info.registration)
    car_details = car_lookup.get_car_details()
    
    # Update VehicleInfo
    basic_details = car_details.get("basicDetails", {})
    vehicle_data.vehicle_info.make = basic_details.get("make")
    vehicle_data.vehicle_info.model = basic_details.get("model")

    # Update EngineSpecs
    if not vehicle_data.specifications.engine:
        vehicle_data.specifications.engine = EngineSpecs()
    vehicle_data.specifications.fuel.fuel_type = basic_details.get("fuelType")
    vehicle_data.specifications.engine.engine_size = basic_details.get("engineSize")

    # Update ChassisSpecs
    if not vehicle_data.specifications.chassis:
        vehicle_data.specifications.chassis = ChassisSpecs()
    vehicle_data.specifications.chassis.doors = basic_details.get("doors")

    # Update VehicleStatus
    if not vehicle_data.vehicle_status:
        vehicle_data.vehicle_status = VehicleStatus()
    vehicle_data.vehicle_info.color = basic_details.get("colour")
    vehicle_data.vehicle_status.mileage = basic_details.get("mileage")
    
    # Convert timestamps to datetime objects
    manufacture_date = datetime.fromtimestamp(basic_details.get("manufactureDate", 0), tz=timezone.utc)
    mot_due_date = datetime.fromtimestamp(basic_details.get("motDueDate", 0), tz=timezone.utc)
    last_v5c_issue_date = datetime.fromtimestamp(basic_details.get("lastV5CIssueDate", 0), tz=timezone.utc)

    # Update RegistrationInfo
    if not vehicle_data.registration_info:
        vehicle_data.registration_info = RegistrationInfo()
    vehicle_data.registration_info.manufacture_date = manufacture_date
    vehicle_data.registration_info.mot_due_date = mot_due_date
    vehicle_data.registration_info.last_v5c_issue_date = last_v5c_issue_date

    # Update mot_valid attribute
    current_date = datetime.now(timezone.utc)
    vehicle_data.vehicle_status.mot_valid = mot_due_date > current_date

    # Update Provenance information
    provenance = car_details.get("provenance", {})
    vehicle_data.vehicle_status.has_plate_changes = provenance.get("hasPlateChanges")
    vehicle_data.vehicle_status.has_color_changes = provenance.get("hasColourChanges")
    vehicle_data.vehicle_status.has_salvage_records = provenance.get("hasSalvageRecords")
    vehicle_data.vehicle_status.has_mileage_anomaly = provenance.get("hasMileageAnomaly")
    vehicle_data.vehicle_status.is_exported = provenance.get("isExported")
    vehicle_data.vehicle_status.is_possible_taxi = provenance.get("isPossibleTaxi")

    return vehicle_data

# Make sure to export the function
__all__ = ['get_car_details']
