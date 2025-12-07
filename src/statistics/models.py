from datetime import date

from pydantic import BaseModel


class CenterBreakdownItem(BaseModel):
    center_name: str
    breakdown_count: int

class TimeDynamicsItem(BaseModel):
    week: int
    breakdown_count: int

class FaultTypeItem(BaseModel):
    type: str
    count: int

class TimeFrame(BaseModel):
    from_date: date
    to_date: date

class StatisticsResponse(BaseModel):
    time_frame: TimeFrame
    items: list[CenterBreakdownItem]