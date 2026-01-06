from src.exceptions import ErrorCode, ErrorMap

error_map: dict[ErrorCode, dict[str, ErrorMap]] = {
    ErrorCode.duplication: {
        "name": ErrorMap(code="name exists", message="Виробник з такою назвою уже існує"),
    },
    ErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Виробника з таким id не існує")
    }
}

