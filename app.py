import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁頁面配置
st.set_page_config(
    page_title="智能基金風險評估系統", 
    page_icon="🛡️", 
    layout="wide"
)

# 2. 注入自訂 CSS 樣式（1:1 還原圖片介面與顏色）
st.markdown("""
    <style>
    /* 全局背景與字體大小 */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        background-color: #F8FAFC;
    }
    
    /* 頂部 KPI 卡片樣式 */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        margin-bottom: 10px;
        height: 100%;
    }
    .kpi-title {
        font-size: 13px;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .kpi-value-container {
        display: flex;
        align-items: baseline;
        gap: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #0F172A;
    }
    .kpi-subtext {
        font-size: 14px;
        color: #94A3B8;
    }
    
    /* 狀態標籤 (Pill Badges) */
    .badge-green {
        background-color: #D1FAE5;
        color: #065F46;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: 8px;
    }
    .badge-yellow {
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: 8px;
    }
    .badge-red {
        background-color: #FEE2E2;
        color: #991B1B;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: 8px;
    }
    
    /* 表格與標頭 */
    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #1E293B;
        margin-top: 15px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 📚 客觀真實資料庫 (照片專屬對應資料)
PRESET_FUNDS = {
    "霸菱環球高收益債券基金 (債券型)": {
        "type": "債券型基金",
        "zh": "霸菱環球高收益債券基金",
        "en": "Barings Global High Yield Bond Fund",
        "score": "82.5",
        "status_tag": "🟢 健康 (整體財務結構良好)",
        "kpi_leverage": "101.1%",
        "kpi_leverage_tag": "✅ 優秀 (無顯著借貸槓桿)",
        "kpi_cash": "11.26%",
        "kpi_cash_tag": "✅ 優秀 (~5.5億美元現金儲備)",
        "kpi_roc": "42%~59%",
        "kpi_roc_tag": "🟢 總回報覆蓋率佳 (緩衝池擴大)",
        "summary": "霸菱環球高收益債券基金綜合風險評分為 82.5 分 (健康)。槓桿控制極佳 (101.1%)，現金儲備充沛 (11.26%，約5.5億美元)，存續期僅 2.58 年抗升息力強；雖然單一區域 (北美 61.3%) 集中度較高，但整體財務與避險結構非常穩健。",
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
                "• 20分: ROC <10% 或 總回報 ≥ 派息率\n• 10分: ROC 10%~50% 且總回報覆蓋率 >70%\n• 0分: ROC >50% 且 總回報為負",
                "• 15分: 平均評級 BBB 以上\n• 10分: 平均評級 BB 級\n• 5分: Caa/CCC級 >10% 或未評級 >15%",
                "• 15分: 比率 <105% (無顯著槓桿)\n• 10分: 比率 105%~120%\n• 0分: 比率 >120% (槓桿過高)",
                "• 10分: 存續期 <3 年 (抗升息)\n• 5分: 存續期 3~6 年\n• 0分: 存續期 >6 年",
                "• 10分: 現金 >10% 且營運 Cash Flow 為正\n• 5分: 現金 5%~10%\n• 0分: 現金 <5% 或流動性緊縮",
                "• 10分: 前持倉 <20% (極分散)\n• 5分: 前持倉 20%~30%\n• 0分: 前持倉 >30%",
                "• 10分: 全額對衝且衍生品虧損 <1% NAV\n• 5分: 部分對衝\n• 0分: 未對衝且外幣曝險過高",
                "• 5分: 單一區域 <40%\n• 2.5分: 單一區域 40%~60%\n• 0分: 單一區域 >60%",
                "• 5分: 管理費 <1.0%\n• 2.5分: 管理費 1.0%~1.5%\n• 0分: 管理費 >1.5%"
            ],
            "霸菱基金真實數據與解析": [
                "• ROC 比例：42.2% ~ 59.2%\n• 2025總回報：+9.19% | 派息率：~9.87%\n👉 2025帳面營運淨利 (3.74億美元) 遠高於派息總額 (1.0億美元)，總回報幾乎完全覆蓋派息，緩衝池實質擴大。",
                "• 平均評級：BB\n• Ba 級 37.91%、B 級 33.75%\n• Caa1 及以下占 9.69%\n👉 標準高收益債配備，一次投資風險適中可控。",
                "• 總資產 / 淨資產：101.1%\n• Amounts due to broker 僅占 NAV 0.4%\n👉 幾乎無借貸槓桿，結構非常安全透明。",
                "• 最低修訂存續期：2.58 年\n👉 存續期極短，對央行利率變化的敏感度與衝擊較低。",
                "• 現金及等值：11.26% (約 5.5 億美元)\n• 2025營運現金流轉正 (+$2.11 億美元)\n👉 現金充沛，足以支應短期贖回需求。",
                "• 前十大發行人合計占：13.59%\n• 最大單一發行人 (Bausch Health) 僅占 2.40%\n👉 極度分散，有效避免單一公司黑天鵝事件。",
                "• 各非美元類別均提供衍生品對衝\n• 2025衍生品未實現淨利益 +$1,224 萬美元 (占 NAV 0.28%)\n👉 避險機制運作順暢，衍生品風險極低。",
                "• 北美地區：61.3% | 歐洲地區：23.8%\n👉 重倉北美/美國市場，受美國宏觀經濟與信用週期影響深遠。",
                "• G類別 (零售)：1.25% / 年\n• F類別 (法人)：0% / 年\n👉 屬於市場高收益債券基金的標準收費區間。"
            ],
            "得分 / 滿分": ["15 / 20", "10 / 15", "15 / 15", "10 / 10", "10 / 10", "10 / 10", "10 / 10", "0 / 5", "2.5 / 5"],
            "風險狀態": ["🟢 健康/觀察", "🟡 中等風險", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🟢 優秀", "🔴 集中度偏高", "🟡 中等"]
        },
        "top10": [
            {"排名": 1, "持倉名稱": "現金及等值資產 (Cash Equivalents)", "資產類別": "現金/貨幣市場", "佔比 (%)": 11.26},
            {"排名": 2, "持倉名稱": "Bausch Health Companies Inc.", "資產類別": "醫療保健債", "佔比 (%)": 2.40},
            {"排名": 3, "持倉名稱": "Charter Communications Inc.", "資產類別": "通訊服務債", "佔比 (%)": 1.71},
            {"排名": 4, "持倉名稱": "First Quantum Minerals Ltd", "資產類別": "基本工業債", "佔比 (%)": 1.66},
            {"排名": 5, "持倉名稱": "Uniti Group Inc.", "資產類別": "通訊基礎設施債", "佔比 (%)": 1.46},
        ]
    }
}

# 3. 頂部切換選單
ctrl_col1, ctrl_col2 = st.columns([2, 1])
with ctrl_col1:
    selected_preset = st.selectbox("📌 選擇評估標的基金：", list(PRESET_FUNDS.keys()))

curr_fund = PRESET_FUNDS[selected_preset]

# 4. 頂部 4 大 KPI 核心卡片（1:1 還原圖片樣式與顏色）
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">綜合風險評分</div>
            <div class="kpi-value-container">
                <span class="kpi-value">{curr_fund['score']}</span>
                <span class="kpi-subtext">/ 100</span>
            </div>
            <div class="badge-green">✔ 健康 (整體財務結構良好)</div>
        </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">資產槓桿水平</div>
            <div class="kpi-value">{curr_fund['kpi_leverage']}</div>
            <div class="badge-green">✔ 優秀 (無顯著借貸槓桿)</div>
        </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">現金與流動性</div>
            <div class="kpi-value">{curr_fund['kpi_cash']}</div>
            <div class="badge-green">✔ 優秀 (~5.5億美元現金儲備)</div>
        </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">從資本派息 (ROC) 狀況</div>
            <div class="kpi-value">{curr_fund['kpi_roc']}</div>
            <div class="badge-green">🟢 總回報覆蓋率佳 (緩衝池擴大)</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. 下方 9 大維度風險評估明細表 (1:1 對齊照片標題與結構)
st.markdown('<div class="section-header">📋 9 大維度風險評估明細表</div>', unsafe_allow_html=True)

df_mock = pd.DataFrame(curr_fund["mock_data"])

st.dataframe(
    df_mock[["評估維度", "具體檢查指標", "專屬評分簡算規則", "霸菱基金真實數據與解析", "得分 / 滿分", "風險狀態"]],
    use_container_width=True,
    hide_index=True,
    height=480
)

# 6. 底部總得分匯總列 (1:1 對齊照片底部)
st.markdown("""
    <div style="background-color: #F1F5F9; border-radius: 6px; padding: 12px 20px; display: flex; justify-content: flex-end; align-items: center; gap: 20px; font-weight: 700; color: #1E293B;">
        <span>總得分 / 得分率：</span>
        <span style="font-size: 20px; color: #0284C7;">82.5 / 100</span>
        <span style="background-color: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 12px; font-size: 14px;">82.5% (健康)</span>
    </div>
""", unsafe_allow_html=True)
