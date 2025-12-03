from pydantic import BaseModel

class LowStockMessagePayload(BaseModel):
    receiver_username: str

    spare_part_name: str
    spare_part_serial_number: str

    spare_part_current_quantity: int
    spare_part_min_quantity: int

class RepairRequestCreatedMessagePayload(BaseModel):
    receiver_username: str

    equipment_name: str
    repair_request_description: str
    repair_request_urgency_level: str

    repair_request_photos: list[str]