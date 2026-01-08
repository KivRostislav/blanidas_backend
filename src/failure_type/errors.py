from src.exceptions import ErrorMap, ErrorsMap, DomainErrorCode, ApiError, ApiErrorCode

errors_map: ErrorsMap = {
    DomainErrorCode.duplication: {
        "name": ErrorMap(code=ApiErrorCode.value_already_exists, message="Тип поломки з такою назвою уже існує"),
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Типу поломки з таким ідентифікатором не існує")
    }
}