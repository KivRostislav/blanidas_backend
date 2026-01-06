from src.exceptions import ErrorCode, ErrorMap

error_map: dict[ErrorCode, dict[str, ErrorMap]] = {
    ErrorCode.duplication: {
        "name": ErrorMap(code="name exists", message="Виробник з такою назвою уже існує"),
    },
    ErrorCode.foreign_key: {
        "assigned_engineer_id": ErrorMap(code="engineer does not exist", message="Інженера з таким ідентифікатором не існує"),
    },
    ErrorCode.check_constraint: {
        "quantity": ErrorMap(code="invalid quantity", message="Вказана кількість запчастин перевищує кількість на складі")
    },
    ErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Виробника з таким id не існує")
    },
    ErrorCode.unsupported_file_type: {
        "photos": ErrorMap(code="unsupported file type", message="Файл має невідомий або непідтримуваний формат")
    }
}

