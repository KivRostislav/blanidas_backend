from src.exceptions import ErrorCode, ErrorsMap, ErrorMap

errors_map: ErrorsMap = {
    ErrorCode.duplication: {
        "name": ErrorMap(code="name exists", message="Постачальник з такою назвою уже існує"),
    },
    ErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Постачальник з таким id не існує")
    }
}