"""
Host Agent — Gradio frontend + Google ADK routing agent.

Architecture: Frontend (Gradio) ← Host Agent (ADK) → A2A Clients → Remote Agents
"""

import asyncio
import os
import sys
import traceback
from collections.abc import AsyncIterator
from pprint import pformat

import gradio as gr
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from host_agent.routing_agent import root_agent as routing_agent  # noqa: E402

APP_NAME = "routing_app"
USER_ID = "default_user"
SESSION_ID = "default_session"

SESSION_SERVICE = InMemorySessionService()
RUNNER = Runner(
    agent=routing_agent,
    app_name=APP_NAME,
    session_service=SESSION_SERVICE,
)


async def get_response(
    message: str,
    history: list[gr.ChatMessage],
) -> AsyncIterator[gr.ChatMessage]:
    """Stream responses from the host agent to the Gradio UI."""
    try:
        async for event in RUNNER.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(role="user", parts=[types.Part(text=message)]),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        fc = pformat(part.function_call.model_dump(exclude_none=True), indent=2, width=80)
                        yield gr.ChatMessage(
                            role="assistant",
                            content=f"🛠️ **Tool Call: {part.function_call.name}**\n```python\n{fc}\n```",
                        )
                    elif part.function_response:
                        resp = part.function_response.response
                        data = resp.get("response", resp) if isinstance(resp, dict) else resp
                        yield gr.ChatMessage(
                            role="assistant",
                            content=f"⚡ **Response from {part.function_response.name}**\n```json\n{pformat(data, indent=2, width=80)}\n```",
                        )

            if event.is_final_response():
                text = ""
                if event.content and event.content.parts:
                    text = "".join(p.text for p in event.content.parts if p.text)
                elif event.actions and event.actions.escalate:
                    text = f"Agent escalated: {event.error_message or 'No message.'}"
                if text:
                    yield gr.ChatMessage(role="assistant", content=text)
                break
    except Exception:
        traceback.print_exc()
        yield gr.ChatMessage(
            role="assistant",
            content="An error occurred. Check server logs.",
        )


async def main():
    await SESSION_SERVICE.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    with gr.Blocks(theme=gr.themes.Ocean(), title="A2A Host Agent") as demo:
        gr.Image(
            "https://a2a-protocol.org/latest/assets/a2a-logo-black.svg",
            width=100, height=100, scale=0,
            show_label=False,
            container=False,
        )
        gr.ChatInterface(
            get_response,
            title="A2A Host Agent",
            description="Ask about weather or Airbnb accommodation",
        )

    demo.queue().launch(server_name="0.0.0.0", server_port=8083)


if __name__ == "__main__":
    asyncio.run(main())