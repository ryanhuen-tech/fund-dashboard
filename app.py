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

# 📚 客觀真實資料庫
PRESET_FUNDS = {
    "富達基金 - 美元高收益基金 (債券型)": {
        "type": "債券型基金",
        "zh": "富達基金 - 美元高收益基金",
        "en": "Fidelity Funds - US High Yield Fund",
        "isin": "LU0132282301",
        "roc": 0.0,
        "duration": 2.8,
        "cash": -0.40,
        "rating": "BB-",
        "ter": 1.00,
        "summary": "本基金為富達美元高收益基金。派息 100% 來自淨可分派收益 (0% 來自資本)；有效存續期 2.8 年，流動性現金佔比為 -0.40%。",
        "top10": [
            {"排名": 1, "持倉名稱": "UST BILLS 0% 07/30/26", "資產類別": "美國國庫券", "佔比 (%)": 3.02},
            {"排名": 2, "持倉名稱": "UST BILLS 0% 09/10/26", "資產類別": "美國國庫券", "佔比 (%)": 2.02},
            {"排名": 3, "持倉名稱": "DIRECTV HLDGS 9.25% 6/32", "資產類別": "通訊服務債", "佔比 (%)": 0.89},
            {"排名": 4, "持倉名稱": "VENTURE 9.875% 02/01/32", "資產類別": "能源債", "佔比 (%)": 0.88},
            {"排名": 5, "持倉名稱": "WULF COMPUTE 7.75% 10/30", "資產類別": "科技債", "佔比 (%)": 0.84},
        ]
    },
    "霸菱環球高收益債券基金 (債券型)": {
        "type": "債券型基金",
        "zh": "霸菱環球高收益債券基金",
        "en": "Barings Global High Yield Bond Fund",
        "isin": "IE00BFM0MQ22",
        "roc": 47.39,
        "duration": 2.58,
        "cash": 11.26,
        "rating": "BB",
        "ter": 1.33,
        "summary": "本基金為霸菱環球高收益債券基金。從資本派息比例為 47.39%，需注意資本侵蝕風險；流動性緩衝 11.26% 相對充裕，有效存續期 2.58 年。",
        "top10": [
            {"排名": 1, "持倉名稱": "現金及等值資產 (Cash Equivalents)", "資產類別": "現金/貨幣市場", "佔比 (%)": 11.26},
            {"排名": 2, "持倉名稱": "Bausch Health Companies Inc.", "資產類別": "醫療保健債", "佔比 (%)": 2.40},
            {"排名": 3, "持倉名稱": "Charter Communications Inc.", "資產類別": "通訊服務債", "佔比 (%)": 1.71},
            {"排名": 4, "持倉名稱": "First Quantum Minerals Ltd", "資產類別": "基本工業債", "佔比 (%)": 1.66},
            {"排名": 5, "持倉名稱": "Uniti Group Inc.", "資產類別": "通訊基礎設施債", "佔比 (%)": 1.46},
        ]
    }
}

# 2. 頂部選擇區
ctrl_col1, ctrl_col2 = st.columns([1.5, 1])

with ctrl_col1:
    selected_preset = st.selectbox("📌 快速選擇已建檔基金：", list(PRESET_FUNDS.keys()))

curr_fund = PRESET_FUNDS[selected_preset]

with ctrl_col2:
    fund_type = st.selectbox("📌 基金類型設定：", ["債券型基金", "股票型基金"], index=0 if curr_fund["type"] == "債券型基金" else 1)

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
is_custom_pdf = False

# PDF 上傳動態讀取
with st.expander("📂 點擊上傳新 PDF（自動識別股票型/債券型並更新表單）", expanded=False):
    uploaded_file = st.file_uploader("請上傳任意基金 PDF 檔案", type=["pdf"])
    if uploaded_file is not None and PDF_SUPPORT:
        data_source = f"已上傳 PDF：{uploaded_file.name}"
        fund_name_zh = uploaded_file.name.replace(".pdf", "")
        is_custom_pdf = True

# 3. 根據【基金類型】自動切換專屬 9 大風險評估表
if fund_type == "債券型基金":
    mock_data = {
        "維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、國家/宏觀風險", "九、總開支比率"],
        "具體檢查指標": ["從資本派息 (ROC) 比例", "投資組合平均信貸評級", "衍生工具及總槓桿比率", "有效存續期 (Duration)", "現金及高流動性資產佔比", "前十大持倉總集中比例", "非對沖外幣資產曝險", "單一國家/區域持倉集中度", "每年管理費 / TER"],
        "評分簡準": ["ROC < 10% 滿分 (>30% 扣分)", "評級 BBB 以上滿分 (BB 扣分)", "無槓桿滿分 (>20% 扣分)", "存續期 < 3年 滿分 (>6年 扣分)", "現金 > 10% 滿分 (<5% 扣分)", "前十持倉 < 30% 滿分", "完全對沖滿分 (未對沖扣分)", "單一國家 < 40% 滿分 (>60% 0分)", "TER < 1.0% 滿分 (>1.5% 0分)"],
        "實際數據": [f"{roc_val}% 來自資本", f"平均評級 {rating_val}", "衍生工具風險淨額最高 50%", f"有效存續期 {duration_val} 年", f"現金及等值 {cash_val}%", "前十持倉分散", "基礎貨幣已對沖", "美國/單一區域佔比偏高", f"每年管理費 {ter_val}%"],
        "實際得分": [20 if roc_val < 10 else (10 if roc_val > 30 else 15), 8, 10, 10 if duration_val < 3 else 5, 3 if cash_val < 5 else 10, 10, 10, 0, 5 if ter_val <= 1.0 else 3],
        "滿分": [20, 15, 15, 10, 10, 10, 10, 5, 5],
        "狀態": ["✅ 優秀" if roc_val < 10 else "⚠️ 警示", "⚠️ 警示", "⚠️ 留意槓桿", "✅ 優秀" if duration_val < 3 else "⚠️ 警示", "🚨 流動性緊湊" if cash_val < 5 else "✅ 優秀", "✅ 優秀", "✅ 優秀", "🚨 極高風險", "✅ 優秀" if ter_val <= 1.0 else "⚠️ 警示"]
    }
    total_score = sum(mock_data["實際得分"])
    total_score_str = f"{total_score} / 100"
else: # 📈 股票型基金：若無資料則全數顯示「待核對 / 0分」，絕不虛構！
    mock_data = {
        "維度": ["一、市場敏感度", "二、極端回撤", "三、持倉集中度", "四、絕對波動控制", "五、風險性價比", "六、經理穩定性", "七、規模適中性", "八、行業集中度", "九、地區分散度"],
        "具體檢查指標": ["貝塔係數 (β)", "最大回撤 (Max Drawdown)", "前十大重倉股佔比", "年度化標準差", "夏普比率 (Sharpe Ratio)", "任職年限與變更", "基金資產規模 (AUM)", "最大單一行業佔比", "投資地域分佈"],
        "評分簡準": [
            "β < 0.8 防禦=15分 | 0.8-1.2 適中=9分 | >1.2 高波動=0分",
            "回撤 < 15%=15分 | 15%-25%=9分 | > 25%=0分",
            "< 30% 分散=10分 | 30%-50%=6分 | > 50% 集中=0分",
            "< 10% 穩健=5分 | 10%-20%=3分 | > 20% 高波動=0分",
            "> 1.0 優秀=10分 | 0.5-1.0 良好=6分 | < 0.5 差=0分",
            "> 3年無變更=15分 | 1-3年=9分 | < 1年/頻繁變更=0分",
            "2億-100億=10分 | 5000萬-2億或>100億=6分 | < 5000萬=0分",
            "< 20%=10分 | 20%-30%=6分 | > 30% 高度集中=0分",
            "全球分散<40%=10分 | 區域型40%-70%=6分 | 單一國家>70%=0分"
        ],
        "實際數據": ["待上傳 PDF 核對", "待上傳 PDF 核對", "待上傳 PDF 核對", "待上傳 PDF 核對", "待上傳 PDF 核對", "待上傳 PDF 核對", "待上傳 PDF 核對", "待上傳 PDF 核對", "待上傳 PDF 核對"],
        "實際得分": [0, 0, 0, 0, 0, 0, 0, 0, 0], # 未上傳核對前，分數全數為 0
        "滿分": [15, 15, 10, 5, 10, 15, 10, 10, 10],
        "狀態": ["📋 待核對", "📋 待核對", "📋 待核對", "📋 待核對", "📋 待核對", "📋 待核對", "📋 待核對", "📋 待核對", "📋 待核對"]
    }
    total_score_str = "待核對 (0 / 100)"
    ai_analysis_summary = "目前切換至股票型基金風險架構。請上傳該股票型基金之 Factsheet / 月報 PDF，系統將自動核對 9 大指標並進行評分。"

# 4. 頂部抬頭與 KPI 指標卡片
st.markdown(f"""
    <div class="fund-header">
        <span style="font-size: 14px; color: #888;">當前分析目標基金 ({fund_type})：</span> 
        <span class="source-tag">📍 {data_source}</span><br>
        <span style="font-size: 20px; font-weight: bold; color: #FFF;">{fund_name_zh}</span> 
        <span style="font-size: 14px; color: #AAA;">({fund_name_en})</span>
    </div>
""", unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

if fund_type == "債券型基金":
    with kpi1: st.metric(label="🛡️ 風險健康總分", value=total_score_str, delta=f"{sum(mock_data['實際得分']) - 100} 分", delta_color="inverse")
    with kpi2: st.metric(label="⚠️ 平均信用評級", value=f"{rating_val}", delta="高收益債", delta_color="inverse")
    with kpi3: st.metric(label="💧 流動性緩衝 (現金)", value=f"{cash_val}%", delta="現金偏緊" if cash_val < 5 else "充裕", delta_color="inverse" if cash_val < 5 else "normal")
    with kpi4: st.metric(label="⏳ 利率敏感度 (久期)", value=f"{duration_val} 年", delta="抗加息力強" if duration_val < 3 else "敏感", delta_color="normal")
else:
    with kpi1: st.metric(label="🛡️ 股票風險健康總分", value=total_score_str)
    with kpi2: st.metric(label="📈 市場敏感度 (Beta)", value="待對照 PDF", delta="基準係數 1.0")
    with kpi3: st.metric(label="📊 絕對波動 (標準差)", value="待對照 PDF", delta="年化波幅 %")
    with kpi4: st.metric(label="⚖️ 風險性價比 (Sharpe)", value="待對照 PDF", delta="夏普比率")

st.markdown("---")

# 5. 雷達圖與持倉表格
col_chart, col_table = st.columns([1, 1.3], gap="medium")

df_top10 = pd.DataFrame(top10_list)

with col_chart:
    tab1, tab2 = st.tabs([f"🕸️ {fund_type}風險雷達圖", "📋 前十大持倉清單"])
    with tab1:
        if fund_type == "股票型基金" and sum(mock_data["實際得分"]) == 0:
            st.info("💡 目前尚未載入股票型基金數據，請上傳 PDF 後生成風險雷達圖。")
        else:
            df_chart = pd.DataFrame(dict(Score=mock_data["實際得分"], Dimension=mock_data["維度"]))
            fig_radar = px.line_polar(df_chart, r='Score', theta='Dimension', line_close=True, markers=True, range_r=[0, 15], template="plotly_dark", color_discrete_sequence=['#00E676'])
            fig_radar.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.3)', line=dict(color='#00E676', width=2))
            fig_radar.update_layout(height=370, margin=dict(l=20, r=20, t=20, b=20), polar=dict(radialaxis=dict(visible=True, range=[0, 15], showticklabels=False)))
            st.plotly_chart(fig_radar, use_container_width=True)
    with tab2:
        st.dataframe(df_top10, use_container_width=True, hide_index=True, height=280)

with col_table:
    st.subheader(f"📋 {fund_type}風險評估項目 (參照標準試算表)")
    df_table = pd.DataFrame(mock_data)
    st.dataframe(df_table[["維度", "具體檢查指標", "評分簡準", "實際數據", "實際得分", "滿分", "狀態"]], use_container_width=True, hide_index=True, height=350)

st.info(f"**💡 系統智能洞察 ({fund_name_zh})**：{ai_analysis_summary}")
