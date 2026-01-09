from sqlalchemy import Select, or_

from src.filters import Filters, FilterRelatedFieldsMap, apply_filters, get_filter_value
from src.institution.schemas import Institution


def apply_institution_filters(stmt: Select, data: Filters, related_fields: FilterRelatedFieldsMap) -> Select:
    stmt = apply_filters(stmt, data, related_fields)

    name_or_address = get_filter_value(data.get("name_or_address"), column=Institution.name)
    if name_or_address is not None:
        stmt = stmt.where(
            or_(
                Institution.name.ilike(f"%{name_or_address}%"),
                Institution.address.ilike(f"%{name_or_address}%"),
            )
        )

    return stmt