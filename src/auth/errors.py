from src.exceptions import ErrorMap, ErrorsMap, DomainErrorCode, ApiErrorCode

errors_map: ErrorsMap = {
    DomainErrorCode.duplication: {
        "email": ErrorMap(code=ApiErrorCode.value_already_exists, message="Користувач з таким email уже існує"),
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Користувача з таким ідентифікатором не існує")
    },
    DomainErrorCode.authentication: {
        "email, password": ErrorMap(code=ApiErrorCode.authentication, message="Не вдалось увійти.")
    }
}