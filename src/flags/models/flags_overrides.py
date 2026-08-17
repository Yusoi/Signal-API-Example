from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from flags.misc.db.base import Base


class FlagOverrides(Base):
    __tablename__ = "flags_overrides"

    flag_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("flags.id"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), primary_key=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean)
