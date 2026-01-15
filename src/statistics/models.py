from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel

class StatisticsTimeStep(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class TimeFrame(BaseModel):
    from_date: datetime
    to_date: datetime
    step: StatisticsTimeStep

class StatisticsFilters(BaseModel):
    time_frame: TimeFrame
    institution_ids: list[int]
    equipment_model_ids: list[int]
    failure_type_ids: list[int]

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
    label: str
    value: float

class TimelinePoint(BaseModel):
    period: datetime
    count: int

class EquipmentBreakdownItem(BaseModel):
    serial_number: str
    model_name: str
    institution_name: str
    breakdown_count: int
    average_repair_seconds: float

class StatisticsResponse(BaseModel):
    time_frame: TimeFrame

    #total_breakdown_count_kpi: KPI
    #average_repair_time_kpi: KPI
    #institutions_kpi: KPI
    #used_spare_parts_kpi: KPI

    institution_breakdown: list[CategoricalChartDataItem]
    time_dynamics: list[TimelinePoint]
    failure_types: list[CategoricalChartDataItem]

    model_breakdowns: list[CategoricalChartDataItem]
    average_repair_time: list[CategoricalChartDataItem]
    equipment_breakdowns: list[EquipmentBreakdownItem]
    used_spare_parts: list[CategoricalChartDataItem]

