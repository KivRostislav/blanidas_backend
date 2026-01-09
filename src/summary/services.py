from src.database import DatabaseSession
from src.exceptions import DomainError, DomainErrorCode
from src.summary.models import SummaryResponse
from src.summary.queries import SUMMARY_RULES


class SummaryServices:
    @staticmethod
    async def get(database: DatabaseSession, schema: str) -> SummaryResponse:
        if schema not in SUMMARY_RULES:
            raise DomainError(code=DomainErrorCode.not_entity)

        rules = SUMMARY_RULES[schema]["rules"]
        response_model = SUMMARY_RULES[schema]["response_model"]

        result = {}
        for rule_name, rule_func in rules.items():
            result[rule_name] = await rule_func(database)
        return response_model.model_validate(result)