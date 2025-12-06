# FastAPI server example
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from core.lia_main import LiaMain

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
lia = LiaMain(api_key="doeM32W2so3ubfYYs673lmiOmUzwN15weKfB68bj")

@app.post("/api/chat")
async def chat(message: str):
    response = lia.process_input(message)
    return {"response": response}
