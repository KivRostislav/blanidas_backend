from src.exceptions import ErrorMap, ErrorsMap, DomainErrorCode, ApiErrorCode

errors_map: ErrorsMap = {
    DomainErrorCode.duplication: {
        "name": ErrorMap(code=ApiErrorCode.value_already_exists, message="Категорія обладнання з такою назвою уже існує"),
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Категорії обладнання з таким ідентифікатором не існує")
    }
}