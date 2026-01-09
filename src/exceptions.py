import re
from enum import Enum

from sqlalchemy.exc import IntegrityError

class ApiErrorCode(str, Enum):
    value_already_exists = "value already exists"
    related_entity_not_found = "related entity not found"
    not_found = "not found"

    invalid_email_format = "invalid email format"
    invalid_phone_format = "invalid phone format"
    invalid_value = "invalid value"

class DomainErrorCode(str, Enum):
    duplication = "duplication"
    foreign_key = "foreign key"
    not_entity = "not entity"
    check_constraint = "check constraint"

    unsupported_file_type = "unsupported file type"

    authentication = "authentication"
    invalid_token = "invalid token"

class ErrorMap:
    code: ApiErrorCode
    message: str

    def __init__(self, code: ApiErrorCode, message: str):
        self.code = code
        self.message = message

ErrorsMap = dict[DomainErrorCode, dict[str, ErrorMap]]


class DomainError(Exception):
    code: DomainErrorCode
    field: str

    def __init__(self, code: DomainErrorCode, field: str = ""):
        self.code = code
        self.field = field

class ApiError(DomainError):
    error_map: ErrorsMap

    def __init__(self, domain: DomainError, error_map: ErrorsMap):
        self.code = domain.code
        self.field = domain.field
        self.error_map = error_map


def parse_integrity_error(error: IntegrityError) -> DomainError | None:
    message = str(error.args[0])
    if "duplicate key value" in message:
        match = re.search(r"Key \((.*?)\)=\((.*?)\) already exists", message)
        return DomainError(DomainErrorCode.duplication, match.group(1))
    if "foreign key constraint" in message:
        match = re.search(r"Key \((.*?)\)=\((.*?)\) is not present", message)
        return DomainError(DomainErrorCode.foreign_key, match.group(1))
    if "violates check constraint" in message:
        match = re.search(r'violates check constraint "(.*?)"', message)
        if match:
            constraint_name = match.group(1)
            column_match = re.search(r'ck_[^_]+_([^_]+)', constraint_name)
            column_name = column_match.group(1) if column_match else None
            return DomainError(DomainErrorCode.check_constraint, column_name)

    return None
