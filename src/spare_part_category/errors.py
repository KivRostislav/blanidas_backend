from src.exceptions import ErrorCode, ErrorsMap, ErrorMap

errors_map: ErrorsMap = {
    ErrorCode.duplication: {
        "name": ErrorMap(code="name exists", message="Категорія запчастин з такою назвою уже існує"),
    },
    ErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Категорії запчастин з таким id не існує")
    }
}