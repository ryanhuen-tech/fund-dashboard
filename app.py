import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="智能基金風險評估系統", page_icon="🛡️", layout="wide")

# 2. 建立側邊欄
st.sidebar.header("🔍 基金搜尋與設定")
fund_code = st.sidebar.text_input("輸入基金代號 / ISIN", value="IE00BFM0MQ22")
analyze_btn = st.sidebar.button("執行風險評估")

# 模擬後台自動抓取的霸菱基金數據
mock_data = {
    "維度": ["派息質量", "信用風險", "槓桿水平", "利率敏感度", "流動性風險", "集中度", "匯率風險", "宏觀風險", "總開支比率"],
    "滿分": [20, 15, 15, 10, 10, 10, 10, 5, 5],
    "實際得分": [10, 8, 15, 10, 10, 10, 10, 0, 3],
    "實際數據": ["47.39%來自資本", "平均BB級", "無過度槓桿", "存續期2.58年", "現金11.26%", "最大持倉2.4%", "已對沖", "北美佔61.3%", "經常性開支1.33%"],
    "狀態": ["⚠️ 警告", "⚠️ 警告", "✅ 安全", "✅ 安全", "✅ 安全", "✅ 安全", "✅ 安全", "🚨 危險", "⚠️ 警告"]
}

if analyze_btn or fund_code:
    st.title(f"📊 基金風險評估報告: 霸菱環球高收益債券基金")
    st.markdown("---")

    # 3. 頂部看板 (KPI Metrics)
    col1, col2, col3, col4 = st.columns(4)
    total_score = sum(mock_data["實際得分"])
    
    col1.metric("風險健康總分", f"{total_score} / 100", "-24分 (扣分項)")
    col2.metric("派息食老本比例", "47.39%", "高風險", delta_color="inverse")
    col3.metric("流動性緩衝 (現金)", "11.26%", "極佳")
    col4.metric("利率敏感度 (久期)", "2.58年", "防禦力強")

    st.markdown("---")

    # 4. 核心視覺化與明細
    col_chart, col_table = st.columns([0.8, 1.2])

    with col_chart:
        st.subheader("🕸️ 風險維度雷達圖")
        # 繪製 Plotly 互動式雷達圖
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
        line=dict(color='#00E676', width=3),
        marker=dict(size=8, color='#00E676')
    )
    fig.update_layout(
        margin=dict(l=30, r=30, t=30, b=30),
        polar=dict(radialaxis=dict(visible=True, range=[0, 20]))
    )
    st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("📋 評估明細與系統判定")
        df_table = pd.DataFrame(mock_data)
        # 設定表格樣式
        st.dataframe(
            df_table[["維度", "實際數據", "實際得分", "滿分", "狀態"]],
            use_container_width=True,
            hide_index=True
        )
        
    # 5. 專家總結
    st.info("**💡 系統智能洞察：** 該基金具備極佳的流動性與抗加息能力（久期極短），但投資者需密切注意其「派息質量」。近半數派息源於本金，長期持有恐面臨淨值慢性侵蝕。此外，單一北美市場曝險過高，需與您的整體資產配置進行宏觀對沖。")
