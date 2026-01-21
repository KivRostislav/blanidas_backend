from src.exceptions import ErrorsMap, DomainErrorCode, ErrorMap, ApiErrorCode

errors_map: ErrorsMap = {
    DomainErrorCode.duplication: {
        "name": ErrorMap(code=ApiErrorCode.value_already_exists, message="Заклад з такою назвою вже існує"),
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Закладу з таким ідентифікатором не існує")
    }
}
