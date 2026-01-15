from datetime import date

from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import TypeDecorator, Date

class UkrainianPhoneNumber(PhoneNumber):
    default_region_code = 'UA'
    supported_regions = ['UA']
    phone_format = 'E164'
