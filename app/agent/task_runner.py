from aiogram.types import Message

from app.agent.final_report import FinalReportAgent
from app.agent.step_executor import StepExecutor
from app.db.crud import (
    get_completed_steps,
    get_next_pending_step,
    get_task_by_id,
    mark_step_error,
    mark_step_in_progress,
    save_memory,
    update_step_result,
)


class TaskRunner:
    def __init__(self):
        self.executor = StepExecutor()
        self.reporter = FinalReportAgent()

    async def run_task(self, session, task_id: int, message: Message):
        while True:
            step = await get_next_pending_step(session, task_id)
            if not step:
                break

            await mark_step_in_progress(session, step.id)

            try:
                print(f"ENTER executor step order: {step.step_order}")
                output = await self.executor.execute(step.description)
                await update_step_result(session, step.id, output)
                await message.answer(f"Шаг №{step.step_order} изучен 🔍")

            except Exception as e:
                await mark_step_error(session, step.id, str(e))
                print(f"DEBUG run_task: {e}")
                # break

        # 2. собираем результаты
        steps = await get_completed_steps(session, task_id)
        steps_results = [step.result for step in steps]
        sources = [step.sources_json for step in steps]
        all_sources: list[str] = []
        for step in steps:
            if step.sources_json:
                all_sources.extend(step.sources_json)

        all_sources = list(set(all_sources))

        # 3. генерируем итог
        print("ENTER report generate")
        final_report = await self.reporter.generate(steps_results, sources)

        # 4. сохраняем в память
        task = await get_task_by_id(session, task_id)
        await save_memory(
            session=session,
            user_id=task.user_id,
            task_id=task_id,
            title=task.title,
            summary=final_report,
            sources_json=all_sources,
        )

        return final_report
