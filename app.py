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
    .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
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

st.title("🛡️ 智能基金風險評估系統")

# 📚 定義兩隻基金的預設資料庫
PRESET_FUNDS = {
    "霸菱環球高收益債券基金": {
        "zh": "霸菱環球高收益債券基金",
        "en": "Barings Global High Yield Bond Fund",
        "isin": "IE00BFM0MQ22",
        "roc": 47.39,
        "duration": 2.58,
        "cash": 11.26,
        "rating": "BB",
        "ter": 1.33,
        "summary": "本基金為霸菱環球高收益債券基金。從資本派息比例較高 (47.39%)，需注意資本侵蝕風險；流動性緩衝 11.26% 相對充裕，有效存續期 2.58 年防禦力強。",
        "top10": [
            {"排名": 1, "持倉名稱": "現金及等值資產 (Cash Equivalents)", "資產類別": "現金/貨幣市場", "佔比 (%)": 11.26},
            {"排名": 2, "持倉名稱": "Bausch Health Companies Inc.", "資產類別": "醫療保健債", "佔比 (%)": 2.40},
            {"排名": 3, "持倉名稱": "Charter Communications Inc.", "資產類別": "通訊服務債", "佔比 (%)": 1.71},
            {"排名": 4, "持倉名稱": "First Quantum Minerals Ltd", "資產類別": "基本工業債", "佔比 (%)": 1.66},
            {"排名": 5, "持倉名稱": "Uniti Group Inc.", "資產類別": "通訊基礎設施債", "佔比 (%)": 1.46},
            {"排名": 6, "持倉名稱": "Radiology Partners", "資產類別": "醫療保健債", "佔比 (%)": 1.31},
            {"排名": 7, "持倉名稱": "LifePoint Health", "資產類別": "醫療保健債", "佔比 (%)": 1.27},
            {"排名": 8, "持倉名稱": "EchoStar", "資產類別": "衛星通訊債", "佔比 (%)": 1.25},
            {"排名": 9, "持倉名稱": "Herbalife Ltd.", "資產類別": "非必需消費債", "佔比 (%)": 1.10},
            {"排名": 10, "持倉名稱": "PRA Group", "資產類別": "金融服務債", "佔比 (%)": 1.06},
        ]
    },
    "富達基金 - 美元高收益基金": {
        "zh": "富達基金 - 美元高收益基金",
        "en": "Fidelity Funds - US High Yield Fund",
        "isin": "LU0132282301",
        "roc": 0.0,
        "duration": 2.8,
        "cash": -0.40,
        "rating": "BB-",
        "ter": 1.00,
        "summary": "本基金為富達美元高收益基金。派息 100% 來自淨可分派收益 (0% 來自資本)，派息品質優良；有效存續期 2.8 年，流動性現金佔比為 -0.40%。",
        "top10": [
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
    }
}

# 2. 頂部選擇區 (新增一鍵選單)
ctrl_col1, ctrl_col2 = st.columns([1, 1])

with ctrl_col1:
    selected_preset = st.selectbox("📌 快速選擇已建檔基金：", list(PRESET_FUNDS.keys()))

# 載入選擇的預設資料
curr_fund = PRESET_FUNDS[selected_preset]
fund_name_zh = curr_fund["zh"]
fund_name_en = curr_fund["en"]
fund_isin = curr_fund["isin"]
roc_val = curr_fund["roc"]
duration_val = curr_fund["duration"]
cash_val = curr_fund["cash"]
rating_val = curr_fund["rating"]
ter_val = curr_fund["ter"]
ai_analysis_summary = curr_fund["summary"]
top10_list = curr_fund["top10"]
data_source = f"預設資料庫: {fund_name_zh}"

# PDF 上傳解析區 (上傳新 PDF 時自動覆蓋)
with st.expander("📂 或點擊這裡：上傳新基金月報/股息紀錄 PDF (動態覆蓋)", expanded=False):
    uploaded_file = st.file_uploader("請上傳任意基金 PDF 檔案", type=["pdf"])
    
    if uploaded_file is not None and PDF_SUPPORT:
        text_content = ""
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for p in range(min(len(pdf.pages), 5)):
                    extracted = pdf.pages[p].extract_text()
                    if extracted: text_content += extracted + "\n"
        except Exception: pass

        parsed_by_ai = False
        gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")

        if gemini_api_key and GEMINI_SUPPORT:
            for target_model in ["gemini-1.5-flash", "gemini-1.5-pro"]:
                try:
                    client = genai.Client(api_key=gemini_api_key)
                    prompt = f"閱讀以下文件，輸出JSON: {{\"fund_name_zh\": \"名稱\", \"fund_isin\": \"ISIN\", \"duration\": 數字, \"cash\": 數字, \"roc\": 數字, \"ter\": 數字, \"rating\": \"評級\", \"summary\": \"點評\"}}\n內文：{text_content[:4000]}"
                    response = client.models.generate_content(model=target_model, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json"))
                    cleaned_json = re.sub(r'```json\s*|\s*```', '', response.text).strip()
                    ai_result = json.loads(cleaned_json)
                    fund_name_zh = ai_result.get("fund_name_zh", uploaded_file.name)
                    fund_isin = ai_result.get("fund_isin", fund_isin)
                    duration_val = float(ai_result.get("duration", duration_val))
                    cash_val = float(ai_result.get("cash", cash_val))
                    roc_val = float(ai_result.get("roc", roc_val))
                    ter_val = float(ai_result.get("ter", ter_val))
                    rating_val = ai_result.get("rating", rating_val)
                    ai_analysis_summary = ai_result.get("summary", "")
                    data_source = f"Gemini AI 解析：{uploaded_file.name}"
                    parsed_by_ai = True
                    break
                except Exception: continue

        if not parsed_by_ai:
            data_source = f"PDF 本地解析：{uploaded_file.name}"
            dur_match = re.search(r'(?:有效存續期|修訂存續期|久期|Duration)[^\d]*(-?[\d\.]+)', text_content)
            if dur_match: duration_val = float(dur_match.group(1))
            cash_match = re.search(r'(?:Cash\s*現金|現金及等值|Cash)[^\d\-]*(-?[\d\.]+)', text_content)
            if cash_match: cash_val = float(cash_match.group(1))

# 3. 動態生成 9 大維度數據
mock_data = {
    "維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、國家/宏觀風險", "九、總開支比率"],
    "具體檢查指標": ["從資本派息 (ROC) 比例", "投資組合平均信貸評級", "衍生工具及總槓桿比率", "有效存續期 (Duration)", "現金及高流動性資產佔比", "前十大持倉總集中比例", "非對沖外幣資產曝險", "單一國家/區域持倉集中度", "每年管理費 / TER"],
    "評分簡準": ["ROC < 10% 滿分 (>30% 扣分)", "評級 BBB 以上滿分 (BB 扣分)", "無槓桿滿分 (>20% 扣分)", "存續期 < 3年 滿分 (>6年 扣分)", "現金 > 10% 滿分 (<5% 扣分)", "前十持倉 < 30% 滿分", "完全對沖滿分 (未對沖扣分)", "單一國家 < 40% 滿分 (>60% 0分)", "TER < 1.0% 滿分 (>1.5% 0分)"],
    "實際數據": [
        f"{roc_val}% 來自資本", 
        f"平均評級 {rating_val} (高收益債)", 
        "衍生工具風險淨額最高 50%", 
        f"有效存續期 {duration_val} 年", 
        f"現金及等值 {cash_val}%", 
        "前十持倉分散", "基礎貨幣已對沖", "北美/美國佔比偏高", f"每年管理費 {ter_val}%"
    ],
    "實際得分": [
        20 if roc_val < 10 else (10 if roc_val > 30 else 15),
        8, 10,
        10 if duration_val < 3 else (7 if duration_val <= 6 else 3),
        3 if cash_val < 5 else 10,
        10, 10, 0,
        5 if ter_val <= 1.0 else 3
    ],
    "滿分": [20, 15, 15, 10, 10, 10, 10, 5, 5],
    "狀態": ["✅ 優秀" if roc_val < 10 else "⚠️ 高風險警示", "⚠️ 警示", "⚠️ 留意槓桿", "✅ 優秀" if duration_val < 3 else "⚠️ 警示", "🚨 流動性緊湊" if cash_val < 5 else "✅ 優秀", "✅ 優秀", "✅ 優秀", "🚨 極高風險", "✅ 優秀" if ter_val <= 1.0 else "⚠️ 警示"]
}

# 4. 頂部抬頭與 KPI 指標卡片
st.markdown(f"""
    <div class="fund-header">
        <span style="font-size: 14px; color: #888;">當前分析目標基金：</span> 
        <span class="source-tag">📍 {data_source}</span><br>
        <span style="font-size: 20px; font-weight: bold; color: #FFF;">{fund_name_zh}</span> 
        <span style="font-size: 14px; color: #AAA;">({fund_name_en})</span>
    </div>
""", unsafe_allow_html=True)

total_score = sum(mock_data["實際得分"])
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1: st.metric(label="🛡️ 風險健康總分", value=f"{total_score} / 100", delta=f"{total_score - 100} 分", delta_color="inverse")
with kpi2: st.metric(label="⚠️ 平均信用評級", value=f"{rating_val}", delta="高收益債", delta_color="inverse")
with kpi3: st.metric(label="💧 流動性緩衝 (現金)", value=f"{cash_val}%", delta="現金偏緊" if cash_val < 5 else "充裕", delta_color="inverse" if cash_val < 5 else "normal")
with kpi4: st.metric(label="⏳ 利率敏感度 (久期)", value=f"{duration_val} 年", delta="抗加息力強" if duration_val < 3 else "敏感", delta_color="normal")

st.markdown("---")

# 5. 雷達圖與持倉表格
col_chart, col_table = st.columns([1, 1.3], gap="medium")

df_top10 = pd.DataFrame(top10_list)
top10_total_pct = round(df_top10["佔比 (%)"].sum(), 2) if "佔比 (%)" in df_top10.columns else 0.0

with col_chart:
    tab1, tab2 = st.tabs(["🕸️ 風險維度雷達圖", "📋 前十大持倉清單"])
    with tab1:
        df_chart = pd.DataFrame(dict(Score=mock_data["實際得分"], Dimension=mock_data["維度"]))
        fig_radar = px.line_polar(df_chart, r='Score', theta='Dimension', line_close=True, markers=True, range_r=[0, 20], template="plotly_dark", color_discrete_sequence=['#00E676'])
        fig_radar.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.3)', line=dict(color='#00E676', width=2))
        fig_radar.update_layout(height=370, margin=dict(l=20, r=20, t=20, b=20), polar=dict(radialaxis=dict(visible=True, range=[0, 20], showticklabels=False)))
        st.plotly_chart(fig_radar, use_container_width=True)
    with tab2:
        st.metric(label="📌 前十大持倉合共佔比", value=f"{top10_total_pct}%")
        st.dataframe(df_top10, use_container_width=True, hide_index=True, height=280)

with col_table:
    st.subheader("📋 風險評估項目")
    df_table = pd.DataFrame(mock_data)
    st.dataframe(df_table[["維度", "具體檢查指標", "評分簡準", "實際數據", "實際得分", "滿分", "狀態"]], use_container_width=True, hide_index=True, height=350)

st.info(f"**💡 系統智能洞察 ({fund_name_zh})**：{ai_analysis_summary}")
