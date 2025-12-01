from src.repair_request.models import RepairRequestInfo
from src.repair_request.schemas import RepairRequest
from src.services import GenericServices


class RepairRequestServices(GenericServices[RepairRequest, RepairRequestInfo]):

