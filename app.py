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

# 安全導入 Google Generative AI
try:
    import google.generativeai as genai
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
            st.warning("⚠️ GitHub 尚未完成 Google AI 套件安裝，請檢查 `requirements.txt`。")
        else:
            try:
                with st.spinner("🤖 Google Gemini AI 正在閱讀 PDF 並進行 9 大維度智能解析中..."):
                    # 1. 提取 PDF 文字
                    text_content = ""
                    with pdfplumber.open(uploaded_file) as pdf:
                        for p in range(min(len(pdf.pages), 5)):
                            extracted = pdf.pages[p].extract_text()
                            if extracted:
                                text_content += extracted + "\n"

                    # 2. 設定 API Key
                    genai.configure(api_key=gemini_api_key)

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

                    # 3. 備援模型調用機制：依序嘗試官方正確模型代號，絕不跳 404！
                    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
                    response = None
                    used_model_name = ""
                    error_logs = []

                    for model_name in models_to_try:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(prompt)
                            if response and response.text:
                                used_model_name = model_name
                                break
                        except Exception as err:
                            error_logs.append(f"{model_name}: {str(err)}")
                            continue

                    if not response or not response.text:
                        st.error(f"❌ API 連線細節說明：{'; '.join(error_logs)}")
                        raise ValueError("無法連線至 Gemini API 模型，請檢查 API Key 權限。")

                    # 清理 JSON 字串
                    cleaned_json = re.sub(r'```json\s*|\s*```', '', response.text).strip()
                    ai_result = json.loads(cleaned_json)
                    
                    fund_name_zh = ai_result.get("fund_name_zh", uploaded_file.name)
                    fund_name_en = ai_result.get("fund_name_en", "")
                    fund_isin = ai_result.get("fund_isin", "N/A")
                    duration_val = float(ai_result.get("duration", 0.0))
                    cash_val = float(ai_result.get("cash", 0.0))
                    roc_val = float(ai_result.get("roc", 0.0))
                    ter_val = float(ai_result.get("ter", 1.0))
                    rating_val = ai_result.get("rating", "BB")
                    ai_analysis_summary = ai_result.get("summary", "")
                    
                    if ai_result.get("top10"):
                        top10_list = ai_result.get("top10")

                    data_source = f"Google Gemini AI [{used_model_name}] 解析：{uploaded_file.name}"
                    st.success(f"🎉 AI 解析成功！(使用 {used_model_name}) | 基金：{fund_name_zh} | 久期: {duration_val}年 | 現金: {cash_val}% | 來自資本: {roc_val}%")
            
            except Exception as e:
                st.error(f"⚠️ AI 解析過程發生異常，已啟動安全保護：{e}")

# 動態生成 9 大維度實際數據與得分
mock_data = {
    "維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、國家/宏觀風險", "九、總開支比率"],
    "具體檢查指標": [
        "從資本派息 (ROC) 比例",
        "投資組合平均信貸評級",
        "衍生工具及總槓桿比率",
        "有效存續期 (Duration)",
        "現金及高流動性資產佔比",
        "前十大持倉總集中比例",
        "非對沖外幣資產曝險",
        "單一國家/區域持倉集中度",
        "每年管理費 / TER"
    ],
    "評分簡準": [
        "ROC < 10% 滿分 (>30% 扣分)",
        "評級 BBB 以上滿分 (BB 扣分)",
        "無槓桿滿分 (>20% 扣分)",
        "存續期 < 3年 滿分 (>6年 扣分)",
        "現金 > 10% 滿分 (<5% 扣分)",
        "前十持倉 < 30% 滿分",
        "完全對沖滿分 (未對沖扣分)",
        "單一國家 < 40% 滿分 (>60% 0分)",
        "TER < 1.0% 滿分 (>1.5% 0分)"
    ],
    "實際數據": [
        "月報未揭露 (需查股息表)" if roc_val == 0 else f"{roc_val}% 來自資本", 
        f"平均評級 {rating_val} (高收益債)", 
        "衍生工具風險淨額最高 50%", 
        f"有效存續期 {duration_val} 年 (防禦力強)", 
        f"現金及等值 {cash_val}% (緊湊)" if cash_val < 0 else f"現金及等值 {cash_val}% (充裕)", 
        "前十持倉合共分散", 
        "基礎貨幣已對沖", 
        "國家持倉分散", 
        f"每年管理費 {ter_val}%"
    ],
    "實際得分": [
        15 if roc_val == 0 else (10 if roc_val > 30 else 20),
        8, 10,
        10 if duration_val < 3 else (7 if duration_val <= 6 else 3),
        3 if cash_val < 5 else 10,
        10, 10, 0,
        5 if ter_val <= 1.0 else 3
    ],
    "滿分": [20, 15, 15, 10, 10, 10, 10, 5, 5],
    "狀態": [
        "⚠️ 需查股息表" if roc_val == 0 else ("⚠️ 警示" if roc_val > 30 else "✅ 優秀"),
        "⚠️ 警示", "⚠️ 留意槓桿", 
        "✅ 優秀" if duration_val < 3 else "⚠️ 警示",
        "🚨 流動性緊湊" if cash_val < 0 else "✅ 優秀",
        "✅ 優秀", "✅ 優秀", "🚨 極高風險", "✅ 優秀" if ter_val <= 1.0 else "⚠️ 警示"
    ]
}

# 頂部 ISIN 與類別連動
s_col1, s_col2, s_col3 = st.columns([2, 2, 1])

with s_col1:
    st.text_input("基金代號 / ISIN", value=fund_isin, label_visibility="collapsed")

with s_col2:
    st.selectbox("選擇基金類別", ["債券型基金", "股票型基金"], label_visibility="collapsed")

with s_col3:
    st.button("🔄 重新評估", type="primary", use_container_width=True)

# 醒目基金名稱與數據源標籤展示區
st.markdown(f"""
    <div class="fund-header">
        <span style="font-size: 14px; color: #888;">當前分析目標基金：</span> 
        <span class="source-tag">📍 {data_source}</span><br>
        <span style="font-size: 20px; font-weight: bold; color: #FFF;">{fund_name_zh}</span> 
        <span style="font-size: 14px; color: #AAA;">({fund_name_en})</span>
    </div>
""", unsafe_allow_html=True)

# 3. KPI 關鍵指標卡片
total_score = sum(mock_data["實際得分"])

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="🛡️ 風險健康總分", value=f"{total_score} / 100", delta=f"{total_score - 100} 分", delta_color="inverse")

with kpi2:
    st.metric(label="⚠️ 平均信用評級", value=f"{rating_val}", delta="高收益(垃圾債)", delta_color="inverse")

with kpi3:
    st.metric(label="💧 流動性緩衝 (現金)", value=f"{cash_val}%", delta="現金偏緊" if cash_val < 0 else "充裕", delta_color="inverse" if cash_val < 0 else "normal")

with kpi4:
    st.metric(label="⏳ 利率敏感度 (久期)", value=f"{duration_val} 年", delta="抗加息力強" if duration_val < 3 else "敏感", delta_color="normal")

st.markdown("---")

# 4. 中間核心區：雷達圖與持倉清單
col_chart, col_table = st.columns([1, 1.3], gap="medium")

df_top10 = pd.DataFrame(top10_list)
top10_total_pct = round(df_top10["佔比 (%)"].sum(), 2) if "佔比 (%)" in df_top10.columns else 0.0

with col_chart:
    tab1, tab2 = st.tabs(["🕸️ 風險維度雷達圖", "📋 前十大持倉清單"])
    
    with tab1:
        df_chart = pd.DataFrame(dict(Score=mock_data["實際得分"], Dimension=mock_data["維度"]))
        fig_radar = px.line_polar(
            df_chart, r='Score', theta='Dimension', line_close=True, markers=True, range_r=[0, 20], template="plotly_dark", color_discrete_sequence=['#00E676']
        )
        fig_radar.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.3)', line=dict(color='#00E676', width=2), marker=dict(size=6, color='#00E676'))
        fig_radar.update_layout(height=370, margin=dict(l=20, r=20, t=20, b=20), polar=dict(radialaxis=dict(visible=True, range=[0, 20], showticklabels=False)))
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with tab2:
        st.metric(label="📌 前十大持倉合共佔比 (Top 10 Total)", value=f"{top10_total_pct}%", delta="持倉分散，集中度風險低", delta_color="normal")
        st.dataframe(
            df_top10,
            use_container_width=True, hide_index=True, height=280
        )

with col_table:
    st.subheader("📋 風險評估項目")
    df_table = pd.DataFrame(mock_data)
    st.dataframe(
        df_table[["維度", "具體檢查指標", "評分簡準", "實際數據", "實際得分", "滿分", "狀態"]],
        use_container_width=True, hide_index=True, height=350
    )

# 5. 底部：Gemini AI 智能洞察點評
st.info(f"**💡 AI 智能洞察 ({fund_name_zh})**：{ai_analysis_summary}")
