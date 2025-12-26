class DomainError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

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

