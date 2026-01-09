import enum
from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)

    memories: Mapped[list["Memory"]] = relationship(
        "Memory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User telegram_id={self.telegram_id} username={self.username}>"


# ---------- ENUM for task status ----------
class TaskStatus(str, enum.Enum):
    NEW = "new"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DONE = "done"


# ---------- ENUM for task_steps status ----------
class TaskStepStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ERROR = "error"


# ---------- TASKS ----------
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"),
        default=TaskStatus.NEW,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    clarification_needed: Mapped[bool] = mapped_column(default=False)
    clarification_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    # связь 1 → много steps
    steps: Mapped[list["TaskStep"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )

    # связь с user
    user = relationship("User", back_populates="tasks")


User.tasks = relationship("Task", back_populates="user")


# ---------- TASK STEPS ----------
class TaskStep(Base):
    __tablename__ = "task_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    step_order: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    status: Mapped[TaskStepStatus] = mapped_column(
        Enum(TaskStepStatus, name="task_step_status"),
        default=TaskStepStatus.PENDING,
    )
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    sources_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    task: Mapped[Task] = relationship("Task", back_populates="steps")


# ---------- Memory ----------
class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=False)
    sources_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped[User] = relationship("User", back_populates="memories")
    task: Mapped["Task"] = relationship()
