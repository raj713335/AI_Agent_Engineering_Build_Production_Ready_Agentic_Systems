"""A2A Client wrapper — connects to a single remote agent via A2A protocol."""
from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

import httpx
from a2a.client import A2ACardResolver, Client, ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    SendMessageRequest,
    StreamResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)

TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Any]


class RemoteAgentConnections:
    """Holds an A2A Client connected to a single remote agent."""

    def __init__(self, agent_card: AgentCard, agent_url: str) -> None:
        self.card = agent_card
        self.url = agent_url
        self._httpx = httpx.AsyncClient(timeout=30)
        self.client: Client = ClientFactory(
            ClientConfig(streaming=True, httpx_client=self._httpx)
        ).create(card=agent_card)

    @classmethod
    async def from_url(cls, agent_url: str) -> "RemoteAgentConnections":
        client = httpx.AsyncClient(timeout=30)
        resolver = A2ACardResolver(httpx_client=client, base_url=agent_url)
        card = await resolver.get_agent_card()
        return cls(agent_card=card, agent_url=agent_url)

    async def send_message(
        self, request: SendMessageRequest
    ) -> AsyncIterator[StreamResponse]:
        async for response in self.client.send_message(request):
            yield response

    async def aclose(self) -> None:
        try:
            await self.client.close()
        except Exception:
            pass
        await self._httpx.aclose()