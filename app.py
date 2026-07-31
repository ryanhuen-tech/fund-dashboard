import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定（寬螢幕模式）
st.set_page_config(
    page_title="智能基金風險評估系統", 
    page_icon="🛡️", 
    layout="wide"
)

# 自訂 CSS：隱藏上下邊界，優化表格文字排版
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# 模擬數據（霸菱環球高收益債券基金 - 包含具體檢查指標與評分準則）
mock_data = {
    "維度": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、國家/宏觀風險", "九、總開支比率"],
    "具體檢查指標": [
        "派息來自資本 (ROC) 比例",
        "投資組合平均信貸評級",
        "衍生工具及總槓桿比率",
        "修訂存續期 (Duration)",
        "現金及高流動性資產佔比",
        "前十大持倉總集中的比例",
        "非對沖外幣資產曝險",
        "單一國家/區域持倉集中度",
        "經常性開支比率 (TER)"
    ],
    "評分準則": [
        "ROC<10% (20分); 10-30% (15分); >30% (10分)",
        "AAA/AA (15分); A/BBB (12分); BB/B (8分); <CCC (0分)",
        "無槓桿/僅對沖 (15分); 槓桿<20% (10分); >50% (0分)",
        "存續期<3年 (10分); 3-6年 (7分); >6年 (3分)",
        "現金>10% (10分); 5-10% (7分); <5% (3分)",
        "前十持倉<30% (10分); 30-50% (6分); >50% (0分)",
        "已完全對沖/無外匯風險 (10分); 未對沖>20% (3分)",
        "單一國家<40% (5分); 40-60% (3分); >60% (0分)",
        "TER<1.0% (5分); 1.0-1.5% (3分); >1.5% (0分)"
    ],
    "實際數據": [
        "47.39% 來自資本 (食老本)", 
        "平均評級 BB (高收益債)", 
        "無過度槓桿 (安全)", 
        "存續期 2.58 年 (防禦力強)", 
        "現金及等值 11.26% (充裕)", 
        "最大持倉 2.40% (分散)", 
        "基礎貨幣已對沖", 
        "北美佔比 61.3% (極度集中)", 
        "經常性開支比率 1.33%"
    ],
    "實際得分": [10, 8, 15, 10, 10, 10, 10, 0, 3],
    "滿分": [20, 15, 15, 10, 10, 10, 10, 5, 5],
    "狀態": ["⚠️ 警示", "⚠️ 警示", "✅ 優秀", "✅ 優秀", "✅ 優秀", "✅ 優秀", "✅ 優秀", "🚨 極高風險", "⚠️ 警示"]
}

# 2. 頂部工具列：主標題與搜尋按鈕並排
st.title("🛡️ 智能基金風險評估系統")

# 使用橫向 3 欄式設計放置搜尋功能
s_col1, s_col2, s_col3 = st.columns([2, 2, 1])

with s_col1:
    fund_code = st.text_input("輸入基金代號 / ISIN", value="IE00BFM0MQ22", label_visibility="collapsed")

with s_col2:
    fund_type = st.selectbox("選擇基金類別", ["債券型基金", "股票型基金"], label_visibility="collapsed")

with s_col3:
    analyze_btn = st.button("🔄 執行評估", type="primary", use_container_width=True)

st.markdown("---")

# 3. KPI 關鍵指標卡片 (4 欄配置)
total_score = sum(mock_data["實際得分"])

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="🛡️ 風險健康總分", value=f"{total_score} / 100", delta="-24 分 (扣分項)", delta_color="inverse")

with kpi2:
    st.metric(label="⚠️ 派息食老本比例", value="47.39%", delta="高風險警示", delta_color="inverse")

with kpi3:
    st.metric(label="💧 流動性緩衝 (現金)", value="11.26%", delta="資產充裕", delta_color="normal")

with kpi4:
    st.metric(label="⏳ 利率敏感度 (久期)", value="2.58 年", delta="抗加息力強", delta_color="normal")

st.markdown("---")

# 4. 中間核心區：雷達圖與表格並排（1:1.2 比例優化表格閱讀）
col_chart, col_table = st.columns([1, 1.3], gap="medium")

with col_chart:
    st.subheader("🕸️ 風險維度雷達圖")
    df_chart = pd.DataFrame(dict(
        Score=mock_data["實際得分"],
        Dimension=mock_data["維度"]
    ))
    
    fig = px.line_polar(
        df_chart,
        r='Score',
        theta='Dimension',
        line_close=True,
        markers=True,
        range_r=[0, 20],
        template="plotly_dark",
        color_discrete_sequence=['#00E676']
    )
    fig.update_traces(
        fill='toself',
        fillcolor='rgba(0, 230, 118, 0.3)',
        line=dict(color='#00E676', width=2),
        marker=dict(size=6, color='#00E676')
    )
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        polar=dict(radialaxis=dict(visible=True, range=[0, 20], showticklabels=False))
    )
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    st.subheader("📋 風險評估項目")
    df_table = pd.DataFrame(mock_data)
    
    # 顯示包含檢查指標與評分準則的詳細表格
    st.dataframe(
        df_table[["維度", "具體檢查指標", "評分準則", "實際數據", "實際得分", "滿分", "狀態"]],
        use_container_width=True,
        hide_index=True,
        height=420
    )

# 5. 底部：系統洞察點評
st.info("**💡 系統智能洞察**：該基金具備極佳的流動性與抗加息能力（久期極短），但投資者需密切注意其「派息質量」。近半數派息源於本金，長期持有恐面臨淨值慢性侵蝕。此外，單一北美市場曝險過高，需與您的整體資產配置進行宏觀對沖。")
