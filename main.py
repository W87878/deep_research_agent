import re
from fastapi import FastAPI, WebSocket
from memory.chat_memory import get_memory
from langchain_openai import OpenAI
from dotenv import load_dotenv 
from starlette.websockets import WebSocketDisconnect
from agents.crawler_agent import crawler_agent
from agents.summary_agent import summarize_crawled_data_stream
from intent.crawler_intent import detect_crawl_task
import time

load_dotenv()  # 載入環境變數
import os
# 確保已經設定了 OPENAI_API_KEY 環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 取得環境變數的值
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
user_data_dir = '/Users/steve.wang/Library/Application\\ Support/Google/Chrome'
profile_directory = 'Profile 1' # Profile 1, Profile 2, Default, etc.
set_profile = False  # 是否使用特定的 Chrome profile
headless = True  # 是否以無頭模式運行 Chrome
max_results = 10  # 爬取的最大結果數量

app = FastAPI()

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)



@app.websocket("/ws/deepresearch")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # memory = get_memory()
    results = []
    try:
        while True:
            user_input = await websocket.receive_text()
            print("🟢 Received user input:", user_input)
            async def stream_agent(agent_func):
                try:
                    async for chunk in agent_func(user_input, results):
                        print(">> Streaming chunk:", repr(chunk))  # 👈 Log token
                        try:
                            await websocket.send_text(chunk)
                        except RuntimeError as e:
                            print("Client disconnected while streaming:", e)
                            break
                except WebSocketDisconnect:
                    print("🟠 Client disconnected, stop streaming")
                except Exception as e:
                    print("🔴 Unexpected error:", e)
                    try:
                        await websocket.send_text(f"[錯誤] {str(e)}")
                    except RuntimeError:
                        print("🟠 Cannot send error message, websocket closed")

            # 使用者意圖拆解
            intent_result = detect_crawl_task(user_input)
            print("使用者意圖:", intent_result)
            # 爬蟲工具調用 － 爬取網路資料
            results = await crawler_agent(intent_result, user_data_dir, profile_directory)
            time.sleep(5)  # 等待爬蟲完成
            if not results:
                print("⚠️ 沒有找到相關資料")
                await websocket.send_text("沒有找到相關資料")
                continue
            print("爬蟲結果:", repr(results))
            await stream_agent(summarize_crawled_data_stream)
            
    except WebSocketDisconnect:
        print("客戶端中斷連線")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# This code sets up a FastAPI application with a WebSocket endpoint.    