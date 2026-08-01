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

    /* 統一 HTML 表格樣式 (靠左對齊 + 深藍標頭) */
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
        vertical-align: middle;
        color: #334155;
        line-height: 1.6;
        text-align: left;
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
        "summary": "霸菱環球高收益債券基金綜合風險評分為 82.5 分 (健康)。資產槓桿率 101.1% 幾乎無借貸槓桿，現金儲備 11.26% 充沛 (約5.5億美元)，最低修訂存續期 2.58 年對利率敏感度低；但需留意平均評級為 BB 級 (高收益債/非投資級)，且派息率 (9.87%) 高於底層到期收益率，存在本金補貼缺口。",
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
            {"排名": 1, "持倉名稱": "現金及等值資產 (Cash Equivalents)", "資產類別": "現金/貨幣市場", "佔比 (%)": "11.26%"},
            {"排名": 2, "持倉名稱": "Bausch Health Companies Inc.", "資產類別": "醫療保健債", "佔比 (%)": "2.40%"},
            {"排名": 3, "持倉名稱": "Charter Communications Inc.", "資產類別": "通訊服務債", "佔比 (%)": "1.71%"},
            {"排名": 4, "持倉名稱": "First Quantum Minerals Ltd", "資產類別": "基本工業債", "佔比 (%)": "1.66%"},
            {"排名": 5, "持倉名稱": "Uniti Group Inc.", "資產類別": "通訊基礎設施債", "佔比 (%)": "1.46%"},
            {"排名": 6, "持倉名稱": "Radiology Partners", "資產類別": "醫療保健債", "佔比 (%)": "1.31%"},
            {"排名": 7, "持倉名稱": "LifePoint Health", "資產類別": "醫療保健債", "佔比 (%)": "1.27%"},
            {"排名": 8, "持倉名稱": "EchoStar", "資產類別": "衛星通訊債", "佔比 (%)": "1.25%"},
            {"排名": 9, "持倉名稱": "Herbalife Ltd.", "資產類別": "非必需消費債", "佔比 (%)": "1.10%"},
            {"排名": 10, "持倉名稱": "PRA Group", "資產類別": "金融服務債", "佔比 (%)": "1.06%"},
        ],
        "history_div": [
            ["30/06/2026", "01/07/2026", "08/07/2026", "0.578980", "73.11", "9.93%"],
            ["29/05/2026", "02/06/2026", "08/06/2026", "0.578980", "73.55", "9.87%"],
            ["30/04/2026", "01/05/2026", "08/05/2026", "0.578980", "73.73", "9.84%"],
            ["31/03/2026", "01/04/2026", "09/04/2026", "0.578980", "73.39", "9.89%"],
            ["27/02/2026", "02/03/2026", "06/03/2026", "0.578980", "74.51", "9.73%"],
            ["30/01/2026", "03/02/2026", "09/02/2026", "0.593352", "75.02", "9.92%"],
            ["31/12/2025", "02/01/2026", "08/01/2026", "0.593352", "74.92", "9.93%"],
            ["28/11/2025", "01/12/2025", "05/12/2025", "0.593352", "74.87", "9.94%"],
            ["31/10/2025", "03/11/2025", "07/11/2025", "0.593352", "75.19", "9.89%"],
            ["30/09/2025", "01/10/2025", "07/10/2025", "0.593352", "75.85", "9.80%"],
            ["29/08/2025", "02/09/2025", "08/09/2025", "0.593352", "75.70", "9.82%"],
            ["31/07/2025", "01/08/2025", "08/08/2025", "0.593352", "75.61", "9.83%"]
        ],
        "composition_div": [
            ["05-2026", "0.578980", "52.61%", "47.39%"],
            ["04-2026", "0.578980", "55.51%", "44.49%"],
            ["03-2026", "0.578980", "57.81%", "42.19%"],
            ["02-2026", "0.578980", "52.16%", "47.84%"],
            ["01-2026", "0.593352", "50.79%", "49.21%"],
            ["12-2025", "0.593352", "48.35%", "51.65%"],
            ["11-2025", "0.593352", "53.82%", "46.18%"],
            ["10-2025", "0.593352", "47.31%", "52.69%"],
            ["09-2025", "0.593352", "47.88%", "52.12%"],
            ["08-2025", "0.593352", "55.34%", "44.66%"],
            ["07-2025", "0.593352", "53.51%", "46.49%"],
            ["06-2025", "0.593352", "40.80%", "59.20%"]
        ],
        "sector_dist": [
            ["電訊", "12.19%"],
            ["醫療保健", "11.69%"],
            ["能源", "9.38%"],
            ["金融服務", "6.91%"],
            ["媒體", "6.61%"],
            ["基本工業", "5.05%"],
            ["資本物品", "4.62%"],
            ["休閒", "4.49%"],
            ["服務", "4.47%"],
            ["科技及電子", "4.26%"]
        ],
        "rating_dist": [
            ["Baa及以上", "5.40%"],
            ["Ba", "37.91%"],
            ["B", "33.75%"],
            ["Caa1及以下", "9.69%"],
            ["尚未評級", "2.00%"],
            ["現金及等值", "11.26%"]
        ],
        "geo_dist_history": [
            {"月份": "25年6月", "北美": 66.2, "歐洲": 27.6, "其他地區": 1.6, "現金及等值": 4.6},
            {"月份": "25年9月", "北美": 67.4, "歐洲": 25.9, "其他地區": 2.4, "現金及等值": 4.3},
            {"月份": "25年12月", "北美": 66.7, "歐洲": 24.6, "其他地區": 2.7, "現金及等值": 6.0},
            {"月份": "26年3月", "北美": 68.3, "歐洲": 22.9, "其他地區": 3.1, "現金及等值": 5.7},
            {"月份": "26年5月", "北美": 61.3, "歐洲": 23.8, "其他地區": 3.6, "現金及等值": 11.3}
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
kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5, kpi_c6, kpi_c7 = st.columns(7)

if fund_type == "債券基金":
    with kpi_c1: st.metric(label="現時派息率", value=curr_fund['kpis']['p1'], delta="年化分派", delta_color="normal")
    with kpi_c2: st.metric(label="派息與收益息差", value=curr_fund['kpis']['p2'], delta="⚠️ 存在本金補貼風險", delta_color="inverse")
    with kpi_c3: st.metric(label="平均持有債務評級", value=curr_fund['kpis']['p3'], delta="⚠️ 高收益債 (非投資級)", delta_color="inverse")
    with kpi_c4: st.metric(label="續存率 / 有效期", value=curr_fund['kpis']['p4'], delta="存續期 (久期)", delta_color="normal")
    with kpi_c5: st.metric(label="手持現金比率", value=curr_fund['kpis']['p5'], delta="流動性充沛", delta_color="normal")
    with kpi_c6: st.metric(label="前十大發行人佔比", value=curr_fund['kpis']['p6'], delta="極度分散", delta_color="normal")
    with kpi_c7: st.metric(label="槓桿比率", value=curr_fund['kpis']['p7'], delta="無顯著借貸", delta_color="normal")
else:
    for c, title in zip([kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5, kpi_c6, kpi_c7], ["現時派息率", "息差 / Beta", "平均持股/債評級", "續存率 / 波動率", "手持現金比率", "前十大發行人佔比", "槓桿比率"]):
        with c: st.metric(label=title, value="待核對", delta="請上傳PDF")

st.markdown("<br>", unsafe_allow_html=True)

# 6. 風險維度分析及基金底層資產數據 (7 大 TAB)
st.markdown("### 📊 風險維度分析及基金底層資產數據")

main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6, main_tab7 = st.tabs([
    "🕸️ 風險維度雷達圖", 
    "📋 前十大持倉清單",
    "📅 歷史派息紀錄", 
    "💰 派息組成 (收益 vs 資本)", 
    "🏭 十大行業分佈 (%)", 
    "🛡️ 評級分佈 (%)",
    "🌍 地區分佈歷年走勢 (%)"
])

# Tab 1: 風險維度雷達圖
with main_tab1:
    if fund_type != "債券基金":
        st.info(f"💡 目前切換至【{fund_type}】，請上傳對應 Factsheet / 月報 PDF 後生成專屬風險雷達圖。")
    else:
        df_chart = pd.DataFrame(dict(Score=curr_fund["radar_scores"], Dimension=curr_fund["radar_dimensions"]))
        fig_radar = px.line_polar(df_chart, r='Score', theta='Dimension', line_close=True, markers=True, range_r=[0, 20], color_discrete_sequence=['#00E676'])
        fig_radar.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.35)', line=dict(color='#00E676', width=2.5), marker=dict(size=7, color='#00E676'))
        fig_radar.update_layout(
            height=480, margin=dict(l=60, r=60, t=30, b=30), paper_bgcolor="rgba(0,0,0,0)",
            polar=dict(bgcolor="#1E222D", radialaxis=dict(visible=True, range=[0, 20], showticklabels=False, gridcolor="#334155"), angularaxis=dict(tickfont=dict(size=13, color="#000000", family="Arial, sans-serif"), gridcolor="#334155"))
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# Tab 2: 前十大持倉清單
with main_tab2:
    top10_rows_html = "".join([f"<tr><td style='width: 10%;'><b>{row['排名']}</b></td><td style='width: 45%;'><b>{row['持倉名稱']}</b></td><td style='width: 30%;'>{row['資產類別']}</td><td style='width: 15%; font-weight: bold;'>{row['佔比 (%)']}</td></tr>" for row in curr_fund["top10"]])
    st.markdown(f"""
    <table class="custom-table">
        <thead><tr><th>排名</th><th>持倉名稱</th><th>資產類別</th><th>佔比 (%)</th></tr></thead>
        <tbody>{top10_rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

# Tab 3: 歷史派息紀錄
with main_tab3:
    h_rows = "".join([f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td><b>{r[3]}</b></td><td>{r[4]}</td><td style='font-weight:bold; color:#059669;'>{r[5]}</td></tr>" for r in curr_fund["history_div"]])
    st.markdown(f"""
    <table class="custom-table">
        <thead>
            <tr><th>記錄日</th><th>除息日</th><th>派息日</th><th>每單位股息 (美元)</th><th>除息日每單位資產淨值 (美元)</th><th>年度化派息率</th></tr>
        </thead>
        <tbody>{h_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

# Tab 4: 派息組成
with main_tab4:
    st.caption("📌 註：G類別美元分派(每月) - 該月份可分派淨收入股息 vs 由資本所分派之股息")
    c_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td style='font-weight:bold; color:#D97706;'>{r[3]}</td></tr>" for r in curr_fund["composition_div"]])
    st.markdown(f"""
    <table class="custom-table">
        <thead>
            <tr><th>月份 (For the month of)</th><th>每股股息 (Dividend per share)</th><th>該月份可分派之淨收入股息 %</th><th>由資本所分派之股息 % (ROC)</th></tr>
        </thead>
        <tbody>{c_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

# Tab 5: 十大行業分佈
with main_tab5:
    s_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td style='font-weight:bold; color:#1E3A8A;'>{r[1]}</td></tr>" for r in curr_fund["sector_dist"]])
    st.markdown(f"""
    <table class="custom-table" style="width: 50%;">
        <thead>
            <tr><th>行業類別 (十大行業)</th><th>佔市值 %</th></tr>
        </thead>
        <tbody>{s_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

# Tab 6: 評級分佈
with main_tab6:
    r_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td style='font-weight:bold; color:#1E3A8A;'>{r[1]}</td></tr>" for r in curr_fund["rating_dist"]])
    st.markdown(f"""
    <table class="custom-table" style="width: 50%;">
        <thead>
            <tr><th>信貸評級分佈</th><th>佔市值 %</th></tr>
        </thead>
        <tbody>{r_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

# Tab 7: 地區分佈歷年走勢 (%)
with main_tab7:
    col_chart_geo, col_table_geo = st.columns([1.2, 1])
    df_geo = pd.DataFrame(curr_fund["geo_dist_history"])
    with col_chart_geo:
        fig_geo = px.bar(
            df_geo, x='月份', y=['北美', '歐洲', '其他地區', '現金及等值'],
            title="地區分佈歷史變動走勢 (佔市值 %)",
            color_discrete_map={'北美': '#0B2545', '歐洲': '#10B981', '其他地區': '#94A3B8', '現金及等值': '#1E50A2'},
            template="plotly_white"
        )
        fig_geo.update_layout(height=380, barmode='stack', yaxis_title="佔比 (%)", legend_title_text="地區類別")
        st.plotly_chart(fig_geo, use_container_width=True)
    with col_table_geo:
        geo_rows = "".join([f"<tr><td><b>{r['月份']}</b></td><td>{r['北美']}%</td><td>{r['歐洲']}%</td><td>{r['其他地區']}%</td><td>{r['現金及等值']}%</td></tr>" for r in curr_fund["geo_dist_history"]])
        st.markdown(f"""
        <table class="custom-table">
            <thead>
                <tr><th>月份</th><th>北美 %</th><th>歐洲 %</th><th>其他地區 %</th><th>現金及等值 %</th></tr>
            </thead>
            <tbody>{geo_rows}</tbody>
        </table>
        """, unsafe_allow_html=True)

st.markdown("---")

# 7. 💡 【新增隱藏功能】：使用 st.expander 將「基金深度風險評估」表格可摺疊隱藏！
with st.expander("📋 點擊展開 / 折疊：基金深度風險評估明細表", expanded=True):
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
