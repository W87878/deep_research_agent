# Deep Research AI Agent

## 功能
- 自動爬取科技新聞
- 使用 LangChain 與 OpenAI 做問答
- FastAPI WebSocket 即時串流回答

## 快速開始

### 1. 安裝套件
```bash
pip install -r requirements.txt
```

### 2. 設定環境變數
建立 `.env` 檔案，內容如下：

```env
OPENAI_API_KEY=your_key_here
```

或直接在 CLI 中執行：
```bash
export OPENAI_API_KEY=your_key_here
```

### 3. 執行伺服器
```bash
python main.py
```

預設會啟動在 `ws://localhost:8000/ws/deepresearch`

### 4. 前端頁面
若你已建立 `frontend.html` 前端，可使用 VSCode 的 Live Server 外掛打開(使用 VSCode Live Server 或其他即時刷新工具時，頁面可能會自動刷新，影響測試流程。
建議改用瀏覽器直接打開本地 HTML 檔案（file:/// 路徑），或使用不會自動刷新的 HTTP 伺服器（例如 python3 -m http.server）避免自動刷新。):
```bash
# 或手動開啟 HTML 檔案
open frontend.html
```

## 範例對話
目前支援的對話範例：
```txt
我想知道最近關於生成式AI的新聞大概有哪些?       => NEWS
```

## 聯絡作者
Steve Wang | 2025
