"""Extension page."""

import os
import streamlit as st
from aic_core.streamlit.page import AICPage
from pydantic_graph import Graph
from extendable_agents.graph.feedly_filter import (
    FeedlyStateWithTokens,
    GetNews,
    LabelNews,
    MarkNews,
)


class FeedlyFilterPage(AICPage):
    """Feedly Filter Page."""

    def filter_news(
        self, max_count: int, category: str, feedly_token: str, openai_api_key: str
    ) -> dict:
        """Filter news."""
        state = FeedlyStateWithTokens(
            feedly_token=feedly_token, openai_api_key=openai_api_key
        )
        feedly_graph = Graph[FeedlyStateWithTokens](
            nodes=[GetNews, LabelNews, MarkNews]
        )
        result = feedly_graph.run_sync(
            GetNews(
                max_count=max_count,
                category=category,
            ),
            state=state,
        )
        if result.output is None:
            return {}
        return result.output

    def run(self) -> None:
        """Run the page."""
        st.title("Feedly Filter")
        openai_api_key = st.sidebar.text_input(
            "OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", "")
        )
        st.write(
            "This tool reads news titles from your selected category and marks "
            "the uninteresting ones as read. It's recommended to first "
            "customise the prompt in the `FeedlyPrompt` on the `Custom Agent` "
            "page. Get your feedly token from https://feedly.com/i/console"
        )
        feedly_token = st.text_input("Feedly Token", type="password")
        news_category = st.text_input("News Category", value="AI")
        max_count = st.number_input("Max Count", min_value=1, max_value=500, value=10)
        if st.button("Filter"):
            if feedly_token and news_category:
                result = self.filter_news(
                    max_count, news_category, feedly_token, openai_api_key
                )
                st.dataframe(result)
            else:
                st.write("Please enter the Feedly token and news category.")


FeedlyFilterPage().run()
