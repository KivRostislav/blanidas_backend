import json

from fastapi import APIRouter
from fastapi.params import Depends, Query

from src.database import DatabaseSession
from src.decorators import domain_errors
from src.pagination import Pagination, PaginationResponse
from src.sorting import Sorting
from src.supplier.errors import errors_map
from src.supplier.models import SupplierInfo, SupplierCreate, SupplierUpdate
from src.supplier.services import SupplierServices

router = APIRouter(prefix="/suppliers", tags=["Supplier"])
services = SupplierServices()

@router.get("/", response_model=PaginationResponse[SupplierInfo])
async def get_supplier_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        sorting: Sorting = Depends(),
        filters: str | None = Query(None),
) -> PaginationResponse[SupplierInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        filters=json.loads(filters) if filters else None,
        sorting=None if sorting.sort_by == "" else sorting,
    )

@router.post("/", response_model=SupplierInfo)
@domain_errors(errors_map)
async def create_supplier_endpoint(model: SupplierCreate, database: DatabaseSession) -> SupplierInfo:
    return await services.create(data=model.model_dump(exclude_none=True), database=database)

@router.put("/", response_model=SupplierInfo)
@domain_errors(errors_map)
async def update_supplier_endpoint(model: SupplierUpdate, database: DatabaseSession) -> SupplierInfo:
    return await services.update(id_=model.id, data=model.model_dump(exclude_none=True), database=database)

@router.delete("/{id_}", response_model=int)
@domain_errors(errors_map)
async def delete_supplier_endpoint(id_: int, database: DatabaseSession) -> int:
    return await services.delete(id_=id_, database=database)
