from src.exceptions import ErrorMap, ErrorsMap, ErrorCode

errors_map: ErrorsMap = {
    ErrorCode.duplication: {
        "serial_number": ErrorMap(code="serial number exists", message="Обладнання з таким серійним номером уже існує"),
    },
    ErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Обладнання з таким id не існує")
    }
}