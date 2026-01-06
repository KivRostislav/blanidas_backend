from src.exceptions import ErrorsMap, ErrorCode, ErrorMap

errors_map: ErrorsMap = {
    ErrorCode.duplication: {
        "name": ErrorMap(code="name exists", message="Заклад з такою назвою уже існує"),
    },
    ErrorCode.foreign_key: {
        "institution_type_id": ErrorMap(code="institution type does not exists", message="Тип закладу з таким id не існує")
    },
    ErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Закладу з таким id не існує")
    }
}
