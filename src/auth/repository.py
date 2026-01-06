from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import User
from src.filters import FilterRelatedField, apply_filters_wrapper, apply_filters
from src.repository import CRUDRepository
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting
from src.utils import build_relation


filter_related_fields_map = {
    "username": FilterRelatedField(join=None, column=User.username, use_exists=False),
    "role": FilterRelatedField(join=None, column=User.role, use_exists=False),
    "receive_low_stock_notification": FilterRelatedField(join=None, column=User.receive_low_stock_notification, use_exists=False),
    "receive_repair_request_created_notification": FilterRelatedField(join=None, column=User.receive_repair_request_created_notification, use_exists=False),
}

sorting_related_fields_map = {"username": SortingRelatedField(join=None, column=User.username)}

class AuthRepository(CRUDRepository[User]):
    def __init__(self):
        super().__init__(
            User,
            filter_callback=apply_filters_wrapper(apply_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_sorting, sorting_related_fields_map),
       )

    async def get_by_email(self, email: str, database: AsyncSession, preloads: list[str] | None = None) -> User | None:
        options = build_relation(User, preloads or [])
        stmt = select(User).options(*options).where(User.email == email)
        return (await database.execute(stmt)).unique().scalars().first()