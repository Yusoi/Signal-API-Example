from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from flags.misc.db.base import Base


class Flags(Base):
    __tablename__ = "flags"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)
