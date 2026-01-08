from src.exceptions import DomainErrorCode, ErrorMap

error_map: dict[DomainErrorCode, dict[str, ErrorMap]] = {
    DomainErrorCode.duplication: {
        "name": ErrorMap(code="name exists", message="Виробник з такою назвою уже існує"),
    },
    DomainErrorCode.foreign_key: {
        "assigned_engineer_id": ErrorMap(code="engineer does not exist", message="Інженера з таким ідентифікатором не існує"),
    },
    DomainErrorCode.check_constraint: {
        "quantity": ErrorMap(code="invalid quantity", message="Вказана кількість запчастин перевищує кількість на складі")
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Виробника з таким id не існує")
    },
    DomainErrorCode.unsupported_file_type: {
        "photos": ErrorMap(code="unsupported file type", message="Файл має невідомий або непідтримуваний формат")
    }
}

