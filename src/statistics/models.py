from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel

class StatisticsTimeStep(str, Enum):
    hour = "hour"
    day = "day"
    week = "week"
    month = "month"

class KPIChange(str, Enum):
    up = "up"
    down = "down"
    no_change = "no_change"

class KPI(BaseModel):
    title: str
    value: str
    change: KPIChange
    change_percent: float

class CategoricalChartDataItem(BaseModel):
    model_id: int
    label: str
    value: int

class TimelinePoint(BaseModel):
    period: str
    count: int

class TimeFrame(BaseModel):
    from_date: datetime
    to_date: datetime
    step: StatisticsTimeStep

class EquipmentBreakdownItem(BaseModel):
    serial_number: str
    model_name: str
    center_name: str
    breakdown_count: int
    avg_repair_seconds: float

class StatisticsResponse(BaseModel):
    time_frame: TimeFrame

    total_breakdown_count_kpi: KPI
    average_repair_time_kpi: KPI
    institutions_kpi: KPI
    used_spare_parts_kpi: KPI

    center_breakdown: list[CategoricalChartDataItem]
    time_dynamics: list[TimelinePoint]
    failure_types: list[CategoricalChartDataItem]

    model_breakdown: list[CategoricalChartDataItem]
    average_repair_time: list[CategoricalChartDataItem]

    spare_part_categories: list[CategoricalChartDataItem]
    used_spare_parts: list[CategoricalChartDataItem]

    equipment_breakdown: list[EquipmentBreakdownItem]


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

class EquipmentBreakdown(BaseModel):
    items: list[EquipmentBreakdownItem]
