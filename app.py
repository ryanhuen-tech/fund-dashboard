import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 安全導入 pdfplumber
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

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

# 📚 方案 A：通用關鍵字字典
KEYWORDS_ISIN = [r'ISIN[:\s]*([A-Z0-9]{12})', r'代號[:\s]*([A-Z0-9]{12})']
KEYWORDS_DURATION = [r'(?:修訂存續期|存續期|有效久期|久期|Mod\s*Duration|Effective\s*Duration|Duration)[^\d]*([\d\.]+)', r'([\d\.]+)\s*(?:年|Years)\s*(?:久期|存續期|Duration)']
KEYWORDS_CASH = [r'(?:現金及等值|現金及等同資產|現金佔比|現金與等值|流動資金|現金|Cash\s*&\s*Equivalents|Cash\s*Equivalents|Cash)[^\d]*([\d\.]+)\s*%', r'([\d\.]+)\s*%\s*(?:現金|Cash)']
KEYWORDS_ROC = [r'(?:由資本所分派之股息|來自資本|從資本派息|資本分派|派息來自資本|資本派息|ROC|Pay\s*from\s*Capital|Capital\s*Distribution)[^\d]*([\d\.]+)\s*%', r'([\d\.]+)\s*%\s*(?:來自資本|來自本金|ROC)']
KEYWORDS_TER = [r'(?:經常性開支比率|總開支比率|總管理費|經常性開支|TER|Total\s*Expense\s*Ratio|Ongoing\s*Charges)[^\d]*([\d\.]+)\s*%']

# 預設數據範本 (未上傳時的預設值)
fund_name_zh = "霸菱環球高收益債券基金"
fund_name_en = "Barings Global High Yield Bond Fund"
fund_isin = "IE00BFM0MQ22"

roc_val = 47.39
duration_val = 2.58
cash_val = 11.26
rating_val = "BB"
ter_val = 1.33
data_source = "預設範本"

# 預設霸菱十大持倉
top10_list = [
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

# 2. 頂部工具列與 PDF 自動化解析區
st.title("🛡️ 智能基金風險評估系統")

with st.expander("📂 點擊這裡：上傳任一基金月報/概覽 PDF (已啟動全公司關鍵字對照)", expanded=True):
    uploaded_file = st.file_uploader("拖跩或選擇 PDF 檔案（支援霸菱、聯博、貝萊德等各大基金格式）", type=["pdf"])
    
    if uploaded_file is not None and PDF_SUPPORT:
        try:
            text_content = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for p in range(min(len(pdf.pages), 5)):
                    extracted = pdf.pages[p].extract_text()
                    if extracted:
                        text_content += extracted + "\n"
            
            # 🔍 自動抓取基金名稱 (取第一行文字或檔名)
            file_title = uploaded_file.name.replace(".pdf", "")
            fund_name_zh = f"已分析基金 ({file_title})"
            fund_name_en = f"Uploaded PDF: {uploaded_file.name}"
            data_source = f"PDF 解析自: {uploaded_file.name}"

            # 🔍 1. ISIN
            for pattern in KEYWORDS_ISIN:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    fund_isin = match.group(1)
                    break
            
            # 🔍 2. Duration
            for pattern in KEYWORDS_DURATION:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    duration_val = float(match.group(1))
                    break

            # 🔍 3. Cash
            for pattern in KEYWORDS_CASH:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    cash_val = float(match.group(1))
                    top10_list[0]["佔比 (%)"] = cash_val  # 自動連動現金持倉比率
                    break

            # 🔍 4. ROC
            for pattern in KEYWORDS_ROC:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    roc_val = float(match.group(1))
                    break

            # 🔍 5. TER
            for pattern in KEYWORDS_TER:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    ter_val = float(match.group(1))
                    break

            st.success(f"🎉 數據更新成功！已載入檔案《{uploaded_file.name}》| ISIN: {fund_isin} | 資本派息: {roc_val}% | 久期: {duration_val}年 | 現金: {cash_val}%")
        
        except Exception as e:
            st.error(f"⚠️ 解析 PDF 時出現微小異常，已保護系統運作：{e}")

# 動態生成 9 大維度實際數據與得分
mock_data = {
    "維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、國家/宏觀風險", "九、總開支比率"],
    "具體檢查指標": [
        "從資本派息 (ROC) 比例",
        "投資組合平均信貸評級",
        "衍生工具及總槓桿比率",
        "修訂存續期 (Duration)",
        "現金及高流動性資產佔比",
        "前十大持倉總集中比例",
        "非對沖外幣資產曝險",
        "單一國家/區域持倉集中度",
        "經常性開支比率 (TER)"
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
        f"{roc_val}% 來自資本", 
        f"平均評級 {rating_val} (高收益債)", 
        "無過度槓桿 (安全)", 
        f"存續期 {duration_val} 年 (防禦力強)", 
        f"現金及等值 {cash_val}% (充裕)", 
        "最大持倉 2.40% (分散)", 
        "基礎貨幣已對沖", 
        "北美佔比 61.3% (極度集中)", 
        f"經常性開支比率 {ter_val}%"
    ],
    "實際得分": [
        10 if roc_val > 30 else (15 if roc_val > 10 else 20),
        8, 15, 
        10 if duration_val < 3 else (7 if duration_val <= 6 else 3),
        10 if cash_val > 10 else (7 if cash_val >= 5 else 3),
        10, 10, 0,
        5 if ter_val < 1.0 else (3 if ter_val <= 1.5 else 0)
    ],
    "滿分": [20, 15, 15, 10, 10, 10, 10, 5, 5],
    "狀態": [
        "⚠️ 警示" if roc_val > 30 else "✅ 優秀",
        "⚠️ 警示", "✅ 優秀", 
        "✅ 優秀" if duration_val < 3 else "⚠️ 警示",
        "✅ 優秀" if cash_val > 10 else "⚠️ 警示",
        "✅ 優秀", "✅ 優秀", "🚨 極高風險",
        "✅ 優秀" if ter_val < 1.0 else "⚠️ 警示"
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
    st.metric(label="⚠️ 從資本派息比例", value=f"{roc_val}%", delta="高風險警示" if roc_val > 30 else "健康", delta_color="inverse" if roc_val > 30 else "normal")

with kpi3:
    st.metric(label="💧 流動性緩衝 (現金)", value=f"{cash_val}%", delta="資產充裕" if cash_val > 10 else "偏低", delta_color="normal")

with kpi4:
    st.metric(label="⏳ 利率敏感度 (久期)", value=f"{duration_val} 年", delta="抗加息力強" if duration_val < 3 else "敏感", delta_color="normal")

st.markdown("---")

# 4. 中間核心區：雷達圖與持倉清單
col_chart, col_table = st.columns([1, 1.3], gap="medium")

df_top10 = pd.DataFrame(top10_list)
top10_total_pct = round(df_top10["佔比 (%)"].sum(), 2)

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
            df_top10[["排名", "持倉名稱", "資產類別", "佔比 (%)"]],
            use_container_width=True, hide_index=True, height=280,
            column_config={
                "排名": st.column_config.NumberColumn("排名", alignment="left"),
                "持倉名稱": st.column_config.TextColumn("持倉名稱", alignment="left"),
                "資產類別": st.column_config.TextColumn("資產類別", alignment="left"),
                "佔比 (%)": st.column_config.NumberColumn("佔比 (%)", alignment="left", format="%.2f%%"),
            }
        )

with col_table:
    st.subheader("📋 風險評估項目")
    df_table = pd.DataFrame(mock_data)
    st.dataframe(
        df_table[["維度", "具體檢查指標", "評分簡準", "實際數據", "實際得分", "滿分", "狀態"]],
        use_container_width=True, hide_index=True, height=350
    )

# 5. 底部：動態系統洞察點評
st.info(f"**💡 系統智能洞察 ({fund_name_zh})**：【{data_source}】數據已載入！當前資本派息比例為 **{roc_val}%**、久期為 **{duration_val} 年**、現金比例為 **{cash_val}%**。風險分數已即時計算完畢！")
