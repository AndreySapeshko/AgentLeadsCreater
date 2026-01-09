import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.agent.detect_repeat import detect_repeat
from app.agent.utils import ask_clarification, build_continuation_context, is_short, run_research
from app.db.crud import (
    build_memory_context,
    clear_clarification_state,
    get_last_memories,
    get_memory_by_id,
    get_or_create_user,
    get_recent_memories,
    get_task_waiting_clarification,
    get_user_by_telegram_id,
    save_clarification_state,
)
from app.db.session import AsyncSessionLocal

logger = logging.getLogger("bot")

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message):
    print("ENTER start_cmd")
    telegram_id = message.from_user.id
    username = message.from_user.username

    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=telegram_id,
            username=username,
        )
        await session.commit()

    await message.answer(
        f"👋 Привет!\n\n"
        f"Ты успешно зарегистрирован.\n"
        f"Твой ID: {user.telegram_id}\n"
        f"Имя: {user.username}\n"
        "AgentResearcher готов. 🚀\n"
        "Пришли задачу для исследования."
    )


@router.message(Command("history"))
async def history_handler(message: Message):
    print("ENTER history_handler")
    async with AsyncSessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Сначала отправь /start, чтобы зарегистрироваться.")
            return
        memories = await get_last_memories(session, user.id)

    if not memories:
        await message.answer("История пока пуста.")
        return

    text = "📚 Последние исследования:\n\n"
    for m in memories:
        text += f"#{m.id} — {m.title}\n"

    text += "\nИспользуй /last или /show <id>"
    await message.answer(text)


@router.message(Command("last"))
async def last_handler(message: Message):
    print("ENTER last_handler")
    async with AsyncSessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Сначала отправь /start, чтобы зарегистрироваться.")
            return
        memories = await get_last_memories(session, user.id, limit=1)

    if not memories:
        await message.answer("Нет сохранённых исследований.")
        return

    await message.answer(memories[0].summary)


@router.message(Command("show"))
async def show_handler(message: Message, command: CommandObject):
    print("ENTER show_handler")
    if not command.args:
        await message.answer("Укажи ID исследования: /show 3")
        return

    memory_id = int(command.args)

    async with AsyncSessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        print(f"message.from_user.id: {message.from_user.id}")
        if user is None:
            await message.answer("Сначала отправь /start, чтобы зарегистрироваться.")
            return
        memory = await get_memory_by_id(session, memory_id, user.id)

    if not memory:
        await message.answer("Исследование не найдено.")
        return

    await message.answer(f"📌 {memory.title}\n\n{memory.summary}")


@router.message(F.text & ~F.text.startswith("/"))
async def handle_task(message: Message):
    print("ENTER handle_task")
    user_input = message.text.strip()
    async with AsyncSessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Сначала отправь /start, чтобы зарегистрироваться.")
            return

        memories = await get_recent_memories(session, user.id)

        # 1. Проверяем: не ждём ли мы уточнение
        pending_task = await get_task_waiting_clarification(session, user.id)
        if pending_task:
            memory_context = build_continuation_context(
                pending_task.clarification_context,
                memories,
            )

            enriched_input = "User clarification:\n" + user_input

            await clear_clarification_state(session, pending_task)

            await run_research(
                user=user,
                user_input=enriched_input,
                session=session,
                message=message,
                task=pending_task,
                memory_context=memory_context,
            )
            return

        # 2. Обычный вход

        is_repeat = await detect_repeat(user_input, memories)
        logger.info(
            "Agent flow: user=%s repeat=%s clarification=%s",
            user.id,
            is_repeat,
            bool(pending_task),
        )
        if is_repeat and is_short(user_input):
            await ask_clarification(message)

            await save_clarification_state(
                session=session,
                user_id=user.id,
                original_input=user_input,
            )
            await session.commit()
            return

        # 3. Иначе — сразу исследуем
        memory_context = build_memory_context(memories)
        await run_research(
            user=user, user_input=user_input, session=session, message=message, memory_context=memory_context
        )
