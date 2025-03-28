"""Pydantic Graph for filtering news from Feedly."""

from __future__ import annotations
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from aic_core.agent.agent import AgentConfig
from aic_core.agent.agent import AgentFactory
from feedly.api_client.session import FeedlySession
from feedly.api_client.stream import StreamOptions
from pydantic import BaseModel
from pydantic import Field
from pydantic_ai.messages import ModelMessage
from pydantic_ai.messages import ModelResponse
from pydantic_ai.messages import ToolCallPart
from pydantic_graph import BaseNode
from pydantic_graph import End
from pydantic_graph import GraphRunContext
from extendable_agents.constants import HF_REPO_ID


class Interestingness(BaseModel):
    """Interestingness of a news."""

    title: str = Field(..., description="The title of the news.")
    uninteresting: bool = Field(..., description="Whether the news is uninteresting.")


@dataclass
class FeedlyState:
    """State for the Feedly filter."""

    titles: list[str] = field(default_factory=list)
    uninteresting: list[bool] = field(default_factory=list)
    ids: list[str] = field(default_factory=list)


@dataclass
class FeedlyStateWithTokens(FeedlyState):
    """State for the Feedly filter with tokens."""

    feedly_token: str = "feedly_token"
    openai_api_key: str = "openai_api_key"


@dataclass
class GetNews(BaseNode[FeedlyStateWithTokens]):
    """Get the latest news from Feedly."""

    max_count: int = 10
    category: str = "AI"

    async def run(  # noqa: D102
        self,
        ctx: GraphRunContext[FeedlyStateWithTokens],
    ) -> LabelNews:
        session = FeedlySession(auth=ctx.state.feedly_token)

        category_name = session.user.user_categories.get(self.category)

        for article in category_name.stream_contents(
            options=StreamOptions(max_count=self.max_count)
        ):
            ctx.state.titles.append(article["title"])
            ctx.state.ids.append(article["id"])

        return LabelNews()


@dataclass
class LabelNews(BaseNode[FeedlyStateWithTokens]):
    """Label the news based on the title."""

    def prepare_prompt(self, ctx: GraphRunContext[FeedlyStateWithTokens]) -> str:
        """Prepare the prompt for the label news."""
        return "Label the interestingness of these news titles: \n* " + "\n* ".join(
            ctx.state.titles
        )

    def extract_tool_args(self, messages: list[ModelMessage]) -> list[dict]:
        """Extract the tool calls from the messages."""
        results = []
        for msg in messages:
            if isinstance(msg, ModelResponse) and isinstance(
                msg.parts[0], ToolCallPart
            ):
                results.extend([part.args_as_dict() for part in msg.parts])
        return results

    async def run(self, ctx: GraphRunContext[FeedlyStateWithTokens]) -> MarkNews:  # noqa: D102
        agent_config = AgentConfig.from_hub(HF_REPO_ID, "FeedlyAgent")
        agent_factory = AgentFactory(agent_config)
        agent = agent_factory.create_agent(api_key=ctx.state.openai_api_key)
        agent.result_type = Interestingness
        result = await agent.run(self.prepare_prompt(ctx))
        tool_args = self.extract_tool_args(result.new_messages())
        data = [Interestingness(**args) for args in tool_args]
        for item in data:
            ctx.state.uninteresting.append(item.uninteresting)
        return MarkNews()


@dataclass
class MarkNews(BaseNode[FeedlyStateWithTokens]):
    """Mark uninteresting news as read."""

    async def run(self, ctx: GraphRunContext[FeedlyStateWithTokens]) -> End[dict]:  # noqa: D102
        # TODO: mark uninteresting news as read
        result = asdict(ctx.state)
        result.pop("feedly_token")
        result.pop("openai_api_key")
        return End(result)
