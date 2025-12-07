from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel

class StatisticsTimeStep(str, Enum):
    hour = "hour"
    day = "day"
    week = "week"
    month = "month"

class CenterBreakdownItem(BaseModel):
    center_id: int
    center_name: str
    breakdown_count: int

class CenterBreakdown(BaseModel):
    items: list[CenterBreakdownItem]

class FailureTypeItem(BaseModel):
    failure_type_name: str
    failure_type_id: int
    count: int

class FailureTypes(BaseModel):
    items: list[FailureTypeItem]

class ModelBreakdownItem(BaseModel):
    model_id: int
    model_name: str
    breakdown_count: int

class TimeDynamicsItem(BaseModel):
    unit: str
    breakdown_count: int

class TimeDynamics(BaseModel):
    items: list[TimeDynamicsItem]

class ModelBreakdown(BaseModel):
    items: list[ModelBreakdownItem]

class AvgRepairTimeItem(BaseModel):
    center_id: int
    center_name: str
    avg_repair_seconds: float

class AvgRepairTime(BaseModel):
    items: list[AvgRepairTimeItem]

class EquipmentBreakdownItem(BaseModel):
    serial_number: str
    model_name: str
    center_name: str
    breakdown_count: int
    avg_repair_seconds: float

class EquipmentBreakdown(BaseModel):
    items: list[EquipmentBreakdownItem]

class TimeFrame(BaseModel):
    from_date: datetime
    to_date: datetime
    step: StatisticsTimeStep

class StatisticsResponse(BaseModel):
    time_frame: TimeFrame
    center_breakdown: CenterBreakdown
    failure_types: FailureTypes
    model_breakdown: ModelBreakdown
    time_dynamics: TimeDynamics
    average_repair_time: AvgRepairTime
    equipment_breakdown: EquipmentBreakdown
