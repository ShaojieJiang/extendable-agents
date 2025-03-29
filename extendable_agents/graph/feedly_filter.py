"""Pydantic Graph for filtering news from Feedly."""

from __future__ import annotations
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from aic_core.agent.agent import AgentConfig
from aic_core.agent.agent import AgentFactory
from aic_core.mcp.feedly.server import get_feedly_news
from pydantic import BaseModel
from pydantic import Field
from pydantic_ai import Agent
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
        news = get_feedly_news(self.max_count, self.category, ctx.state.feedly_token)
        for article in news:
            ctx.state.titles.append(article["title"])
            ctx.state.ids.append(article["id"])

        return LabelNews()


@dataclass
class LabelNews(BaseNode[FeedlyStateWithTokens]):
    """Label the news based on the title."""

    batch_size: int = 50

    def prepare_prompt(self, titles: list[str]) -> str:
        """Prepare the prompt for the label news."""
        return "Label the interestingness of these news titles: \n* " + "\n* ".join(
            titles
        )

    def extract_tool_args(self, messages: list[ModelMessage]) -> list[dict]:
        """Extract the tool calls from the messages."""
        results = []
        for msg in messages:
            if isinstance(msg, ModelResponse) and isinstance(
                msg.parts[0], ToolCallPart
            ):
                results.extend([part.args_as_dict() for part in msg.parts])  # type: ignore[union-attr]
        return results

    async def agent_run(self, agent: Agent, titles: list[str]) -> list[bool]:
        """Run the agent to label the news."""
        uninteresting = []
        result = await agent.run(self.prepare_prompt(titles))
        tool_args = self.extract_tool_args(result.new_messages())
        data = [Interestingness(**args) for args in tool_args]
        for item in data:
            uninteresting.append(item.uninteresting)

        return uninteresting

    async def run(self, ctx: GraphRunContext[FeedlyStateWithTokens]) -> MarkNews:  # noqa: D102
        agent_config = AgentConfig.from_hub(HF_REPO_ID, "FeedlyPrompt")
        agent_config.result_type = [Interestingness.__name__]
        agent_factory = AgentFactory(agent_config)
        agent = agent_factory.create_agent(api_key=ctx.state.openai_api_key)
        # agent.result_type = Interestingness  # type: ignore[assignment]

        for i in range(0, len(ctx.state.titles), self.batch_size):
            titles = ctx.state.titles[i : i + self.batch_size]
            uninteresting = await self.agent_run(agent, titles)
            ctx.state.uninteresting.extend(uninteresting)

        return MarkNews()


@dataclass
class MarkNews(BaseNode[FeedlyStateWithTokens]):
    """Mark uninteresting news as read."""

    async def run(self, ctx: GraphRunContext[FeedlyStateWithTokens]) -> End[dict]:  # type: ignore[override] # noqa: D102
        # for id, uninteresting in zip(
        #     ctx.state.ids, ctx.state.uninteresting, strict=True
        # ):
        #     if uninteresting:
        #         mark_as_read(id, ctx.state.feedly_token)
        result = asdict(ctx.state)
        result.pop("feedly_token")
        result.pop("openai_api_key")
        return End(result)
