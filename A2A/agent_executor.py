from a2a.helpers import new_task_from_user_message, new_text_artifact, new_text_message

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from a2a.types.a2a_pb2 import TaskArtifactUpdateEvent, TaskState, TaskStatus, TaskStatusUpdateEvent

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv

load_dotenv()

class HelloWorldAgent:
    """Hello World Agent"""

    def __init__(self):

        model = init_chat_model("openai:gpt-4.1-mini")

        self.agent = create_agent(
            model=model,
            system_prompt=(
                "You are a helpful research assistant."
            ),
        )


    async def invoke(self, user_input: str) -> str:
        """Invoke the Hello World agent to generate a response."""
        response = await self.agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        })

        return response["messages"][-1].content


class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation"""

    def __init__(self) -> None:
        self.agent = HelloWorldAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute the agent process and enqueue the final response"""

        task = context.current_task or new_task_from_user_message(
            context.message
        )

        await event_queue.enqueue_event(task)

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(
                    state=TaskState.TASK_STATE_WORKING,
                    message=new_text_message('Processing request...'),
                ),
            )
        )

        result = await self.agent.invoke(context.message.parts[0].text)

        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                artifact=new_text_artifact(name='result', text=result),
            )
        )

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Raise exception as cancel is not supported."""
        raise Exception('Cancel is not Supported')
