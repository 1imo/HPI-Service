from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class VehicleInfo:
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    series_description: Optional[str] = None
    vin: Optional[str] = None
    registration: Optional[str] = None
    color: Optional[str] = None
    price: Optional[float] = None

@dataclass
class EngineSpecs:
    engine_size: Optional[int] = None
    power_bhp: Optional[int] = None
    power_kw: Optional[float] = None
    number_of_cylinders: Optional[int] = None
    fuel_system: Optional[str] = None
    aspiration: Optional[str] = None
    fuel_consumption_l_100km: Optional[float] = None
    fuel_consumption_mpg: Optional[float] = None
    torque_ftlb: Optional[float] = None
    torque_nm: Optional[float] = None

@dataclass
class TransmissionSpecs:
    type: Optional[str] = None
    number_of_gears: Optional[int] = None

@dataclass
class PerformanceSpecs:
    top_speed_kph: Optional[int] = None
    top_speed_mph: Optional[int] = None

    def __post_init__(self):
        if self.top_speed_kph is not None and self.top_speed_mph is None:
            self.top_speed_mph = round(self.top_speed_kph / 1.60934)
        elif self.top_speed_mph is not None and self.top_speed_kph is None:
            self.top_speed_kph = round(self.top_speed_mph * 1.60934)

@dataclass
class DimensionSpecs:
    length: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None
    wheel_base: Optional[int] = None
    unladen_weight: Optional[int] = None

@dataclass
class ChassisSpecs:
    drive_type: Optional[str] = None
    driving_axle: Optional[str] = None
    number_of_axles: Optional[int] = None
    doors: Optional[int] = None

@dataclass
class FuelSpecs:
    fuel_type: Optional[str] = None
    fuel_tank_capacity: Optional[int] = None

@dataclass
class VehicleSpecifications:
    engine: Optional[EngineSpecs] = None
    transmission: Optional[TransmissionSpecs] = None
    performance: Optional[PerformanceSpecs] = None
    dimensions: Optional[DimensionSpecs] = None
    chassis: Optional[ChassisSpecs] = None
    fuel: Optional[FuelSpecs] = None

@dataclass
class RegistrationInfo:
    manufacture_date: Optional[int] = None
    first_registration_date: Optional[int] = None
    last_v5c_issue_date: Optional[int] = None
    mot_due_date: Optional[int] = None
    tax_due_date: Optional[int] = None

@dataclass
class VehicleStatus:
    type_approval_category: Optional[str] = None
    euro_status: Optional[str] = None
    co2_emissions: Optional[float] = None
    average_miles_per_year: Optional[float] = None
    previous_owners: Optional[int] = None
    has_plate_changes: Optional[bool] = None
    has_colour_changes: Optional[bool] = None
    has_salvage_records: Optional[bool] = None
    has_mileage_anomaly: Optional[bool] = None
    is_exported: Optional[bool] = None
    is_possible_taxi: Optional[bool] = None
    is_stolen: Optional[bool] = None
    has_outstanding_finance: Optional[bool] = None
    has_been_written_off: Optional[bool] = None
    mot_valid: Optional[bool] = None
    tax_valid: Optional[bool] = None

@dataclass
class VehicleScore:
    overall_score: Optional[int] = None
    age_score: Optional[int] = None
    mileage_score: Optional[int] = None
    mot_history_score: Optional[int] = None
    average_score: Optional[int] = None

@dataclass
class MOTTest:
    date: Optional[int] = None
    result: Optional[str] = None
    mileage: Optional[int] = None
    expiry_date: Optional[int] = None
    advisories: List[str] = field(default_factory=list)
    defects: List[str] = field(default_factory=list)

@dataclass
class MarketData:
    estimated_value: Optional[float] = None
    price_range: Optional[tuple] = None
    days_to_sell: Optional[int] = None
    similar_listings: Optional[int] = None

@dataclass
class VehicleDataModel:
    vehicle_info: Optional[VehicleInfo] = None
    specifications: Optional[VehicleSpecifications] = None
    registration_info: Optional[RegistrationInfo] = None
    vehicle_status: Optional[VehicleStatus] = None
    score: Optional[VehicleScore] = None
    mot_history: List[MOTTest] = field(default_factory=list)
    market_data: Optional[MarketData] = None

