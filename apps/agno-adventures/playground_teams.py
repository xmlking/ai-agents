from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from pydantic import BaseModel


class StockAnalysis(BaseModel):
    symbol: str
    company_name: str
    analysis: str


stock_searcher = Agent(
    name="Stock Searcher",
    model=OpenAIChat("gpt-4o"),
    role="Searches the web for information on a stock.",
    tools=[YFinanceTools()],
)

web_searcher = Agent(
    name="Web Searcher",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    role="Searches the web for information on a company.",
)


agent_team = Team(
    name="Stock Team",
    mode="coordinate",
    model=OpenAIChat("gpt-4o"),
    members=[stock_searcher, web_searcher],
    instructions=[
        "First, search the stock market for information about a particular company's stock.",
        "Then, ask the web searcher to search for wider company information.",
    ],
    # response_model=StockAnalysis,
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
)
embers_responses = (True,)


app = Playground(
    teams=[agent_team],
).get_app()

if __name__ == "__main__":
    serve_playground_app("playground_teams:app", reload=True)

## Ask
# Write a report on the Apple stock.
# Pull up the previous report again.
