"""
OpenAI-based Routing Agent — Delegates tasks to remote agents via A2A.
No Google ADK dependency.
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Any

import httpx
from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    Message,
    Part,
    Role,
    SendMessageRequest,
    StreamResponse,
    Task,
)
from dotenv import load_dotenv
from openai import OpenAI

try:
    from host_agent.remote_agent_connection import RemoteAgentConnections
except ImportError:
    from remote_agent_connection import RemoteAgentConnections

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ── Helpers ─────────────────────────────────────────────

def _text_part(text: str) -> Part:
    p = Part()
    p.text = text
    return p


def _extract_text(parts: list[Part]) -> str:
    return "\n".join(p.text for p in parts if getattr(p, "text", None))


def build_send_message_request(
    text: str,
    *,
    task_id: str | None = None,
    context_id: str | None = None,
) -> SendMessageRequest:
    msg = Message()
    msg.message_id = uuid.uuid4().hex
    msg.role = Role.ROLE_USER
    if task_id:
        msg.task_id = task_id
    if context_id:
        msg.context_id = context_id
    msg.parts.append(_text_part(text))

    req = SendMessageRequest()
    req.message.CopyFrom(msg)
    return req


# ── OpenAI Routing Agent ────────────────────────────────

class OpenAIRoutingAgent:
    def __init__(self) -> None:
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}

    async def init(self, remote_agent_addresses: list[str]) -> None:
        async with httpx.AsyncClient(timeout=30) as client_http:
            for address in remote_agent_addresses:
                try:
                    resolver = A2ACardResolver(httpx_client=client_http, base_url=address)
                    card = await resolver.get_agent_card()

                    self.remote_agent_connections[card.name] = RemoteAgentConnections(
                        agent_card=card,
                        agent_url=address,
                    )
                    self.cards[card.name] = card

                    print(f"✅ Connected to {card.name} at {address}")

                except Exception as e:
                    print(f"❌ Cannot reach agent at {address}: {e}")

    # ── OpenAI decision ─────────────────────────────

    def _build_agent_list(self) -> str:
        return "\n".join(
            f"- {c.name}: {c.description}" for c in self.cards.values()
        )

    async def decide(self, user_message: str, state: dict) -> dict:
        prompt = f"""
You are a routing agent.

Available agents:
{self._build_agent_list()}

Rules:
- Choose the best agent
- Rewrite the task clearly for that agent
- If a previous agent is active, continue with it

Return ONLY JSON:
{{"agent_name": "...", "task": "..."}}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message},
            ],
        )

        content = response.choices[0].message.content.strip()

        try:
            return json.loads(content)
        except Exception:
            # fallback (avoid crash)
            return {
                "agent_name": list(self.cards.keys())[0],
                "task": user_message,
            }

    # ── Send to remote agent ─────────────────────────

    async def send(
        self,
        agent_name: str,
        task: str,
        state: dict,
    ) -> str:
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f"Agent {agent_name!r} not found")

        state["active_agent"] = agent_name
        connection = self.remote_agent_connections[agent_name]

        request = build_send_message_request(
            text=task,
            task_id=state.get("task_id"),
            context_id=state.get("context_id") or str(uuid.uuid4()),
        )

        chunks: list[str] = []
        final_task: Task | None = None

        async for response in connection.send_message(request):
            if not isinstance(response, StreamResponse):
                continue

            kind = response.WhichOneof("payload") if hasattr(response, "WhichOneof") else None

            if kind == "task" and response.HasField("task"):
                final_task = response.task

            elif kind == "message" and response.HasField("message"):
                chunks.append(_extract_text(list(response.message.parts)))

            elif response.HasField("status_update"):
                su = response.status_update

                if su.status.HasField("message"):
                    chunks.append(_extract_text(list(su.status.message.parts)))

                if su.task_id:
                    state["task_id"] = su.task_id

                if su.context_id:
                    state["context_id"] = su.context_id

            elif response.HasField("artifact_update"):
                chunks.append(_extract_text(list(response.artifact_update.artifact.parts)))

        if final_task:
            for art in final_task.artifacts:
                chunks.append(_extract_text(list(art.parts)))

            state["task_id"] = final_task.id
            state["context_id"] = final_task.context_id

        return "\n".join(c for c in chunks if c).strip() or "(no response)"

    # ── Main entry ─────────────────────────────

    async def handle(self, message: str, state: dict) -> str:
        decision = await self.decide(message, state)

        return await self.send(
            agent_name=decision["agent_name"],
            task=decision["task"],
            state=state,
        )


# ── Singleton ──────────────────────────────────────────

async def create_agent() -> OpenAIRoutingAgent:
    agent = OpenAIRoutingAgent()

    await agent.init([
        os.getenv("AIR_AGENT_URL", "http://localhost:10002"),
        os.getenv("WEA_AGENT_URL", "http://localhost:10001"),
    ])

    return agent