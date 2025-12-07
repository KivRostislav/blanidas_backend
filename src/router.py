from fastapi import APIRouter

from src.institution.router import router as institution_router
from src.institution_type.router import router as institution_type_router
from src.equipment_model.router import router as equipment_model_router
from src.equipment_category.router import router as equipment_category_router
from src.manufacturer.router import router as manufacturer_router
from src.supplier.router import router as supplier_router
from src.equipment.router import router as equipment_router
from src.spare_part_category.router import router as spare_part_category_router
from src.spare_part.router import router as spare_part_router
from src.repair_request.router import router as repair_request_router
from src.failure_type.router import router as failure_type_router
from src.summary.router import router as summary_router
from src.auth.router import router as auth_router
from src.health_check.router import router as health_check
from src.statistics.router import router as statistics_router

router = APIRouter(prefix="/api")

router.include_router(institution_router)
router.include_router(institution_type_router)
router.include_router(equipment_model_router)
router.include_router(equipment_category_router)
router.include_router(manufacturer_router)
router.include_router(equipment_router)
router.include_router(auth_router)
router.include_router(institution_type_router)
router.include_router(supplier_router)
router.include_router(spare_part_category_router)
router.include_router(spare_part_router)
router.include_router(repair_request_router)
router.include_router(failure_type_router)
router.include_router(summary_router)
router.include_router(health_check)
router.include_router(statistics_router)
