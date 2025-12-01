from dataclasses import dataclass

from pydantic import BaseModel

class LowStockMessagePayload(BaseModel):
    receiver_username: str

    spare_part_name: str
    spare_part_serial_number: str

    spare_part_current_quantity: int
    spare_part_min_quantity: int