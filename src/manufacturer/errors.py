from src.exceptions import DomainErrorCode, ErrorMap, ApiErrorCode

error_map: dict[DomainErrorCode, dict[str, ErrorMap]] = {
    DomainErrorCode.duplication: {
        "name": ErrorMap(code=ApiErrorCode.value_already_exists, message="Виробник з такою назвою уже існує"),
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Виробника з таким ідентифікатором не існує")
    }
}

