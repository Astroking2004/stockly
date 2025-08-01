import os
import yfinance as yf
import gradio as gr
import matplotlib.pyplot as plt
from agents import Agent, Runner

from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define agent for recommendations
agent = Agent(name="Stockly Assistant", instructions="You are a financial assistant. Analyze price trends and provide plain English recommendations.")


def fetch_data(ticker: str, period: str = "1mo"):
    ticker_obj = yf.Ticker(ticker)
    data = ticker_obj.history(period=period)
    # Fetch current price
    try:
        current_price = ticker_obj.info.get('regularMarketPrice')
    except Exception:
        current_price = None
    return data, current_price

def plot_trend(data):
    plt.figure(figsize=(10, 4))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title('Price Trend')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.tight_layout()
    plt.savefig('trend.png')
    plt.close()
    return 'trend.png'


import asyncio

async def get_recommendation(ticker: str, data):
    prompt = f"Analyze the following price data for {ticker} and provide a plain English recommendation: {data['Close'].tolist()}"
    # Use correct async runner method
    result = await Runner.run(agent, prompt)
    return result.final_output



async def app(ticker: str, period: str = "1mo"):
    data, current_price = fetch_data(ticker, period)
    img_path = plot_trend(data)
    recommendation = await get_recommendation(ticker, data)
    price_str = f"Current Price: {current_price}" if current_price is not None else "Current Price: N/A"
    return recommendation, img_path, price_str



gui = gr.Interface(
    fn=app,
    inputs=[gr.Textbox(label="Ticker (e.g. AAPL, BTC-USD)"), gr.Textbox(label="Period", value="1mo")],
    outputs=[gr.Textbox(label="Recommendation"), gr.Image(label="Trend"), gr.Textbox(label="Current Price")],
    title="Stockly: Price Trends & Recommendations",
    description="Enter a stock or crypto ticker to get price trends, current price, and AI-powered recommendations.",
    allow_flagging="never",
    concurrency_limit=None,
)

gui.launch()
