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

# 安全導入 Google AI
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

# 🤖 混合智能解析上傳區
with st.expander("📂 點擊這裡：上傳任一基金月報/股息紀錄 PDF（智能自動解析）", expanded=True):
    uploaded_file = st.file_uploader("請上傳任意基金 PDF 檔案", type=["pdf"])
    
    if uploaded_file is not None and PDF_SUPPORT:
        with st.spinner("⚡ 系統正在讀取並智能解析 PDF 文件中..."):
            # 1. 提取 PDF 文字
            text_content = ""
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    for p in range(min(len(pdf.pages), 5)):
                        extracted = pdf.pages[p].extract_text()
                        if extracted:
                            text_content += extracted + "\n"
            except Exception:
                pass

            parsed_by_ai = False
            gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")

            # 2. 嘗試 第一 & 第二層：AI 智能解析
            if gemini_api_key and GEMINI_SUPPORT:
                for target_model in ["gemini-1.5-flash", "gemini-1.5-pro"]:
                    try:
                        client = genai.Client(api_key=gemini_api_key)
                        prompt = f"""
                        閱讀以下基金文件，輸出JSON格式：
                        {{"fund_name_zh": "名稱", "fund_isin": "ISIN", "duration": 數字, "cash": 數字, "roc": 數字, "ter": 數字, "rating": "評級", "summary": "點評"}}
                        內文：{text_content[:4000]}
                        """
                        response = client.models.generate_content(
                            model=target_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(response_mime_type="application/json"),
                        )
                        cleaned_json = re.sub(r'```json\s*|\s*
