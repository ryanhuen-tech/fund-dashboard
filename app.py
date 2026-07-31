import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re

# 安全導入 pdfplumber
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# 安全導入 Google 最新 SDK (google-genai)
try:
    from google import genai
    from google.genai import types
    GEMINI_SUPPORT = True
except ImportError:
    GEMINI_SUPPORT = False

# 1. 網頁基本設定
st.set_page_config(
    page_title="智能基金風險評估系統", 
    page_icon="🛡️", 
    layout="wide"
)

# 自訂 CSS 樣式
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
    }
    .fund-header {
        background-color: #1E222D;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 5px solid #00E676;
        margin-bottom: 15px;
    }
    .source-tag {
        background-color: #00E676;
        color: #000;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# 預設數據範本
fund_name_zh = "富達基金 - 美元高收益基金"
fund_name_en = "Fidelity Funds - US High Yield Fund"
fund_isin = "LU0132282301"

roc_val = 0.0
duration_val = 2.8
cash_val = -0.40
rating_val = "BB-"
ter_val = 1.00
data_source = "預設範本 (富達 Z13)"
ai_analysis_summary = "該基金有效存續期為 2.8 年，現金比例為 -0.40%，每年管理費為 1.00%。持倉高度分散，但美國單一市場佔比達 79.60%，需留意區域集中風險。"

top10_list = [
    {"排名": 1, "持倉名稱": "UST BILLS 0% 07/30/26", "資產類別": "美國國庫券", "佔比 (%)": 3.02},
    {"排名": 2, "持倉名稱": "UST BILLS 0% 09/10/26", "資產類別": "美國國庫券", "佔比 (%)": 2.02},
    {"排名": 3, "持倉名稱": "DIRECTV HLDGS 9.25% 6/32", "資產類別": "通訊服務債", "佔比 (%)": 0.89},
    {"排名": 4, "持倉名稱": "VENTURE 9.875% 02/01/32", "資產類別": "能源債", "佔比 (%)": 0.88},
    {"排名": 5, "持倉名稱": "WULF COMPUTE 7.75% 10/30", "資產類別": "科技債", "佔比 (%)": 0.84},
    {"排名": 6, "持倉名稱": "NISSAN MOTOR 7.5% 7/17/30", "資產類別": "汽車債", "佔比 (%)": 0.82},
    {"排名": 7, "持倉名稱": "SWORD PURCH 8.25% 4/15/33", "資產類別": "工業債", "佔比 (%)": 0.82},
    {"排名": 8, "持倉名稱": "1261229 BC LTD 10% 4/32", "資產類別": "醫療債", "佔比 (%)": 0.80},
    {"排名": 9, "持倉名稱": "CARNIVAL CORP 6.125% 2/33", "資產類別": "休閒旅遊債", "佔比 (%)": 0.80},
    {"排名": 10, "持倉名稱": "OAK-EAGLE ACQUI 7.25% 7/33", "資產類別": "金融債", "佔比 (%)": 0.78},
]

# 2. 頂部工具列與 PDF 自動化解析區
st.title("🛡️ 智能基金風險評估系統")

# 🤖 Google Gemini AI 全自動解析上傳區
with st.expander("📂 點擊這裡：上傳任一基金月報/股息紀錄 PDF（Google Gemini AI 自動理解解析）", expanded=True):
    uploaded_file = st.file_uploader("請上傳任意基金 PDF 檔案", type=["pdf"])
    
    if uploaded_file is not None and PDF_SUPPORT:
        gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
        
        if not gemini_api_key:
            st.warning("⚠️ 未檢測到 Google Gemini API Key，請至 Streamlit 專案 Settings -> Secrets 設定 `GEMINI_API_KEY`。")
        elif not GEMINI_SUPPORT:
            st.warning("⚠️ GitHub 尚未完成 Google AI (google-genai) 套件安裝，請檢查 requirements.txt。")
        else:
            try:
                with st.spinner("🤖 Google Gemini AI 正在連線並智能解析 PDF..."):
                    # 1. 提取 PDF 文字
                    text_content = ""
                    with pdfplumber.open(uploaded_file) as pdf:
                        for p in range(min(len(pdf.pages), 5)):
                            extracted = pdf.pages[p].extract_text()
                            if extracted:
                                text_content += extracted + "\n"

                    # 2. 初始化 Client
                    client = genai.Client(api_key=gemini_api_key)

                    # 💡 自動獲取 API 允許存取的模型列表，排除 404 錯號！
                    available_models = []
                    try:
                        for m in client.models.list():
                            m_name = getattr(m, 'name', '') or str(m)
                            if 'gemini' in m_name:
                                available_models.append(m_name.replace('models/', ''))
                    except Exception:
                        pass

                    # 優先選擇 Flash 模型
                    selected_model = "gemini-1.5-flash"
                    for m_candidate in available_models:
                        if 'flash' in m_candidate:
                            selected_model = m_candidate
                            break
                    if not available_models and not selected_model:
                        selected_model = "gemini-1.5-flash"

                    prompt = f"""
                    你是一位頂尖的金融量化分析師。請閱讀以下基金報告或股息紀錄內容，精確提取關鍵數據並回傳 JSON 格式。
                    若內容未提及 ROC 派息來自資本，請將 roc 設為 0。
                    
                    請嚴格只輸出 JSON，格式如下：
                    {{
                        "fund_name_zh": "基金中文名稱",
                        "fund_name_en": "基金英文名稱",
                        "fund_isin": "ISIN代號",
                        "duration": 數字(存續期/久期，單位:年),
                        "cash": 數字(現金比例%，可為負數),
                        "roc": 數字(派息來自資本%，若無則0),
                        "ter": 數字(管理費/TER %),
                        "rating": "字串(如 BB-, BB, BBB, A)",
                        "summary": "一段100字內的智能洞察點評",
                        "top10": [
                            {{"排名": 1, "持倉名稱": "持倉1", "資產類別": "類別", "佔比 (%)": 數字}},
                            ... (最多10個)
                        ]
                    }}

                    基金文本內容：
                    {text_content[:6000]}
                    """

                    # 3. 調用自動選出的模型
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        ),
                    )

                    # 清理 JSON 字串
                    cleaned_json = re.sub(r'```json\s*|\s*
