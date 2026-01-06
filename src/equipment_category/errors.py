from src.exceptions import ErrorMap, ErrorsMap, ErrorCode

errors_map: ErrorsMap = {
    ErrorCode.duplication: {
        "name": ErrorMap(code="name exists", message="Категорія обладнання з такою назвою уже існує"),
    },
    ErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Категорії обладнання з таким id не існує")
    }
}