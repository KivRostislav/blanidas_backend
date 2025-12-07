from fastapi import APIRouter
from fastapi.params import Depends

from src.database import DatabaseSession
from src.pagination import Pagination, PaginationResponse
from src.supplier.models import SupplierInfo, SupplierFilters, SupplierCreate, SupplierUpdate
from src.supplier.services import SupplierServices

router = APIRouter(prefix="/suppliers", tags=["Supplier"])
services = SupplierServices()

@router.get("/", response_model=PaginationResponse[SupplierInfo])
async def get_supplier_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: SupplierFilters = Depends(),
) -> PaginationResponse[SupplierInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True)
    )

@router.post("/", response_model=SupplierInfo)
async def create_supplier_endpoint(
        model: SupplierCreate,
        database: DatabaseSession,
) -> SupplierInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.put("/", response_model=SupplierInfo)
async def update_supplier_endpoint(
        model: SupplierUpdate,
        database: DatabaseSession,
) -> SupplierInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.delete("/{id_}", response_model=None)
async def delete_supplier_endpoint(id_: int, database: DatabaseSession) -> None:
    return await services.delete(id_=id_, database=database)
