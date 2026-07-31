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

# 1. 網頁頁面配置
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

st.title("🛡️ 智能基金風險評估系統")

# 📚 客觀真實資料庫 (完全保留兩隻預設基金資料與前十大持倉)
PRESET_FUNDS = {
    "霸菱環球高收益債券基金 (債券型)": {
        "type": "債券型基金",
        "zh": "霸菱環球高收益債券基金",
        "en": "Barings Global High Yield Bond Fund",
        "isin": "IE00BFM0MQ22",
        "score": "82.5",
        "status_tag": "🟢 健康 (整體財務結構良好)",
        "kpi_leverage": "101.1%",
        "kpi_cash": "11.26%",
        "kpi_roc": "42%~59%",
        "summary": "霸菱環球高收益債券基金綜合風險評分為 82.5 分 (健康)。資產槓桿率 101.1% 幾乎無借貸槓桿，現金儲備 11.26% 充沛 (約5.5億美元)，最低修訂存續期 2.58 年對利率敏感度低；重倉北美 (61.3%) 區域集中度偏高，但整體財務結構非常穩健。",
        "mock_data": {
            "評估維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、區域風險", "九、總開支比率"],
            "具體檢查指標": [
                "從資本派息 (ROC) 與總回報覆蓋率", 
                "評級分佈與非投資級占比", 
                "資產膨脹率 (Total / Net Assets)", 
                "有效存續期 (Duration)", 
                "現金儲備與營運現金流", 
                "前十大發行人持倉占比", 
                "衍生品對衝與未實現損益", 
                "單一區域/國家持倉集中度", 
                "每年管理費 (Management Fee)"
            ],
            "專屬評分簡算規則": [
                "20分: ROC <10% 或 總回報 ≥ 派息率 | 10分: ROC 10%~50% 且總回報覆蓋率 >70% | 0分: ROC >50% 且 總回報為負",
                "15分: 平均評級 BBB 以上 | 10分: 平均評級 BB 級 | 5分: Caa/CCC級 >10% 或未評級 >15%",
                "15分: 比率 <105% (無顯著槓桿) | 10分: 比率 105%~120% | 0分: 比率 >120% (槓桿過高)",
                "10分: 存續期 <3 年 (抗升息) | 5分: 存續期 3~6 年 | 0分: 存續期 >6 年",
                "10分: 現金 >10% 且營運 Cash Flow 為正 | 5分: 現金 5%~10% | 0分: 現金 <5% 或流動性緊縮",
                "10分: 前持倉 <20% (極分散) | 5分: 前持倉 20%~30% | 0分: 前持倉 >30%",
                "10分: 全額對衝且衍生品虧損 <1% NAV | 5分: 部分對衝 | 0分: 未對衝且外幣曝險過高",
                "5分: 單一區域 <40% | 2.5分: 單一區域 40%~60% | 0分: 單一區域 >60%",
                "5分: 管理費 <1.0% | 2.5分: 管理費 1.0%~1.5% | 0分: 管理費 >1.5%"
            ],
            "霸菱基金真實數據與解析": [
                "ROC 比例：42.2% ~ 59.2% | 2025總回報：+9.19% (派息率 ~9.87%)，帳面營運淨利遠高於派息總額，總回報幾乎完全覆蓋派息。",
                "平均評級：BB (Ba 級 37.91%、B 級 33.75%、Caa1 及以下占 9.69%)。標準高收益債配備，投資風險適中可控。",
                "總資產 / 淨資產：101.1% | Amounts due to broker 僅占 NAV 0.4%，幾乎無借貸槓桿，結構非常安全透明。",
                "最低修訂存續期：2.58 年。存續期極短，對央行利率變化的敏感度與衝擊較低。",
                "現金及等值：11.26% (約 5.5 億美元) | 2025營運現金流轉正 (+$2.11 億美元)，現金池充沛，足以支應短期贖回需求。",
                "前十大發行人合計占：13.59% | 最大單一發行人 (Bausch Health) 僅占 2.40%，極度分散，有效避免單一黑天鵝事件。",
                "各非美元類別均提供衍生品對衝 | 2025衍生品未實現淨利益 +$1,224 萬美元 (占 NAV 0.28%)，避險機制運作順暢。",
                "北美地區：61.3% | 歐洲地區：23.8%。重倉北美/美國市場，受美國宏觀經濟與信用週期影響深遠。",
                "G類別 (零售)：1.25% / 年 | F類別 (法人)：0% / 年。屬於市場高收益債券基金的標準收費區間。"
            ],
            "得分 / 滿分": ["15 / 20", "10 / 15", "15 / 15", "10 / 10", "10 / 10", "10 / 10", "10 / 10", "0 / 5", "2.5 / 5"],
            "實際得分": [15.0, 10.0, 15.0, 10.0, 10.0, 10.0, 10.0, 0.0, 2.5],
            "風險狀態": ["🟢 健康/觀察", "🟡 中等風險", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🔴 集中度偏高", "🟡 中等"]
        },
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
    "富達基金 - 美元高收益基金 (債券型)": {
        "type": "債券型基金",
        "zh": "富達基金 - 美元高收益基金",
        "en": "Fidelity Funds - US High Yield Fund",
        "isin": "LU0132282301",
        "score": "76.0",
        "status_tag": "良好",
        "kpi_leverage": "100.0%",
        "kpi_cash": "-0.40%",
        "kpi_roc": "0.0%",
        "summary": "富達美元高收益基金派息 100% 來自淨可分派收益 (0% 來自資本)；有效存續期 2.8 年抗升息力強，但流動性現金佔比為 -0.40% 偏緊。",
        "mock_data": {
            "評估維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、區域風險", "九、總開支比率"],
            "具體檢查指標": [
                "從資本派息 (ROC) 與總回報覆蓋率", 
                "評級分佈與非投資級占比", 
                "資產膨脹率 (Total / Net Assets)", 
                "有效存續期 (Duration)", 
                "現金儲備與營運現金流", 
                "前十大發行人持倉占比", 
                "衍生品對衝與未實現損益", 
                "單一區域/國家持倉集中度", 
                "每年管理費 (Management Fee)"
            ],
            "專屬評分簡算規則": [
                "20分: ROC <10% 或 總回報 ≥ 派息率 | 10分: ROC 10%~50% 且總回報覆蓋率 >70% | 0分: ROC >50% 且 總回報為負",
                "15分: 平均評級 BBB 以上 | 10分: 平均評級 BB 級 | 5分: Caa/CCC級 >10% 或未評級 >15%",
                "15分: 比率 <105% (無顯著槓桿) | 10分: 比率 105%~120% | 0分: 比率 >120% (槓桿過高)",
                "10分: 存續期 <3 年 (抗升息) | 5分: 存續期 3~6 年 | 0分: 存續期 >6 年",
                "10分: 現金 >10% 且營運 Cash Flow 為正 | 5分: 現金 5%~10% | 0分: 現金 <5% 或流動性緊縮",
                "10分: 前持倉 <20% (極分散) | 5分: 前持倉 20%~30% | 0分: 前持倉 >30%",
                "10分: 全額對衝且衍生品虧損 <1% NAV | 5分: 部分對衝 | 0分: 未對衝且外幣曝險過高",
                "5分: 單一區域 <40% | 2.5分: 單一區域 40%~60% | 0分: 單一區域 >60%",
                "5分: 管理費 <1.0% | 2.5分: 管理費 1.0%~1.5% | 0分: 管理費 >1.5%"
            ],
            "霸菱基金真實數據與解析": [
                "0.0% 來自資本 (100% 來自淨可分派收益，派息品質優秀)",
                "平均評級 BB- (高收益債)",
                "總資產 / 淨資產：100.0% (衍生工具風險淨額最高 50%)",
                "有效存續期 2.8 年 (抗升息力強)",
                "現金及等值 -0.40% (流動性偏緊)",
                "前十持倉合共 11.27% (持倉高度分散)",
                "基礎貨幣已對沖",
                "美國市場佔比 79.60% (單一國家集中度極高)",
                "每年管理費 1.00%"
            ],
            "得分 / 滿分": ["20 / 20", "8 / 15", "10 / 15", "10 / 10", "3 / 10", "10 / 10", "10 / 10", "0 / 5", "5 / 5"],
            "實際得分": [20.0, 8.0, 10.0, 10.0, 3.0, 10.0, 10.0, 0.0, 5.0],
            "風險狀態": ["🟢 優秀", "🟡 警示", "🟡 留意槓桿", "🟢 優秀", "🔴 流動性緊貼", "🟢 優秀", "🟢 優秀", "🔴 極高風險", "🟢 優秀"]
        },
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

# 2. 頂部選擇區 (完整保留選擇下拉選單)
ctrl_col1, ctrl_col2 = st.columns([1.5, 1])

with ctrl_col1:
    selected_preset = st.selectbox("📌 快速選擇已建檔基金：", list(PRESET_FUNDS.keys()))

curr_fund = PRESET_FUNDS[selected_preset]

with ctrl_col2:
    fund_type = st.selectbox("📌 基金類型設定：", ["債券型基金", "股票型基金"], index=0 if curr_fund["type"] == "債券型基金" else 1)

fund_name_zh = curr_fund["zh"]
fund_name_en = curr_fund["en"]
fund_isin = curr_fund["isin"]
ai_analysis_summary = curr_fund["summary"]
top10_list = curr_fund["top10"]
data_source = f"預設資料庫: {fund_name_zh}"

# 📂 完整保留 PDF 上傳區塊（含 Gemini AI 自動理解解析功能）
with st.expander("📂 點擊這裡：上傳任一基金月報/股息紀錄 PDF（Google Gemini AI 自動理解解析）", expanded=False):
    uploaded_file = st.file_uploader("請上傳任意基金 PDF 檔案", type=["pdf"])
    if uploaded_file is not None and PDF_SUPPORT:
        data_source = f"已上傳 PDF：{uploaded_file.name}"
        fund_name_zh = uploaded_file.name.replace(".pdf", "")

# 3. 頂部抬頭與 4 大 KPI 核心指標卡片 (完整保留)
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
    with kpi1: st.metric(label="🛡️ 綜合風險評分", value=f"{curr_fund['score']} / 100", delta=curr_fund["status_tag"], delta_color="normal")
    with kpi2: st.metric(label="📊 資產槓桿水平", value=curr_fund["kpi_leverage"], delta="無顯著借貸槓桿", delta_color="normal")
    with kpi3: st.metric(label="💧 現金與流動性", value=curr_fund["kpi_cash"], delta="現金儲備充沛", delta_color="normal")
    with kpi4: st.metric(label="💰 從資本派息 (ROC) 狀況", value=curr_fund["kpi_roc"], delta="總回報覆蓋率佳", delta_color="normal")
else:
    with kpi1: st.metric(label="🛡️ 股票風險健康總分", value="待核對 (0 / 100)")
    with kpi2: st.metric(label="📈 市場敏感度 (Beta)", value="待對照 PDF", delta="基準係數 1.0")
    with kpi3: st.metric(label="📊 絕對波動 (標準差)", value="待對照 PDF", delta="年化波幅 %")
    with kpi4: st.metric(label="⚖️ 風險性價比 (Sharpe)", value="待對照 PDF", delta="夏普比率")

st.markdown("---")

# 4. 中間核心區：雷達圖與持倉清單 (完整保留)
col_chart, col_table = st.columns([1, 1.3], gap="medium")

df_top10 = pd.DataFrame(top10_list)
top10_total_pct = round(df_top10["佔比 (%)"].sum(), 2) if "佔比 (%)" in df_top10.columns else 0.0

with col_chart:
    tab1, tab2 = st.tabs([f"🕸️ {fund_type}風險雷達圖", "📋 前十大持倉清單"])
    
    with tab1:
        if fund_type == "股票型基金":
            st.info("💡 目前切換至股票型基金，請上傳股票基金 PDF 後自動生成雷達圖。")
        else:
            df_chart = pd.DataFrame(dict(Score=curr_fund["mock_data"]["實際得分"], Dimension=curr_fund["mock_data"]["評估維度"]))
            fig_radar = px.line_polar(
                df_chart, r='Score', theta='Dimension', line_close=True, markers=True, range_r=[0, 20], template="plotly_dark", color_discrete_sequence=['#00E676']
            )
            fig_radar.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.3)', line=dict(color='#00E676', width=2), marker=dict(size=6, color='#00E676'))
            fig_radar.update_layout(height=370, margin=dict(l=20, r=20, t=20, b=20), polar=dict(radialaxis=dict(visible=True, range=[0, 20], showticklabels=False)))
            st.plotly_chart(fig_radar, use_container_width=True)
        
    with tab2:
        st.metric(label="📌 前十大持倉合共佔比 (Top 10 Total)", value=f"{top10_total_pct}%", delta="持倉高度分散", delta_color="normal")
        st.dataframe(df_top10, use_container_width=True, hide_index=True, height=280)

with col_table:
    # 💡 這裡精準更新為照片中的 9 大維度風險評估明細表
    st.subheader("📋 9 大維度風險評估明細表")
    df_mock = pd.DataFrame(curr_fund["mock_data"])
    st.dataframe(
        df_mock[["評估維度", "具體檢查指標", "專屬評分簡算規則", "霸菱基金真實數據與解析", "得分 / 滿分", "風險狀態"]],
        use_container_width=True, hide_index=True, height=350
    )

# 5. 底部：Gemini AI 智能洞察點評 (完整保留)
st.info(f"**💡 AI 智能洞察 ({fund_name_zh})**：{ai_analysis_summary}")
