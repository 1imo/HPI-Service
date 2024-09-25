from .connections import CarlyVehicleHistory as CarlyAPI
from datetime import datetime
import json
import os

def get_carly_vehicle_history(vehicle_data):
    carly_api = CarlyAPI()
    carly_data = carly_api.get_vehicle_history(vehicle_data.vehicle_info.registration)
    carly_data = carly_api.extract_vehicle_info(carly_data, vehicle_data.vehicle_info.registration)
    
    # Update VehicleInfo
    vehicle_data.vehicle_info.make = carly_data.get("brandName", vehicle_data.vehicle_info.make)
    vehicle_data.vehicle_info.model = carly_data.get("model", vehicle_data.vehicle_info.model)
    vehicle_data.vehicle_info.vin = carly_data.get("vin", vehicle_data.vehicle_info.vin)
    vehicle_data.vehicle_info.series_description = carly_data.get("Series description", vehicle_data.vehicle_info.series_description)

    # Update EngineSpecs
    vehicle_data.specifications.fuel.fuel_type = carly_data.get("Fuel type", vehicle_data.specifications.fuel.fuel_type)
    vehicle_data.specifications.engine.power_bhp = int(carly_data.get("Power (bhp)", 0)) or None
    vehicle_data.specifications.engine.power_kw = float(carly_data.get("Power (kw)", 0)) or None
    vehicle_data.specifications.engine.number_of_cylinders = int(carly_data.get("Number of cylinders", 0)) or None
    vehicle_data.specifications.engine.fuel_system = carly_data.get("Fuel system")
    vehicle_data.specifications.engine.aspiration = carly_data.get("Aspiration")
    vehicle_data.specifications.engine.fuel_consumption_l_100km = float(carly_data.get("l/100km", 0)) or None
    vehicle_data.specifications.engine.fuel_consumption_mpg = float(carly_data.get("mpg", 0)) or None
    vehicle_data.specifications.engine.torque_ftlb = float(carly_data.get("Torque (ftLb)", 0)) or None
    vehicle_data.specifications.engine.torque_nm = float(carly_data.get("Torque (nm)", 0)) or None

    # Update TransmissionSpecs
    vehicle_data.specifications.transmission.number_of_gears = int(carly_data.get("Number of gears", 0)) or None

    # Update PerformanceSpecs
    vehicle_data.specifications.performance.top_speed_kph = int(carly_data.get("Top speed (kph)", 0)) or None
    vehicle_data.specifications.performance.top_speed_mph = int(carly_data.get("Top speed (mph)", 0)) or None

    # Update DimensionSpecs
    vehicle_data.specifications.dimensions.length = int(carly_data.get("Car length", 0)) or None
    vehicle_data.specifications.dimensions.height = int(carly_data.get("Height", 0)) or None
    vehicle_data.specifications.dimensions.width = int(carly_data.get("Width", 0)) or None
    vehicle_data.specifications.dimensions.wheel_base = int(carly_data.get("Wheel base", 0)) or None
    vehicle_data.specifications.dimensions.unladen_weight = int(carly_data.get("Unladen weight", 0)) or None

    # Update ChassisSpecs
    vehicle_data.specifications.chassis.drive_type = carly_data.get("Drive type")
    vehicle_data.specifications.chassis.driving_axle = carly_data.get("Driving axle")
    vehicle_data.specifications.chassis.number_of_axles = int(carly_data.get("Number of axles", 0)) or None
    vehicle_data.specifications.chassis.doors = int(carly_data.get("Number of doors", 0)) or vehicle_data.specifications.chassis.doors

    # Update FuelSpecs
    vehicle_data.specifications.fuel.fuel_tank_capacity = int(carly_data.get("Fuel tank capacity", 0)) or None

    # Update VehicleStatus
    vehicle_data.vehicle_status.type_approval_category = carly_data.get("Type approval category", vehicle_data.vehicle_status.type_approval_category)
    vehicle_data.vehicle_status.euro_status = carly_data.get("Euro status") or vehicle_data.vehicle_status.euro_status

    return vehicle_data


__all__ = ['get_carly_vehicle_history']