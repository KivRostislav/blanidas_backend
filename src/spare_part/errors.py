from src.exceptions import ErrorCode, ErrorsMap, ErrorMap

errors_map: ErrorsMap = {
    ErrorCode.duplication: {
        "name": ErrorMap(code="name exists", message="Категорія запчастин з такою назвою уже існує"),
        "institution_id, spare_part_id": ErrorMap(code="institution duplication", message="Передано дві локації з одинаковими ідентифікаторами закладів")
    },
    ErrorCode.foreign_key: {
        "institution_id": ErrorMap(code="institution does not exist", message="Закладу з таким ідентифікатором не існує"),
    },
    ErrorCode.not_entity: {
        "": ErrorMap(code="not found", message="Категорії запчастин з таким id не існує")
    }
}