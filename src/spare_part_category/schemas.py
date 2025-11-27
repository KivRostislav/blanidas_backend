from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel


class SparePartCategory(BaseDatabaseModel):
    __tablename__ = "spare_part_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    spare_parts: Mapped[list["SparePart"]] = relationship(back_populates="spare_part_category")
