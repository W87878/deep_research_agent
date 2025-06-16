import sys
sys.stdout.reconfigure(encoding='utf-8')

import traceback
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv 
import json
import re
load_dotenv()  # 載入環境變數
import os
# 確保已經設定了 OPENAI_API_KEY 環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 取得環境變數的值
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)


def detect_crawl_task(user_input: str) -> dict:
    system_prompt = "你是一個語句理解器，請依照 JSON 格式解析使用者輸入的意圖與主題關鍵詞。"
    user_prompt = f"""
        你是一個語句理解器，請判斷使用者的輸入屬於哪一類資訊查詢需求，並同時擷取主題關鍵詞。請以 JSON 格式回傳結果，格式如下：

        {{
        "intent": "NEWS" | "PAPER" | "BLOG" | "PRODUCT" | "OTHER",
        "query": "使用者想查的主題或關鍵詞"
        }}

        請參考以下範例進行判斷與回傳：

        ---
        輸入：找幾篇有關 AI 趨勢的新聞  
        輸出：
        {{
        "intent": "NEWS",
        "query": "AI 趨勢"
        }}

        ---
        輸入：有哪些論文在探討生成式 AI 的倫理問題？  
        輸出：
        {{
        "intent": "PAPER",
        "query": "生成式 AI 倫理"
        }}

        ---
        輸入：有沒有寫過 LangChain 的部落格？  
        輸出：
        {{
        "intent": "BLOG",
        "query": "LangChain"
        }}

        ---
        輸入：Notion AI 跟 ChatGPT 哪個好？  
        輸出：
        {{
        "intent": "PRODUCT",
        "query": "Notion AI vs ChatGPT"
        }}

        ---
        輸入：你會唱歌嗎？  
        輸出：
        {{
        "intent": "OTHER",
        "query": ""
        }}

        ---
        輸入：「{user_input}」  
        輸出：
    """
    try:
        system_prompt = system_prompt.encode('utf-8').decode('utf-8')  # 強制 UTF-8 處理
        user_prompt = user_prompt.encode('utf-8').decode('utf-8')  # 強制 UTF-8 處理
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        content = response.content.strip()  # 這才是文字內容
        print("LLM 回傳內容:", content)  # Log the raw response for debugging
        result = json.loads(content)
        # 確保意圖合法
        if result.get("intent") not in ["NEWS", "PAPER", "BLOG", "PRODUCT"]:
            result["intent"] = "OTHER"
        return result
    except Exception as e:
        traceback.print_exc()  # 印出完整錯誤堆疊
        return {
            "intent": "OTHER",
            "query": "",
            "error": str(e)
        }
