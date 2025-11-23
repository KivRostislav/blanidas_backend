from pydantic import BaseModel

class Pagination(BaseModel):
    offset: int | None = None
    limit: int | None = None
    order_by: str | None = None
    decs: bool = False

Filtered = dict[str, str]