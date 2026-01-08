from src.exceptions import DomainErrorCode, ErrorsMap, ErrorMap, ApiErrorCode

errors_map: ErrorsMap = {
    DomainErrorCode.duplication: {
        "name": ErrorMap(code=ApiErrorCode.value_already_exists, message="Категорія запчастин з такою назвою уже існує"),
        "institution_id, spare_part_id": ErrorMap(code=ApiErrorCode.value_already_exists, message="Передано дві локації з одинаковими ідентифікаторами закладів")
    },
    DomainErrorCode.foreign_key: {
        "institution_id": ErrorMap(code=ApiErrorCode.related_entity_not_found, message="Закладу з таким ідентифікатором не існує"),
    },
    DomainErrorCode.not_entity: {
        "": ErrorMap(code=ApiErrorCode.not_found, message="Категорії запчастин з таким ідентифікатором не існує")
    }
}