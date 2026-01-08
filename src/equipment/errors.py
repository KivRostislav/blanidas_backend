from src.exceptions import ErrorMap, ErrorsMap, DomainErrorCode, ApiErrorCode

errors_map: ErrorsMap = {
    DomainErrorCode.duplication: {
        "serial_number": ErrorMap(code=ApiErrorCode.value_already_exists, message="Обладнання з таким серійним номером уже існує"),
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Обладнання з таким ідентифікатором  не існує")
    }
}