from sqlalchemy.orm import Mapped, relationship, mapped_column
from src.database import BaseDatabaseModel


class InstitutionType(BaseDatabaseModel):
    __tablename__ = "institution_type"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    institutions: Mapped[list["Institution"]] = relationship(back_populates="institution_type", lazy="noload")
