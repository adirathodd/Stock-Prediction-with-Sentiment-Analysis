from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from stock import Stock
import asyncio
import pandas as pd

app = FastAPI()


# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app runs on this origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

origins = [
    "http://localhost:3000",
    "localhost:3000"
]


class StockRequest(BaseModel):
    ticker: str
    window: int

async def send_progress(websocket: WebSocket, message: str, progress: int):
    await websocket.send_json({"message": message, "progress": progress})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            
            data = await websocket.receive_json()
            ticker = data['ticker'].upper()
            
            await send_progress(websocket, "Fetching data...", 10)
            await asyncio.sleep(0.2)

            stock = Stock(ticker)
            stock.create(3)

            await send_progress(websocket, "Performing sentiment analysis...", 30)

            stock.sentiment_analysis()

            await send_progress(websocket, "Predicting...", 80)
            await asyncio.sleep(0.5)

            stock.predict()

            data = stock.get_data()
            data = data.applymap(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)

            await send_progress(websocket, "Completed", 100)
            await websocket.send_json({"data": data.to_dict(orient="records"), "prediction": stock.prediction})
    except WebSocketDisconnect:
        print("Client disconnected")

# Run the app using: uvicorn main:app --reload