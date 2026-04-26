"""Airbnb A2A AgentExecutor — bridges A2A protocol to the ADK Runner."""
from __future__ import annotations

import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import AgentCard, Part, Task, TaskState, TaskStatus
from google.adk import Runner
from google.genai import types as genai_types


logger = logging.getLogger(__name__)


def _text_part(text: str) -> Part:
    p = Part()
    p.text = text
    return p


def _a2a_part_to_genai(part: Part) -> genai_types.Part:
    which = part.WhichOneof("content")
    if which == "text":
        return genai_types.Part(text=part.text)
    raise ValueError(f"Unsupported a2a part: {which!r}")


def _genai_part_to_a2a(part: genai_types.Part) -> Part:
    out = Part()
    if part.text:
        out.text = part.text
    return out


class AirbnbAgentExecutor(AgentExecutor):
    """Wraps an ADK Runner and exposes it as an A2A AgentExecutor."""

    def __init__(self, runner: Runner, card: AgentCard) -> None:
        self.runner = runner
        self._card = card

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.message is None or not context.message.parts:
            raise ValueError("No message in request context")

        # Publish initial Task if needed
        if context.current_task is None:
            task = Task()
            task.id = context.task_id
            task.context_id = context.context_id
            status = TaskStatus()
            status.state = TaskState.TASK_STATE_SUBMITTED
            task.status.CopyFrom(status)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.start_work()

        # Ensure ADK session exists
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name, user_id="user", session_id=context.context_id
        )
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name, user_id="user", session_id=context.context_id
            )

        try:
            async for event in self.runner.run_async(
                session_id=session.id,
                user_id="user",
                new_message=genai_types.UserContent(
                    parts=[_a2a_part_to_genai(p) for p in context.message.parts],
                ),
            ):
                parts = (
                    event.content.parts if event.content and event.content.parts else []
                )
                converted = [_genai_part_to_a2a(p) for p in parts if p.text]

                if event.is_final_response():
                    if converted:
                        await updater.add_artifact(parts=converted, name="airbnb_result")
                    await updater.complete()
                    return

                if not event.get_function_calls() and converted:
                    await updater.update_status(
                        TaskState.TASK_STATE_WORKING,
                        message=updater.new_agent_message(converted),
                    )
        except Exception as exc:
            logger.exception("Airbnb agent failed: %s", exc)
            await updater.failed(
                message=updater.new_agent_message([_text_part(f"Error: {exc}")])
            )
            raise

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.cancel()