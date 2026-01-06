from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.equipment.schemas import Equipment
from src.equipment_model.schemas import EquipmentModel
from src.failure_type.schemas import FailureType, FailureTypeRepairRequest
from src.institution.schemas import Institution
from src.repair_request.schemas import RepairRequest
from src.statistics.models import CenterBreakdownItem, StatisticsResponse, TimeFrame, \
    CenterBreakdown, FailureTypeItem, FailureTypes, ModelBreakdown, ModelBreakdownItem, StatisticsTimeStep, \
    TimeDynamicsItem, TimeDynamics, AvgRepairTimeItem, AvgRepairTime, EquipmentBreakdownItem, EquipmentBreakdown, \
    CategoricalChartDataItem

time_slot_format = {
    StatisticsTimeStep.hour: "%Y-%m-%d %H:00:00",
    StatisticsTimeStep.day: "%Y-%m-%d",
    StatisticsTimeStep.month: "%Y-%W-01",
}

class StatisticsServices:
    @staticmethod
    async def get(database: AsyncSession, data: dict) -> StatisticsResponse:
        query_institution = await database.execute(
            select(
                Institution.name.label("institution_name"),
                func.count(RepairRequest.id).label("breakdown_count")
            )
            .join(Equipment, Equipment.institution_id == Institution.id)
            .join(RepairRequest, RepairRequest.equipment_id == Equipment.id)
            .where(RepairRequest.created_at.between(data["from_date"], data["to_date"]))
            .group_by(Institution.id)
            .order_by(desc("breakdown_count"))
            .limit(10)
        )

        institution_items = [
            CategoricalChartDataItem(
                label=row[0],
                value=row[1]
            ) for row in query_institution.all()
        ]


        query_failure_types = await database.execute(
            select(FailureType.name, func.count(RepairRequest.id).label("count"))
            .select_from(FailureType)
            .join(FailureTypeRepairRequest, FailureType.id == FailureTypeRepairRequest.failure_type_id)
            .join(RepairRequest, FailureTypeRepairRequest.repair_request_id == RepairRequest.id)
            .where(RepairRequest.created_at.between(data["from_date"], data["to_date"]))
            .group_by(FailureType.id)
            .order_by(desc("count"))
            .limit(10)
        )

        failure_types_items = [
            FailureTypeItem(
                failure_type_id=row[0],
                failure_type_name=row[1],
                count=row[2]
            )
            for row in query_failure_types.all()
        ]

        query_models = (await database.execute(
            select(
                EquipmentModel.id,
                EquipmentModel.name,
                func.count(RepairRequest.id).label("count")
            )
            .select_from(EquipmentModel)
            .join(Equipment, EquipmentModel.id == Equipment.equipment_model_id)
            .join(RepairRequest, Equipment.id == RepairRequest.equipment_id)
            .where(RepairRequest.created_at.between(data["from_date"], data["to_date"]))
            .group_by(EquipmentModel.id)
            .order_by(desc("count"))
            .limit(10)
        )).all()

        models_items = [
            ModelBreakdownItem(
                model_id=row[0],
                model_name=row[1],
                breakdown_count=row[2]
            )
            for row in query_models
        ]


        if data["step"] == StatisticsTimeStep.week.value:
            time_col = func.date(RepairRequest.created_at, 'weekday 1', '-6 days')
        else:
            time_col = func.strftime(time_slot_format[data["step"]], RepairRequest.created_at)

        query_time = await database.execute(
            select(time_col.label("time_slot"), func.count(RepairRequest.id).label("breakdown_count"))
            .where(RepairRequest.created_at.between(data["from_date"], data["to_date"]))
            .group_by("time_slot")
            .order_by("time_slot")
        )
        time_dynamics = [
            TimeDynamicsItem(
                unit=row[0],
                breakdown_count=row[1]
            )
            for row in query_time.all()
        ]

        query_avg_repair_time = await database.execute(
            select(
                Institution.id,
                Institution.name,
                (
                    func.avg(
                        (func.julianday(RepairRequest.completed_at) -
                         func.julianday(RepairRequest.created_at)) * 86400
                    )
                ).label("avg_repair_seconds")
            )
            .select_from(Institution)
            .join(Equipment, Equipment.institution_id == Institution.id)
            .join(RepairRequest, RepairRequest.equipment_id == Equipment.id)
            .where(RepairRequest.completed_at.is_not(None))
            .group_by(Institution.id, Institution.name)
            .order_by(desc("avg_repair_seconds"))
            .limit(10)
        )

        avg_repair_time_items = [
            AvgRepairTimeItem(
                center_id=row[0],
                center_name=row[1],
                avg_repair_seconds=row[2],
            )
            for row in query_avg_repair_time.all()
        ]

        query_equipment = await database.execute(
            select(
                Equipment.serial_number,
                EquipmentModel.name.label("model_name"),
                Institution.name.label("center_name"),
                func.count(RepairRequest.id).label("breakdown_count"),
                func.avg(
                    (func.julianday(RepairRequest.completed_at) -
                     func.julianday(RepairRequest.created_at)) * 86400
                ).label("avg_repair_seconds")
            )
            .select_from(Equipment)
            .join(EquipmentModel, EquipmentModel.id == Equipment.equipment_model_id)
            .join(Institution, Institution.id == Equipment.institution_id)
            .join(RepairRequest, RepairRequest.equipment_id == Equipment.id)
            .where(RepairRequest.completed_at.is_not(None))
            .group_by(
                Equipment.id,
                Equipment.serial_number,
                EquipmentModel.name,
                Institution.name
            )
            .order_by(desc("breakdown_count"))
            .limit(10)
        )

        equipment_items = [
            EquipmentBreakdownItem(
                serial_number=row[0],
                model_name=row[1],
                center_name=row[2],
                breakdown_count=row[3],
                avg_repair_seconds=row[4],
            )
            for row in query_equipment.all()
        ]

        return StatisticsResponse(
            center_breakdown=CenterBreakdown(items=institution_items),
            failure_types=FailureTypes(items=failure_types_items),
            model_breakdown=ModelBreakdown(items=models_items),
            time_dynamics=TimeDynamics(items=time_dynamics),
            average_repair_time=AvgRepairTime(items=avg_repair_time_items),
            equipment_breakdown=EquipmentBreakdown(items=equipment_items),
            time_frame=TimeFrame(
                from_date=data["from_date"],
                to_date=data["to_date"],
                step=data["step"]
            ),
        )