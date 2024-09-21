from datetime import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, String, BigInteger, Boolean, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at_type = Annotated[datetime, mapped_column(server_default=text("CURRENT_TIMESTAMP"))]
updated_at_type = Annotated[datetime, mapped_column(server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)]


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class User(Base):
    __tablename__ = 'subscribers'

    id: Mapped[intpk]

    # Account settings
    tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    hamster_token: Mapped[str] = mapped_column(String(100), nullable=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    account: Mapped[str] = mapped_column(String(30), default='HAMSTER_TOKEN_1')
    is_subscriber: Mapped[bool] = mapped_column(Boolean, default=1)

    created_at: Mapped[created_at_type]
    updated_at: Mapped[updated_at_type]

    settings = relationship("UserSetting", back_populates="user")


class UserSetting(Base):
    __tablename__ = 'settings'

    id: Mapped[intpk]
    FK__subscribers_id: Mapped[int] = mapped_column(ForeignKey("subscribers.id", ondelete='CASCADE'))

    # App settings
    send_to_group: Mapped[int] = mapped_column(Integer)
    save_to_file: Mapped[int] = mapped_column(Integer)
    apply_promo: Mapped[int] = mapped_column(Integer)
    spinner: Mapped[str] = mapped_column(String(30))
    lang: Mapped[str] = mapped_column(String(2))
    bonus_for_one_point: Mapped[int] = mapped_column(Integer, nullable=True)
    group_url: Mapped[str] = mapped_column(String(50), nullable=True)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=True)
    cards_in_top: Mapped[int] = mapped_column(Integer)
    all_cards_in_top: Mapped[int] = mapped_column()
    has_hamster_token: Mapped[int] = mapped_column()

    # Bot settings
    balance_threshold: Mapped[int] = mapped_column(Integer)
    complete_taps: Mapped[int] = mapped_column(Integer)
    complete_tasks: Mapped[int] = mapped_column(Integer)
    complete_cipher: Mapped[int] = mapped_column(Integer)
    complete_minigames: Mapped[int] = mapped_column(Integer)
    complete_combo: Mapped[int] = mapped_column(Integer)
    complete_autobuy_upgrades: Mapped[int] = mapped_column(Integer)
    complete_promocodes: Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship("User", back_populates="settings")
