from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.agent import ResearchPlanner
from app.agent.task_runner import TaskRunner
from app.db.crud import add_task_steps, create_task
from app.db.models import Memory, Task, User
from app.db.session import AsyncSessionLocal

MAX_TG_LEN = 4000  # запас


async def send_safe(message, text: str):
    parts = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) + 1 <= MAX_TG_LEN:
            current += line + "\n"
        else:
            parts.append(current.strip())
            current = line + "\n"

    if current:
        parts.append(current.strip())

    for part in parts:
        await message.answer(part)


async def run_research(
    user: User, user_input: str, session: AsyncSession, message: Message, memory_context: str, task: Task = None
):
    planner = ResearchPlanner()
    print("ENTER planner")
    plan = await planner.plan(user_input, memory_context)

    await message.answer(
        "Я понял задачу и составил план:\n\n" + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(plan["steps"]))
    )
    await message.answer("Начинаю выполнение задачи 🔍")

    if task:
        task.title = plan["title"]
    else:
        task = await create_task(session, user.id, plan["title"])
    await add_task_steps(session, task.id, plan["steps"])
    await session.commit()

    runner = TaskRunner()
    async with AsyncSessionLocal() as session:
        print("ENTER task runer")
        final_report = await runner.run_task(session, task.id, message)
        await session.commit()

    await message.answer("Исследование завершено ✅\n\nВот краткий итог:")
    await send_safe(message, final_report)


def is_short(text: str) -> bool:
    return len(text.strip()) < 100


async def ask_clarification(message: Message):
    await message.answer(
        """
        Ты уже исследовал эту тему ранее.

        Чтобы продолжить максимально полезно, уточни, пожалуйста:

        1️⃣ Цель исследования
           (например: обучение, применение в проекте, выбор инструмента)

        2️⃣ Уровень
           beginner / intermediate / advanced

        3️⃣ Формат результата
           brief (кратко) / standard / deep (с примерами)

        Ответь одним сообщением, например:
        "advanced, deep, для реального проекта"

        """
    )


def build_continuation_context(
    clarification_context: str,
    memories: list[Memory],
) -> str:
    parts = []

    # 1. Главный контекст — продолжение
    parts.append(
        "=== CURRENT CONTINUATION CONTEXT ===\n" f"{clarification_context}\n" "=== END CONTINUATION CONTEXT ==="
    )

    # 2. Фоновая память (если есть)
    if memories:
        memory_lines = []
        for m in memories:
            memory_lines.append(f"- Topic: {m.title}\n" f"  Summary: {m.summary[:200]}")

        parts.append(
            "=== BACKGROUND KNOWLEDGE (PAST RESEARCH) ===\n" + "\n".join(memory_lines) + "\n=== END BACKGROUND ==="
        )

    return "\n\n".join(parts)


def parse_executor_output(content: str) -> tuple[str, list[str]]:
    text = ""
    sources: list[str] = []

    if "SOURCES:" in content:
        text_part, sources_part = content.split("SOURCES:", 1)
        text = text_part.replace("TEXT:", "").strip()

        sources = [line.strip("- ").strip() for line in sources_part.splitlines() if line.strip()]
    else:
        text = content.strip()

    return text, sources
