from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.spare_part.schemas import SparePart


class Supplier(BaseDatabaseModel):
    __tablename__ = "supplier"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    contact_email: Mapped[str] = mapped_column()
    contact_phone: Mapped[str] = mapped_column()
# gggggggggggggggggggggggggggggggggggggggggggggggggggggg cascade
    spare_parts: Mapped[list["SparePart"]] = relationship(back_populates="supplier", cascade="all")
