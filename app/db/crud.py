from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memory, Task, TaskStep, TaskStepStatus, User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    user = (await session.scalars(stmt)).one_or_none()

    if user:
        # обновляем username, если изменился
        if user.username != username:
            user.username = username
        return user

    # создаём нового пользователя
    user = User(
        telegram_id=telegram_id,
        username=username,
    )
    session.add(user)
    await session.flush()

    return user


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    stmt = select(User).where(User.telegram_id == telegram_id)
    return (await session.scalars(stmt)).one_or_none()


async def create_task(session: AsyncSession, user_id: int, title: str):
    task = Task(
        user_id=user_id,
        title=title,
    )
    session.add(task)
    await session.flush()
    return task


async def add_task_steps(session: AsyncSession, task_id: int, steps: list[str]):
    task_steps = [
        TaskStep(
            task_id=task_id,
            step_order=i,
            description=description,
        )
        for i, description in enumerate(steps, 1)
    ]

    session.add_all(task_steps)
    await session.flush()
    return task_steps


async def get_task_by_id(
    session: AsyncSession,
    task_id: int,
) -> TaskStep | None:
    stmt = select(Task).where(Task.id == task_id)
    return (await session.scalars(stmt)).one_or_none()


async def get_step_by_id(
    session: AsyncSession,
    step_id: int,
) -> TaskStep | None:
    stmt = select(TaskStep).where(TaskStep.id == step_id)
    return (await session.scalars(stmt)).one_or_none()


async def get_next_pending_step(session: AsyncSession, task_id: int):
    stmt = (
        select(TaskStep)
        .where(TaskStep.task_id == task_id)
        .where(TaskStep.status == TaskStepStatus.PENDING)
        .order_by(TaskStep.step_order.asc())
        .limit(1)
    )

    result = await session.execute(stmt)
    return result.scalars().first()


async def mark_step_in_progress(session: AsyncSession, step_id: int):
    task_step = await get_step_by_id(session, step_id)

    if not task_step:
        return None

    task_step.status = TaskStepStatus.IN_PROGRESS
    return task_step


async def update_step_result(session: AsyncSession, step_id: int, result: dict):
    task_step = await get_step_by_id(session, step_id)

    if not task_step:
        return None

    task_step.status = TaskStepStatus.DONE
    task_step.result = result["text"]
    task_step.sources_json = result["sources"]
    return task_step


async def mark_step_error(session: AsyncSession, step_id: int, error: str):
    task_step = await get_step_by_id(session, step_id)

    if not task_step:
        return None

    task_step.status = TaskStepStatus.ERROR
    task_step.result = error
    return task_step


async def get_completed_steps(session: AsyncSession, task_id: int):
    stmt = (
        select(TaskStep)
        .where(TaskStep.task_id == task_id)
        .where(TaskStep.status == TaskStepStatus.DONE)
        .order_by(TaskStep.step_order.asc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def save_memory(
    session: AsyncSession, user_id: int, task_id: int, title: str, summary: str, sources_json: list | None = None
):
    memory = Memory(
        user_id=user_id,
        task_id=task_id,
        title=title,
        summary=summary,
        sources_json=sources_json or [],
    )
    session.add(memory)
    await session.flush()
    return memory


async def get_last_memories(
    session: AsyncSession,
    user_id: int,
    limit: int = 5,
):
    stmt = select(Memory).where(Memory.user_id == user_id).order_by(Memory.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_memory_by_id(
    session: AsyncSession,
    memory_id: int,
    user_id: int,
):
    stmt = select(Memory).where(Memory.id == memory_id).where(Memory.user_id == user_id)
    return (await session.scalars(stmt)).one_or_none()


async def get_recent_memories(
    session: AsyncSession,
    user_id: int,
    limit: int = 3,
):
    stmt = select(Memory).where(Memory.user_id == user_id).order_by(Memory.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


def build_memory_context(memories: list[Memory]) -> str:
    if not memories:
        return ""

    lines = []
    for m in memories:
        lines.append(f"- {m.title}: {m.summary[:300]}")

    return (
        "=== PREVIOUS RESEARCH CONTEXT ===\n"
        "The user has already completed the following research:\n\n" + "\n".join(lines) + "\n\n"
        "If the current request overlaps with these topics, "
        "DO NOT repeat the same material.\n"
        "=== END CONTEXT ==="
    )


async def get_task_waiting_clarification(session, user_id):
    stmt = select(Task).where(Task.user_id == user_id).where(Task.clarification_needed.is_(True)).limit(1)
    return (await session.scalars(stmt)).one_or_none()


async def clear_clarification_state(session, task):
    task.clarification_needed = False
    task.clarification_context = None
    await session.flush()


async def save_clarification_state(session, user_id, original_input):
    task = Task(
        user_id=user_id,
        title=original_input,
        clarification_needed=True,
        clarification_context=original_input,
    )
    session.add(task)
    await session.flush()
