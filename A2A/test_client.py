import httpx

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import display_agent_card, new_text_message
from a2a.types import GetExtendedAgentCardRequest, Role, SendMessageRequest

from a2a.utils import AGENT_CARD_WELL_KNOWN_PATH


async def main() -> None:

    base_url = 'http://127.0.0.1:9999'

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url
        )
        public_card = await resolver.get_agent_card()
        display_agent_card(public_card)

        config = ClientConfig(streaming=False)
        client = await create_client(agent=public_card, client_config=config)

        message = new_text_message('Say Hello', role=Role.ROLE_USER)
        request = SendMessageRequest(message=message)

        async for chunk in client.send_message(request):
            print(chunk)

        streaming_config = ClientConfig(streaming=True)
        streaming_client = await create_client(agent=public_card, client_config=streaming_config)

        streaming_response = streaming_client.send_message(request)

        async for chunk in streaming_response:
            print('Response Chunk:')
            print(chunk)

        await streaming_client.close()
        await client.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
