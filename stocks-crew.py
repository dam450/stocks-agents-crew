# IMPORTS
import os
from datetime import datetime, timedelta
import yfinance as yf
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchResults
import streamlit as st


# YAHOO FINANCE TOOL
def fetch_stock_price(ticket):
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    stock = yf.download(
        tickers=ticket,
        start=start_date,
        end=end_date,
    )
    return stock


yahoo_finance_tool = Tool(
    name="Yahoo Finance Tool",
    description="Fetches stocks prices for {ticket} from the last year about a specific company from Yahoo Finance API",
    func=lambda ticket: fetch_stock_price(ticket),
)

# IMPORT OPENAI LLM - GPT
os.environ["OPENAI_API_KEY"] = st.secrets["OpenAI_key"]
llm = ChatOpenAI(model="gpt-3.5-turbo")

stockPriceAnalyst = Agent(
    role="Senior stock price Analyst",
    goal="Find the {ticket} stock price and analyses trends",
    backstory="""You're highly experienced in analyzing the price of an specific stock
    and make predictions about its future price.""",
    verbose=True,
    llm=llm,
    max_iter=5,
    memory=True,
    tools=[yahoo_finance_tool],
    allow_delegation=False,
)

# CREATE TASK STOCK_PRICE
getStockPrice = Task(
    description="Analyze the stock {ticket} price history and create a trend analyses of up, down or sideways",
    expected_output="""Specify the current trend stock price - up, down or sideways. 
    eg. stock= 'APPL, price UP' """,
    agent=stockPriceAnalyst,
)

# IMPORTANT SEARCH TOOL [DUCKDUCKGOSEARCHRESULTS]
search_tool = DuckDuckGoSearchResults(backend="news", num_results=10)

# CREATE AGENT NEWS_ANALYST
newsAnalyst = Agent(
    role="Stock News Analyst",
    goal="""Create a short summary of the market news related to the stock {ticket} company. Specify the current trend - up, down or sideways with
    the news context. For each request stock asset, specify a numbet between 0 and 100, where 0 is extreme fear and 100 is extreme greed.""",
    backstory="""You're highly experienced in analyzing the market trends and news and have tracked assest for more then 10 years.

    You're also master level analyts in the tradicional markets and have deep understanding of human psychology.

    You understand news, theirs tittles and information, but you look at those with a health dose of skepticism. 
    You consider also the source of the news articles. """,
    verbose=True,
    llm=llm,
    max_iter=10,
    memory=True,
    tools=[search_tool],
    allow_delegation=False,
)

# CREATE TASK NEWS
get_news = Task(
    description=f"""Take the stock and always include BTC to it (if not request).
    Use the search tool to search each one individually. 

    The current date is {datetime.now()}.

    Compose the results into a helpfull report.""",
    expected_output="""A summary of the overall market and one sentence summary for each request asset. 
    Include a fear/greed score for each asset based on the news. Use format:
    <STOCK ASSET>
    <SUMMARY BASED ON NEWS>
    <TREND PREDICTION>
    <FEAR/GREED SCORE> """,
    agent=newsAnalyst,
)

# CREATE STOCK ANALYST WRITER
stockAnalystWriter = Agent(
    role="Senior Stock Analyts Writer",
    goal="""Analyze the trends price and news and write an insighfull compelling and informative 3 paragraph long newsletter based on the stock report and price trend. """,
    backstory="""You're widely accepted as the best stock analyst in the market. You understand complex concepts and create compelling stories
    and narratives that resonate with wider audiences. 

    You understand macro factors and combine multiple theories - eg. cycle theory and fundamental analyses. 
    You're able to hold multiple opinions when analyzing anything. """,
    verbose=True,
    llm=llm,
    max_iter=5,
    memory=True,
    allow_delegation=True,
)

# CREATE TASK TO WRITE ANALISYS
writeAnalyses = Task(
    description="""Use the stock price trend and the stock news report to create an analyses and write the newsletter about the {ticket} company
    that is brief and highlights the most important points.
    Focus on the stock price trend, news and fear/greed score. What are the near future considerations?
    Include the previous analyses of stock trend and news summary. """,
    expected_output="""An eloquent 3 paragraphs newsletter formated as markdown in an easy readable manner. It should contain:

    - 3 bullets executive summary 
    - Introduction - set the overall picture and spike up the interest
    - main part provides the meat of the analysis including the news summary and fead/greed scores
    - summary - key facts and concrete future trend prediction - up, down or sideways. """,
    agent=stockAnalystWriter,
    context=[getStockPrice, get_news],
)

# CREATE CREW
crew = Crew(
    agents=[stockPriceAnalyst, newsAnalyst, stockAnalystWriter],
    tasks=[getStockPrice, get_news, writeAnalyses],
    verbose=2,
    process=Process.hierarchical,
    full_output=True,
    share_crew=False,
    manager_llm=llm,
    max_iter=15,
)

# streamlit web app
with st.sidebar:
    st.header("Informe a ação para pesquisa:")

    with st.form(key="research_form"):
        topic = st.text_input("ticker")
        submit_button = st.form_submit_button(label="pesquisar")

if submit_button:
    if not topic:
        st.error("Por favor, informe a ação.")
    else:
        results = crew.kickoff(inputs={"ticket": topic})

        st.subheader("Resultado da pesquisa:")
        st.write(results["final_output"])
