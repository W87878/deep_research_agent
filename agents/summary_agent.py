# agents/summary_agent.py
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from typing import List
from dotenv import load_dotenv 
import re
from langchain_openai import ChatOpenAI
import time

load_dotenv()

import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
from openai import AsyncOpenAI
openai = AsyncOpenAI(api_key=OPENAI_API_KEY)

def clean_crawled_text(text: str) -> str:
    # 移除控制符號與不可見字元
    text = re.sub(r"[\x00-\x1f\x7f\u200b\u200e\u202a-\u202e\u2060\ufffc]", "", text)
    return text

def truncate(text, max_chars=1000):
    return text[:max_chars]

async def summarize_crawled_data_stream(user_question: str, crawled_data: List[str]):
    print("crawled_data:", crawled_data)
    results = []
    static_llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0)
    for i, item in enumerate(crawled_data):
        small_summary_prompt = f"""
        爬取資料（第 {i+1} 筆）：
        {truncate(item['content'], 1000)}

        你是一位專業新聞記者，專門分析以上這篇新聞內容並做介紹。

        請根據以下新聞，整理出「3 到 5 個關鍵趨勢」，每個趨勢要包含：
        - 趨勢標題
        - 簡短說明（用白話整理幾句）
        - 產業影響（對科技、商業、人才、創作等的潛在影響）

        以下是格式示範：

        ---
        【趨勢 1：生成式AI進入企業流程自動化】
        說明：越來越多企業將生成式AI應用於客服、自動報告生成、行銷文案撰寫等工作流程，來提升效率與降低成本。
        產業影響：這將影響傳統人工作業的角色，推升AI工具的採購與整合需求，也讓企業IT部門需重新思考與AI協作的架構。

        ---
        【趨勢 2：AI助理成為知識工作者的標配】
        說明：像Claude、ChatGPT等生成式AI正在知識產業中快速普及，成為日常文件摘要、會議筆記、研究協助的工具。
        產業影響：知識密集產業（如法律、顧問、教育）的人力需求可能轉向更高階的策略與溝通能力，同時帶動AI工具教育需求。

        ---
        請以類似的方式整理以下新聞資料：

        新聞資料如下：
        {{
        "news":
            "title": "Amazon 推出 AI 優化物流路線，提升貨運效率",
            "content": "Amazon 近期開始使用生成式AI分析供應鏈資料，自動建議最適化路線以降低成本與延遲。該技術已應用於北美部分倉儲系統。",
            "url": "https://example.com/amazon-ai-logistics"
        }}
        """
        response = static_llm.invoke(small_summary_prompt)
        results.append(f"第 {i+1} 筆摘要：\n{response.content}")
        print(repr(response))
        time.sleep(0.1)  # 避免過快請求
    # print(repr(content))

    content = "\n\n".join(results)
    content = clean_crawled_text(content)
    # 整理最終的趨勢分析
    prompt = f"""
        你是一位產業科技分析師，根據以下多篇新聞摘要及使用者的問題，請整理出 3 到 5 個關鍵趨勢。

        每個趨勢請包含：
        - 趨勢標題
        - 簡短說明（2~3 句）
        - 潛在產業影響（如對企業、自動化、職缺、法規等）

        使用者問題：
        {user_question}

        爬取資料（共 {len(results)} 筆）：
        新聞摘要如下： 
        {content}
        請根據以上新聞摘要，回答使用者問題並整理出關鍵趨勢。
        注意：請避免使用過於專業的術語，並確保每個趨勢都能清楚解釋其背景與影響。
    """

    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    full_response = ''
    i = 0
    async for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        if delta != '':
            full_response += delta
            i += 1
            yield delta
