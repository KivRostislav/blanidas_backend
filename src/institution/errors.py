from src.exceptions import ErrorsMap, DomainErrorCode, ErrorMap, ApiErrorCode

errors_map: ErrorsMap = {
    DomainErrorCode.duplication: {
        "name": ErrorMap(code=ApiErrorCode.value_already_exists, message="Заклад з такою назвою вже існує"),
    },
    DomainErrorCode.foreign_key: {
        "institution_type_id": ErrorMap(code=ApiErrorCode.related_entity_not_found, message="Тип закладу з таким ідентифікатором не існує")
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Закладу з таким ідентифікатором не існує")
    }
}
