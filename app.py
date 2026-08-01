import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁頁面配置
st.set_page_config(
    page_title="智能基金風險評估系統", 
    page_icon="🛡️", 
    layout="wide"
)

# 2. 注入自訂 CSS 樣式
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .fund-header {
        background-color: #1E222D;
        padding: 14px 22px;
        border-radius: 8px;
        border-left: 5px solid #00E676;
        margin-bottom: 20px;
    }
    .source-tag {
        background-color: #00E676;
        color: #000;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
    }

    /* 頂部 7 大核心數據名片網格 */
    .kpi-grid-7 {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        margin-bottom: 25px;
    }
    .kpi-card-custom {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        border-top: 4px solid #1E3A8A;
    }
    .kpi-card-title {
        font-size: 11px;
        color: #64748B;
        font-weight: 700;
        margin-bottom: 4px;
        white-space: nowrap;
    }
    .kpi-card-value {
        font-size: 18px;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .kpi-card-sub {
        font-size: 10px;
        color: #059669;
        font-weight: 600;
    }

    /* HTML 右側表格樣式 */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #FFFFFF;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        margin-top: 10px;
        font-size: 13px;
    }
    .custom-table th {
        background-color: #1E3A8A;
        color: #FFFFFF;
        font-weight: 700;
        text-align: left;
        padding: 12px 14px;
        border-bottom: 2px solid #1E293B;
    }
    .custom-table td {
        padding: 12px 14px;
        border-bottom: 1px solid #E2E8F0;
        vertical-align: top;
        color: #334155;
        line-height: 1.6;
    }
    .custom-table tr:hover {
        background-color: #F8FAFC;
    }

    /* 狀態標籤 */
    .status-badge-green {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
        text-align: center;
    }
    .status-badge-yellow {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
        text-align: center;
    }
    .status-badge-red {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
        text-align: center;
    }

    /* 底部總分欄 */
    .summary-footer {
        background-color: #F1F5F9;
        padding: 14px 24px;
        border-radius: 0 0 8px 8px;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 15px;
        border: 1px solid #E2E8F0;
        border-top: none;
        margin-top: -1px;
        margin-bottom: 25px;
    }
    .summary-title {
        font-size: 14px;
        font-weight: 700;
        color: #334155;
    }
    .summary-score {
        font-size: 18px;
        font-weight: 800;
        color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ 智能基金風險評估系統")

# 3. 預設資料庫
PRESET_FUNDS = {
    "霸菱環球高收益債券基金": {
        "zh": "霸菱環球高收益債券基金",
        "en": "Barings Global High Yield Bond Fund",
        "score": "82.5",
        "summary": "霸菱環球高收益債券基金綜合風險評分為 82.5 分 (健康)。資產槓桿率 101.1% 幾乎無借貸槓桿，現金儲備 11.26% 充沛 (約5.5億美元)，最低修訂存續期 2.58 年對利率敏感度低；重倉北美 (61.3%) 區域集中度偏高，但整體財務結構與避險機制非常穩健。",
        "kpis": {
            "p1": "9.87%",
            "p2": "+2.64%",
            "p3": "BB 級",
            "p4": "2.58 年",
            "p5": "11.26%",
            "p6": "13.59%",
            "p7": "101.1%"
        },
        "radar_scores": [15.0, 10.0, 15.0, 10.0, 10.0, 10.0, 10.0, 0.0, 2.5],
        "radar_dimensions": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、區域風險", "九、總開支比率"],
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
    }
}

# 4. 最上方：選擇基金名稱與風險評估類別選單
ctrl_col1, ctrl_col2 = st.columns([1.8, 1.2])

with ctrl_col1:
    selected_preset = st.selectbox("📌 選擇評估標的基金名稱：", list(PRESET_FUNDS.keys()))

curr_fund = PRESET_FUNDS[selected_preset]

with ctrl_col2:
    fund_type = st.selectbox("📌 風險評估類別：", ["債券基金", "股票基金", "股債混合基金"], index=0)

# 醒目基金名稱抬頭
st.markdown(f"""
    <div class="fund-header">
        <span style="font-size: 13px; color: #888;">當前分析目標基金 ({fund_type})：</span> 
        <span class="source-tag">📍 客觀真實數據源 : {curr_fund['zh']}</span><br>
        <span style="font-size: 20px; font-weight: bold; color: #FFF;">{curr_fund['zh']}</span> 
        <span style="font-size: 14px; color: #AAA;">({curr_fund['en']})</span>
    </div>
""", unsafe_allow_html=True)

# 5. 核心數據名片 (7 大 KPI 名片卡片列)
if fund_type == "債券基金":
    st.markdown(f"""
    <div class="kpi-grid-7">
        <div class="kpi-card-custom"><div class="kpi-card-title">現時派息率</div><div class="kpi-card-value">{curr_fund['kpis']['p1']}</div><div class="kpi-card-sub">年化分派</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">派息率與加權收益息差</div><div class="kpi-card-value">{curr_fund['kpis']['p2']}</div><div class="kpi-card-sub">派息覆蓋佳</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">平均持有債務評級</div><div class="kpi-card-value">{curr_fund['kpis']['p3']}</div><div class="kpi-card-sub">高收益債</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">續存率 / 有效期</div><div class="kpi-card-value">{curr_fund['kpis']['p4']}</div><div class="kpi-card-sub">存續期 (久期)</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">手持現金比率</div><div class="kpi-card-value">{curr_fund['kpis']['p5']}</div><div class="kpi-card-sub">流動性充沛</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">前十大發行人佔比</div><div class="kpi-card-value">{curr_fund['kpis']['p6']}</div><div class="kpi-card-sub">極度分散</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">槓桿比率</div><div class="kpi-card-value">{curr_fund['kpis']['p7']}</div><div class="kpi-card-sub">無顯著借貸</div></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="kpi-grid-7">
        <div class="kpi-card-custom"><div class="kpi-card-title">現時派息率</div><div class="kpi-card-value">待核對</div><div class="kpi-card-sub">請上傳PDF</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">息差 / Beta</div><div class="kpi-card-value">待核對</div><div class="kpi-card-sub">請上傳PDF</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">平均持股/債評級</div><div class="kpi-card-value">待核對</div><div class="kpi-card-sub">請上傳PDF</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">續存率 / 波動率</div><div class="kpi-card-value">待核對</div><div class="kpi-card-sub">請上傳PDF</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">手持現金比率</div><div class="kpi-card-value">待核對</div><div class="kpi-card-sub">請上傳PDF</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">前十大發行人佔比</div><div class="kpi-card-value">待核對</div><div class="kpi-card-sub">請上傳PDF</div></div>
        <div class="kpi-card-custom"><div class="kpi-card-title">槓桿比率</div><div class="kpi-card-value">待核對</div><div class="kpi-card-sub">請上傳PDF</div></div>
    </div>
    """, unsafe_allow_html=True)

# 6. 【上區】：將「雷達圖」與「前十大持倉清單」放在風險評估表格上方！
st.markdown("### 🕸️ 風險維度分析與持倉分佈")

tab1, tab2 = st.tabs(["🕸️ 風險維度雷達圖", "📋 前十大持倉清單"])

with tab1:
    if fund_type != "債券基金":
        st.info(f"💡 目前切換至【{fund_type}】，請上傳對應 Factsheet / 月報 PDF 後生成專屬風險雷達圖。")
    else:
        df_chart = pd.DataFrame(dict(
            Score=curr_fund["radar_scores"], 
            Dimension=curr_fund["radar_dimensions"]
        ))
        # 💡 雷達圖文字徹底優化：文字使用【黑色 + 加粗 (#000000)】，背景改為亮色，清晰可見！
        fig_radar = px.line_polar(
            df_chart, 
            r='Score', 
            theta='Dimension', 
            line_close=True, 
            markers=True, 
            range_r=[0, 20], 
            template="plotly_white",  # 使用白底以凸顯黑色文字
            color_discrete_sequence=['#10B981']
        )
        fig_radar.update_traces(
            fill='toself', 
            fillcolor='rgba(16, 185, 129, 0.25)', 
            line=dict(color='#10B981', width=2.5), 
            marker=dict(size=7, color='#10B981')
        )
        fig_radar.update_layout(
            height=480, 
            margin=dict(l=60, r=60, t=30, b=30), 
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 20], showticklabels=False, gridcolor="#E2E8F0"),
                angularaxis=dict(
                    tickfont=dict(size=13, color="#000000", family="Arial, sans-serif"), # 黑色加粗字體！
                    gridcolor="#E2E8F0"
                )
            )
        )
        st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    df_top10 = pd.DataFrame(curr_fund["top10"])
    top10_total_pct = round(df_top10["佔比 (%)"].sum(), 2)
    st.metric(label="📌 前十大持倉合共佔比 (Top 10 Total)", value=f"{top10_total_pct}%", delta="持倉高度分散", delta_color="normal")
    st.dataframe(df_top10, use_container_width=True, hide_index=True, height=360)

st.markdown("---")

# 7. 【下區】：正式更名為「📋 基金深度風險評估」表格
st.markdown('### 📋 基金深度風險評估')

if fund_type == "債券基金":
    html_table = """
    <table class="custom-table">
        <thead>
            <tr>
                <th style="width: 14%;">評估維度</th>
                <th style="width: 18%;">具體檢查指標</th>
                <th style="width: 25%;">專屬評分簡算規則</th>
                <th style="width: 27%;">霸菱基金真實數據與解析</th>
                <th style="width: 8%; text-align: center;">得分/滿分</th>
                <th style="width: 8%; text-align: center;">風險狀態</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>一、派息質量</b></td>
                <td>從資本派息 (ROC) 與總回報覆蓋率</td>
                <td>• <b>20分</b>: ROC &lt;10% 或 總回報 ≥ 派息率<br>• <b>10分</b>: ROC 10%~50% 且總回報覆蓋率 &gt;70%<br>• <b>0分</b>: ROC &gt;50% 且 總回報為負</td>
                <td>• ROC 比例：<b>42.2% ~ 59.2%</b><br>• 2025總回報：<b>+9.19%</b> | 派息率：<b>~9.87%</b><br>👉 帳面營運淨利遠高於派息總額，總回報幾乎完全覆蓋派息。</td>
                <td style="text-align: center; font-weight: bold;">15 / 20</td>
                <td style="text-align: center;"><span class="status-badge-green">🟢 健康/觀察</span></td>
            </tr>
            <tr>
                <td><b>二、信用風險</b></td>
                <td>評級分佈與非投資級占比</td>
                <td>• <b>15分</b>: 平均評級 BBB 以上<br>• <b>10分</b>: 平均評級 BB 級<br>• <b>5分</b>: Caa/CCC級 &gt;10% 或未評級 &gt;15%</td>
                <td>• 平均評級：<b>BB</b><br>• Ba 級 <b>37.91%</b>、B 級 <b>33.75%</b><br>👉 標準高收益債配備，一次投資風險適中可控。</td>
                <td style="text-align: center; font-weight: bold;">10 / 15</td>
                <td style="text-align: center;"><span class="status-badge-yellow">⚠️ 中等風險</span></td>
            </tr>
            <tr>
                <td><b>三、槓桿水平</b></td>
                <td>資產膨脹率 (Total / Net Assets)</td>
                <td>• <b>15分</b>: 比率 &lt;105% (無顯著槓桿)<br>• <b>10分</b>: 比率 105%~120%<br>• <b>0分</b>: 比率 &gt;120% (槓桿過高)</td>
                <td>• 總資產 / 淨資產：<b>101.1%</b><br>👉 幾乎無借貸槓桿，結構非常安全透明。</td>
                <td style="text-align: center; font-weight: bold;">15 / 15</td>
                <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
            </tr>
            <tr>
                <td><b>四、利率敏感度</b></td>
                <td>有效存續期 (Duration)</td>
                <td>• <b>10分</b>: 存續期 &lt;3 年 (抗升息)<br>• <b>5分</b>: 存續期 3~6 年<br>• <b>0分</b>: 存續期 &gt;6 年</td>
                <td>• 最低修訂存續期：<b>2.58 年</b><br>👉 存續期極短，對央行利率變化的敏感度與衝擊較低。</td>
                <td style="text-align: center; font-weight: bold;">10 / 10</td>
                <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
            </tr>
            <tr>
                <td><b>五、流動性風險</b></td>
                <td>現金儲備與營運現金流</td>
                <td>• <b>10分</b>: 現金 &gt;10% 且營運 Cash Flow 為正<br>• <b>5分</b>: 現金 5%~10%<br>• <b>0分</b>: 現金 &lt;5% 或流動性緊縮</td>
                <td>• 現金及等值：<b>11.26%</b> (約 5.5 億美元)<br>👉 現金充沛，足以支應短期贖回需求。</td>
                <td style="text-align: center; font-weight: bold;">10 / 10</td>
                <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
            </tr>
            <tr>
                <td><b>六、集中度風險</b></td>
                <td>前十大發行人持倉占比</td>
                <td>• <b>10分</b>: 前持倉 &lt;20% (極分散)<br>• <b>5分</b>: 前持倉 20%~30%<br>• <b>0分</b>: 前持倉 &gt;30%</td>
                <td>• 前十大發行人合計占：<b>13.59%</b><br>• 最大單一發行人僅占 <b>2.40%</b><br>👉 極度分散，有效避免單一公司黑天鵝事件。</td>
                <td style="text-align: center; font-weight: bold;">10 / 10</td>
                <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
            </tr>
            <tr>
                <td><b>七、匯率風險</b></td>
                <td>衍生品對沖與未實現損益</td>
                <td>• <b>10分</b>: 全額對沖且衍生品虧損 &lt;1% NAV<br>• <b>5分</b>: 部分對沖<br>• <b>0分</b>: 未對沖且外幣曝險過高</td>
                <td>• 各非美元類別均提供衍生品對沖<br>👉 避險機制運作順暢，衍生品風險極低。</td>
                <td style="text-align: center; font-weight: bold;">10 / 10</td>
                <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
            </tr>
            <tr>
                <td><b>八、區域風險</b></td>
                <td>單一區域/國家持倉集中度</td>
                <td>• <b>5分</b>: 單一區域 &lt;40%<br>• <b>2.5分</b>: 單一區域 40%~60%<br>• <b>0分</b>: 單一區域 &gt;60%</td>
                <td>• 北美地區：<b>61.3%</b> | 歐洲地區：<b>23.8%</b><br>👉 重倉北美/美國市場，受美國信用週期影響深遠。</td>
                <td style="text-align: center; font-weight: bold;">0 / 5</td>
                <td style="text-align: center;"><span class="status-badge-red">🚨 集中度偏高</span></td>
            </tr>
            <tr>
                <td><b>九、總開支比率</b></td>
                <td>每年管理費 (Management Fee)</td>
                <td>• <b>5分</b>: 管理費 &lt;1.0%<br>• <b>2.5分</b>: 管理費 1.0%~1.5%<br>• <b>0分</b>: 管理費 &gt;1.5%</td>
                <td>• G類別 (零售)：<b>1.25% / 年</b><br>👉 屬於市場高收益債券基金的標準收費區間。</td>
                <td style="text-align: center; font-weight: bold;">2.5 / 5</td>
                <td style="text-align: center;"><span class="status-badge-yellow">⚠️ 中等</span></td>
            </tr>
        </tbody>
    </table>
    <div class="summary-footer">
        <span class="summary-title">總得分 / 得分率：</span>
        <span class="summary-score">82.5 / 100</span>
        <span class="status-badge-green" style="font-size: 13px; padding: 5px 12px;">82.5% (健康)</span>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)
else:
    # 📈 股票基金 / 股債混合基金 專屬「基金深度風險評估」表
    html_table = f"""
    <table class="custom-table">
        <thead>
            <tr>
                <th style="width: 16%;">評估維度</th>
                <th style="width: 22%;">具體檢查指標</th>
                <th style="width: 32%;">專屬評分簡算規則</th>
                <th style="width: 18%;">底層資產數據與解析</th>
                <th style="width: 12%; text-align: center;">風險狀態</th>
            </tr>
        </thead>
        <tbody>
            <tr><td><b>一、市場敏感度</b></td><td>貝塔係數 (β) / 股票比率</td><td>β &lt; 0.8 防禦=15分 | 0.8-1.2 適中=9分 | &gt;1.2 高波動=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
            <tr><td><b>二、極端回撤</b></td><td>最大回撤 (Max Drawdown)</td><td>回撤 &lt; 15%=15分 | 15%-25%=9分 | &gt; 25%=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
            <tr><td><b>三、持倉集中度</b></td><td>前十大重倉標的佔比</td><td>&lt; 30% 分散=10分 | 30%-50%=6分 | &gt; 50% 集中=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
            <tr><td><b>四、絕對波動控制</b></td><td>年度化標準差 / 組合久期</td><td>&lt; 10% 穩健=5分 | 10%-20%=3分 | &gt; 20% 高波動=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
            <tr><td><b>五、風險性價比</b></td><td>夏普比率 (Sharpe Ratio)</td><td>&gt; 1.0 優秀=10分 | 0.5-1.0 良好=6分 | &lt; 0.5 差=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
            <tr><td><b>六、經理穩定性</b></td><td>任職年限與團隊變更</td><td>&gt; 3年無變更=15分 | 1-3年=9分 | &lt; 1年/頻繁變更=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
            <tr><td><b>七、規模適中性</b></td><td>基金資產規模 (AUM)</td><td>2億-100億=10分 | 5000萬-2億或&gt;100億=6分 | &lt; 5000萬=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
            <tr><td><b>八、行業集中度</b></td><td>最大單一行業/資產占比</td><td>&lt; 20%=10分 | 20%-30%=6分 | &gt; 30% 高度集中=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
            <tr><td><b>九、匯率對沖曝險</b></td><td>外幣資產與對沖狀況</td><td>完全對沖=10分 | 部分對沖=5分 | 未對沖&gt;30%=0分</td><td>待上傳 PDF 核對</td><td style="text-align: center;"><span class="status-badge-yellow">📋 待核對</span></td></tr>
        </tbody>
    </table>
    <div class="summary-footer">
        <span class="summary-title">總得分 / 得分率：</span>
        <span class="summary-score">待核對 (0 / 100)</span>
        <span class="status-badge-yellow" style="font-size: 12px; padding: 4px 10px;">請上傳月報 PDF</span>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)

# 8. 底部智能洞察點評
st.info(f"**💡 AI 智能洞察 ({curr_fund['zh']})**：{curr_fund['summary']}")
