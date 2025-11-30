from datetime import date

from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import TypeDecorator, Date

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