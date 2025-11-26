from datetime import date

from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import TypeDecorator, Date


class Pagination(BaseModel):
    offset: int | None = None
    limit: int | None = None
    order_by: str | None = None
    decs: bool = False

Filtered = dict[str, str]

class UkrainianPhoneNumber(PhoneNumber):
    default_region_code = 'UA'
    supported_regions = ['UA']
    phone_format = 'NATIONAL'


class StringToDate(TypeDecorator):
    impl = Date

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value

    def process_result_value(self, value, dialect):
        return value