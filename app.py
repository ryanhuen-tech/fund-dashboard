import streamlit as st
import pandas as pd
import plotly.express as px

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
    "霸菱環球高收益債券基金 (債券型)": {
        "type": "債券型基金",
        "zh": "霸菱環球高收益債券基金",
        "en": "Barings Global High Yield Bond Fund",
        "isin": "IE00BFM0MQ22",
        "score": 82.5,
        "status_tag": "健康 (整體財務結構良好)",
        "kpi_leverage": "101.1%",
        "kpi_cash": "11.26%",
        "kpi_roc": "42% ~ 59%",
        "summary": "霸菱環球高收益債券基金綜合風險評分為 82.5 分 (健康)。槓桿控制極佳 (101.1%)，現金儲備充沛 (11.26%，約5.5億美元)，存續期僅 2.58 年抗升息力強；雖然單一區域 (北美 61.3%) 集中度較高，但整體財務與避險結構非常穩健。",
        "mock_data": {
            "評估維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、區域風險", "九、總開支比率"],
            "具體檢查指標": ["從資本派息 (ROC) 與總回報覆蓋率", "評級分佈與非投資級占比", "資產膨脹率 (Total / Net Assets)", "有效存續期 (Duration)", "現金儲備與營運現金流", "前十大發行人持倉占比", "衍生品對衝與未實現損益", "單一區域/國家持倉集中度", "每年管理費 (Management Fee)"],
            "專屬評分簡算規則": [
                "20分: ROC < 10% 或 總回報 ≥ 派息率 | 10分: ROC 10%-50% 且總回報覆蓋率 > 70% | 0分: ROC > 50% 且 總回報為負",
                "15分: 平均評級 BBB 以上 | 10分: 平均評級 BB 級 | 5分: Caa/CCC級 > 10% 或未評級 > 15%",
                "15分: 比率 < 105% (無顯著槓桿) | 10分: 比率 105%-120% | 0分: 比率 > 120% (槓桿過高)",
                "10分: 存續期 < 3年 (抗升息) | 5分: 存續期 3-6年 | 0分: 存續期 > 6年",
                "10分: 現金 > 10% 且營運 Cash Flow 為正 | 5分: 現金 5%-10% | 0分: 現金 < 5% 或流動性緊縮",
                "10分: 前持倉 < 20% (極分散) | 5分: 前持倉 20%-30% | 0分: 前持倉 > 30%",
                "10分: 全額對衝且衍生品虧損 < 1% NAV | 5分: 部分對衝 | 0分: 未對衝且外幣曝險過高",
                "5分: 單一區域 < 40% | 2.5分: 單一區域 40%-60% | 0分: 單一區域 > 60%",
                "5分: 管理費 < 1.0% | 2.5分: 管理費 1.0%-1.5% | 0分: 管理費 > 1.5%"
            ],
            "霸菱基金真實數據與解析": [
                "ROC 比例：42.2%~59.2% | 2025總回報: +9.19% (派息率 ~9.87%)，營運淨利遠高於派息總額，總回報幾乎完全覆蓋派息。",
                "平均評級：BB (Ba級 37.91%、B級 33.75%、Caa1及以下占 9.69%)。標準高收益債配備，投資風險適中可控。",
                "總資產 / 淨資產：101.1% | Amounts due to broker 僅占 NAV 0.4%，幾乎無借貸槓桿，結構非常安全透明。",
                "最低修訂存續期：2.58 年。存續期極短，對央行利率變化的敏感度與衝擊較低。",
                "現金及等值：11.26% (約 5.5 億美元) | 2025營運現金流轉正 (+$2.11 億美元)，現金池充沛，足以支應短期贖回需求。",
                "前十大發行人合計占：13.59% | 最大單一發行人 (Bausch Health) 僅占 2.40%，極度分散。",
                "各非美元類別均提供衍生品對衝 | 2025衍生品未實現淨利益 +$1,224 萬美元 (占 NAV 0.28%)，避險機制運作順暢。",
                "北美地區：61.3% | 歐洲地區：23.8%。重倉北美/美國市場，受美國宏觀經濟與信用週期影響深遠。",
                "G類別 (零售)：1.25% / 年 | F類別 (法人)：0% / 年。屬於市場高收益債券基金的標準收費區間。"
            ],
            "實際得分": [15.0, 10.0, 15.0, 10.0, 10.0, 10.0, 10.0, 0.0, 2.5],
            "滿分": [20, 15, 15, 10, 10, 10, 10, 5, 5],
            "風險狀態": ["🟢 健康/觀察", "🟡 中等風險", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🔴 集中度偏高", "🟡 中等"]
        },
        "top10": [
            {"排名": 1, "持倉名稱": "現金及等值資產 (Cash Equivalents)", "資產類別": "現金/貨幣市場", "佔比 (%)": 11.26},
            {"排名": 2, "持倉名稱": "Bausch Health Companies Inc.", "資產類別": "醫療保健債", "佔比 (%)": 2.40},
            {"排名": 3, "持倉名稱": "Charter Communications Inc.", "資產類別": "通訊服務債", "佔比 (%)": 1.71},
            {"排名": 4, "持倉名稱": "First Quantum Minerals Ltd", "資產類別": "基本工業債", "佔比 (%)": 1.66},
            {"排名": 5, "持倉名稱": "Uniti Group Inc.", "資產類別": "通訊基礎設施債", "佔比 (%)": 1.46},
        ]
    },
    "富達基金 - 美元高收益基金 (債券型)": {
        "type": "債券型基金",
        "zh": "富達基金 - 美元高收益基金",
        "en": "Fidelity Funds - US High Yield Fund",
        "isin": "LU0132282301",
        "score": 76.0,
        "status_tag": "良好",
        "kpi_leverage": "100.0%",
        "kpi_cash": "-0.40%",
        "kpi_roc": "0.0%",
        "summary": "富達美元高收益基金派息 100% 來自淨可分派收益 (0% 來自資本)；有效存續期 2.8 年抗升息力強，但流動性現金佔比為 -0.40% 偏緊。",
        "mock_data": {
            "評估維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、區域風險", "九、總開支比率"],
            "具體檢查指標": ["從資本派息 (ROC) 比例", "投資組合平均信貸評級", "衍生工具及總槓桿比率", "有效存續期 (Duration)", "現金及高流動性資產佔比", "前十大持倉總集中比例", "非對沖外幣資產曝險", "單一國家/區域持倉集中度", "每年管理費 / TER"],
            "專屬評分簡算規則": ["ROC < 10% 滿分", "評級 BBB 以上滿分", "無槓桿滿分", "存續期 < 3年 滿分", "現金 > 10% 滿分", "前十持倉 < 30% 滿分", "完全對沖滿分", "單一國家 < 40% 滿分", "TER < 1.0% 滿分"],
            "霸菱基金真實數據與解析": ["0.0% 來自資本 (100% 來自淨收益)", "平均評級 BB-", "衍生工具風險淨額最高 50%", "有效存續期 2.8 年", "現金及等值 -0.40%", "前十持倉合共 11.27% (極分散)", "基礎貨幣已對沖", "美國市場佔比 79.60% (集中度高)", "每年管理費 1.00%"],
            "實際得分": [20.0, 8.0, 10.0, 10.0, 3.0, 10.0, 10.0, 0.0, 5.0],
            "滿分": [20, 15, 15, 10, 10, 10, 10, 5, 5],
            "風險狀態": ["🟢 優秀", "🟡 警示", "🟡 留意槓桿", "🟢 優秀", "🔴 流動性緊貼", "🟢 優秀", "🟢 優秀", "🔴 極高風險", "🟢 優秀"]
        },
        "top10": [
            {"排名": 1, "持倉名稱": "UST BILLS 0% 07/30/26", "資產類別": "美國國庫券", "佔比 (%)": 3.02},
            {"排名": 2, "持倉名稱": "UST BILLS 0% 09/10/26", "資產類別": "美國國庫券", "佔比 (%)": 2.02},
            {"排名": 3, "持倉名稱": "DIRECTV HLDGS 9.25% 6/32", "資產類別": "通訊服務債", "佔比 (%)": 0.89},
            {"排名": 4, "持倉名稱": "VENTURE 9.875% 02/01/32", "資產類別": "能源債", "佔比 (%)": 0.88},
            {"排名": 5, "持倉名稱": "WULF COMPUTE 7.75% 10/30", "資產類別": "科技債", "佔比 (%)": 0.84},
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

# 載入資料
fund_name_zh = curr_fund["zh"]
fund_name_en = curr_fund["en"]
fund_isin = curr_fund["isin"]
ai_analysis_summary = curr_fund["summary"]
top10_list = curr_fund["top10"]
data_source = f"核對數據源: {fund_name_zh}"

# 3. 頂部抬頭與 KPI 指標卡片 (精準還原圖片 4 大卡片)
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
    with kpi2: st.metric(label="📊 資產槓桿水平", value=curr_fund["kpi_leverage"], delta="優秀 (無顯著借貸槓桿)", delta_color="normal")
    with kpi3: st.metric(label="💧 現金與流動性", value=curr_fund["kpi_cash"], delta="優秀 (~5.5億美元現金儲備)", delta_color="normal")
    with kpi4: st.metric(label="💰 從資本派息 (ROC) 狀況", value=curr_fund["kpi_roc"], delta="總回報覆蓋率佳 (緩衝池擴大)", delta_color="normal")

st.markdown("---")

# 4. 雷達圖與風險評估明細表
col_chart, col_table = st.columns([1, 1.3], gap="medium")

df_mock = pd.DataFrame(curr_fund["mock_data"])

with col_chart:
    tab1, tab2 = st.tabs([f"🕸️ {fund_type}風險雷達圖", "📋 前十大持倉清單"])
    with tab1:
        df_chart = pd.DataFrame(dict(Score=curr_fund["mock_data"]["實際得分"], Dimension=curr_fund["mock_data"]["評估維度"]))
        fig_radar = px.line_polar(df_chart, r='Score', theta='Dimension', line_close=True, markers=True, range_r=[0, 20], template="plotly_dark", color_discrete_sequence=['#00E676'])
        fig_radar.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.3)', line=dict(color='#00E676', width=2))
        fig_radar.update_layout(height=370, margin=dict(l=20, r=20, t=20, b=20), polar=dict(radialaxis=dict(visible=True, range=[0, 20], showticklabels=False)))
        st.plotly_chart(fig_radar, use_container_width=True)
    with tab2:
        st.dataframe(pd.DataFrame(top10_list), use_container_width=True, hide_index=True, height=280)

with col_table:
    st.subheader("📋 9 大維度風險評估明細表")
    st.dataframe(
        df_mock[["評估維度", "具體檢查指標", "專屬評分簡算規則", "霸菱基金真實數據與解析", "實際得分", "滿分", "風險狀態"]], 
        use_container_width=True, hide_index=True, height=350
    )

st.info(f"**💡 系統智能洞察 ({fund_name_zh})**：{ai_analysis_summary}")
