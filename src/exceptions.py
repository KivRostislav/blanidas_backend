import re
from enum import Enum

from sqlalchemy.exc import IntegrityError

class ErrorCode(str, Enum):
    duplication = "duplication"
    foreign_key = "foreign key"
    not_entity = "not entity"
    check_constraint = "check constraint"

    unsupported_file_type = "unsupported file type"

    authentication = "authentication"
    invalid_token = "invalid token"

class ErrorMap:
    code: str
    message: str

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

ErrorsMap = dict[ErrorCode, dict[str, ErrorMap]]


class DomainError(Exception):
    code: ErrorCode
    field: str

    def __init__(self, code: ErrorCode, field: str = ""):
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
        return DomainError(ErrorCode.duplication, match.group(1))
    if "foreign key constraint" in message:
        match = re.search(r"Key \((.*?)\)=\((.*?)\) is not present", message)
        return DomainError(ErrorCode.foreign_key, match.group(1))
    if "violates check constraint" in message:
        match = re.search(r'violates check constraint "(.*?)"', message)
        if match:
            constraint_name = match.group(1)
            column_match = re.search(r'ck_[^_]+_([^_]+)', constraint_name)
            column_name = column_match.group(1) if column_match else None
            return DomainError(ErrorCode.check_constraint, column_name)

    return None

class ForeignKeyNotFoundError(DomainError):
    def __init__(self):
        super().__init__("One or more referenced records do not exist.")

class UniqueConstraintError(DomainError):
    def __init__(self):
        super().__init__("A record with these unique fields already exists.")

class NotFoundError(DomainError):
    def __init__(self, model_name: str | None = None, record_id: int | None = None):
        message = "Requested resource was not found."
        if model_name and record_id:
            message = f"{model_name} with ID {record_id} was not found."
        super().__init__(message)

