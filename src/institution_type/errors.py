from src.exceptions import DomainErrorCode, ErrorsMap, ErrorMap, ApiErrorCode

errors_map: ErrorsMap = {
    DomainErrorCode.duplication: {
        "name": ErrorMap(code=ApiErrorCode.value_already_exists, message="Тип закладу з такою назвою уже існує"),
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Типу закладу з таким ідентифікатором не існує")
    }
}