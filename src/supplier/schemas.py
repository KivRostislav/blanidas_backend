from sqlalchemy.orm import Mapped, relationship, mapped_column
from src.database import BaseDatabaseModel


class Supplier(BaseDatabaseModel):
    __tablename__ = "supplier"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)

    spare_parts: Mapped[list["SparePart"]] = relationship(back_populates="supplier", lazy="noload")
