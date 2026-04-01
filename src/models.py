from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now,
        nullable=False
    )

    todos: Mapped[list['Todo']] = relationship(
        "Todo",
        back_populates="user",
        uselist=True  # viene por default
    )

    def serialize(self):
        # code de python
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }

    def serialize_with_items(self):
        return {
            "name": self.name,
            "todos": [todo.serialize() for todo in self.todos]
        }


class Todo(db.Model):
    __table_name__ = "todo"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    is_done: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped['User'] = relationship(
        "User",
        back_populates="todos"
    )

    def serialize(self):
        return {
            "label": self.label,
            "is_done": self.is_done,
            "id": self.id,
            "created_at": self.created_at.isoformat()
        }
