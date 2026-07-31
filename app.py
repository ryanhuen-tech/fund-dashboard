import streamlit as st
import streamlit.components.v1 as components

# 1. 設定 Streamlit 頁面寬度和標題
st.set_page_config(
    page_title="霸菱 Umbrella Fund - 風險評估 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 2. 基金資料庫 (可自由擴充其他霸菱子基金數據)
# ---------------------------------------------------------
FUNDS_DATA = {
    "霸菱環球高收益債券基金 (Barings Global High Yield Bond Fund)": {
        "score": "82.5 / 100",
        "status": "🟢 健康 (財務結構良好)",
        "radar_scores": [75, 66.7, 100, 100, 100, 100, 100, 0, 50],
        "holdings": [
            ("1", "Bausch Health Companies Inc.", "2.40%", "最大單一持倉"),
            ("2", "Charter Communications Inc.", "1.71%", "媒體與電訊業"),
            ("3", "First Quantum Minerals Ltd", "1.66%", "基礎金屬與採礦"),
            ("4", "Uniti Group Inc.", "1.46%", "不動產/電訊基建"),
            ("5", "Radiology Partners", "1.31%", "醫療保健業"),
            ("6", "LifePoint Health", "1.27%", "醫療保健服務"),
            ("7", "EchoStar", "1.25%", "衛星與電訊服務"),
            ("8", "Herbalife Ltd.", "1.10%", "消費品/保健品"),
            ("9", "PRA Group", "1.06%", "金融服務業"),
            ("10", "Novolex Holdings, Inc.", "1.02%", "基礎工業/包裝材料"),
        ],
        "top10_total": "13.59%",
    },
    "霸菱環球優先順位債券基金 (Barings Global Senior Secured Bond Fund)": {
        "score": "85.0 / 100",
        "status": "🟢 優秀 (優先受償權/擔保度高)",
        "radar_scores": [80, 80, 100, 100, 90, 100, 100, 0, 50],
        "holdings": [
            ("1", "TransDigm Inc.", "2.10%", "航空航天優先債"),
            ("2", "Medline Industries", "1.85%", "醫療保健優先債"),
            ("3", "AthenaHealth", "1.50%", "醫療資訊服務"),
            ("4", "Mozart Borrower LP", "1.42%", "醫療保健服務"),
            ("5", "Hub International", "1.35%", "保險經紀服務"),
        ],
        "top10_total": "15.20%",
    },
}

# ---------------------------------------------------------
# 3. Streamlit 原生頂部與側邊欄選單
# ---------------------------------------------------------
st.sidebar.title("🔍 基金選擇")
selected_fund_name = st.sidebar.selectbox(
    "請選擇欲評估的霸菱基金：", list(FUNDS_DATA.keys())
)

st.title("📊 霸菱 Umbrella Fund Plc - 風險評估 Dashboard")
st.markdown(f"### 當前檢視：**{selected_fund_name}**")

# 讀取當前選擇基金的數據
current_fund = FUNDS_DATA[selected_fund_name]

# ---------------------------------------------------------
# 4. 動態生成 HTML / Chart.js Dashboard
# ---------------------------------------------------------
# 組裝前十大持倉的 HTML 表格列
holdings_html = ""
for rank, issuer, weight, note in current_fund["holdings"]:
    holdings_html += f"<tr><td>{rank}</td><td>{issuer}</td><td>{weight}</td><td>{note}</td></tr>"

dashboard_html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary-color: #1f4e78;
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-main: #2d3748;
            --text-muted: #718096;
            --border-color: #e2e8f0;
            --success-color: #38a169;
            --warning-color: #dd6b20;
            --danger-color: #e53e3e;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }}
        body {{ background-color: var(--bg-color); color: var(--text-main); padding: 5px; line-height: 1.5; }}
        
        .top-section {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        @media (max-width: 900px) {{ .top-section {{ grid-template-columns: 1fr; }} }}
        
        .card {{ background: var(--card-bg); border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid var(--border-color); margin-bottom: 20px; }}
        .card-title {{ font-size: 1.1rem; color: var(--primary-color); margin-bottom: 16px; font-weight: bold; }}
        .chart-container {{ position: relative; height: 310px; width: 100%; display: flex; justify-content: center; }}
        
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; }}
        th {{ background-color: var(--primary-color); color: white; padding: 10px 14px; font-weight: 600; }}
        td {{ padding: 10px 14px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }}
        tr:hover {{ background-color: #f8fafc; }}
        
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
        .badge-good {{ background-color: #c6f6d5; color: #22543d; }}
        .badge-warn {{ background-color: #feebc8; color: #742a2a; }}
        .badge-alert {{ background-color: #fed7d7; color: #9b2c2c; }}
        .score-pill {{ font-weight: bold; color: var(--primary-color); }}
        .bullet-list {{ padding-left: 16px; }}
    </style>
</head>
<body>

<div class="container">
    <!-- 1. 上方：雷達圖 + 持倉 -->
    <div class="top-section">
        <div class="card">
            <div class="card-title">🕸️ 風險維度雷達圖 (得分率 %)</div>
            <div class="chart-container">
                <canvas id="riskRadarChart"></canvas>
            </div>
        </div>

        <div class="card">
            <div class="card-title">📋 前十大持倉清單</div>
            <div style="max-height: 310px; overflow-y: auto;">
                <table>
                    <thead>
                        <tr><th>#</th><th>發行人 (Issuer)</th><th>持倉占比 (%)</th><th>風險備註</th></tr>
                    </thead>
                    <tbody>
                        {holdings_html}
                        <tr style="background-color: #f7fafc; font-weight: bold;">
                            <td colspan="2">前十大持倉合計</td>
                            <td>{current_fund['top10_total']}</td>
                            <td><span class="badge badge-good">極度分散</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- 2. 下方：深度風險評估明細 -->
    <div class="card">
        <div class="card-title">📋 「底層資產」深度風險評估明細</div>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th style="width: 12%;">評估維度</th>
                        <th style="width: 16%;">具體檢查指標</th>
                        <th style="width: 25%;">專屬評分簡算規則</th>
                        <th style="width: 32%;">真實數據與解析</th>
                        <th style="width: 8%;">得分/滿分</th>
                        <th style="width: 7%;">風險狀態</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>一、派息質量</strong></td>
                        <td>從資本派息 (ROC) 與總回報覆蓋率</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>20分</b>: ROC &lt;10% 或 總回報 &ge; 派息率</li>
                                <li><b>10分</b>: ROC 10%~50% 且總回報覆蓋率 &gt;70%</li>
                                <li><b>0分</b>: ROC &gt;50% 且 總回報為負</li>
                            </ul>
                        </td>
                        <td>
                            • ROC 比例：<b>42.2% ~ 59.2%</b><br>
                            • 2025總回報：<b>+9.19%</b> | 派息率：<b>~9.87%</b><br>
                            👉 2025帳面營運淨利（3.74億美元）遠高於派息總額（1.0億美元），總回報幾乎完全覆蓋派息，緩衝池實質擴大。
                        </td>
                        <td><span class="score-pill">15</span> / 20</td>
                        <td><span class="badge badge-good">🟢 健康/觀察</span></td>
                    </tr>
                    <tr>
                        <td><strong>二、信用風險</strong></td>
                        <td>評級分佈與非投資級占比</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>15分</b>: 平均評級 BBB 以上</li>
                                <li><b>10分</b>: 平均評級 BB 級</li>
                                <li><b>5分</b>: Caa/CCC級 &gt;10% 或未評級 &gt;15%</li>
                            </ul>
                        </td>
                        <td>
                            • 平均評級：<b>BB</b><br>
                            • Ba 級 37.91%、B 級 33.75%<br>
                            • Caa1 及以下占 9.69%<br>
                            👉 標準高收益債配備，次投資級風險適中可控。
                        </td>
                        <td><span class="score-pill">10</span> / 15</td>
                        <td><span class="badge badge-warn">⚠️ 中等風險</span></td>
                    </tr>
                    <tr>
                        <td><strong>三、槓桿水平</strong></td>
                        <td>資產膨脹率 (Total / Net Assets)</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>15分</b>: 比率 &lt;105% (無顯著槓桿)</li>
                                <li><b>10分</b>: 比率 105%~120%</li>
                                <li><b>0分</b>: 比率 &gt;120% (槓桿過高)</li>
                            </ul>
                        </td>
                        <td>
                            • 總資產 / 淨資產：<b>101.1%</b><br>
                            • Amounts due to broker 僅占 NAV 0.4%<br>
                            👉 幾乎無借貸槓桿，結構非常安全透明。
                        </td>
                        <td><span class="score-pill">15</span> / 15</td>
                        <td><span class="badge badge-good">✅ 優秀</span></td>
                    </tr>
                    <tr>
                        <td><strong>四、利率敏感度</strong></td>
                        <td>有效存續期 (Duration)</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>10分</b>: 存續期 &lt;3 年 (抗升息)</li>
                                <li><b>5分</b>: 存續期 3~6 年</li>
                                <li><b>0分</b>: 存續期 &gt;6 年</li>
                            </ul>
                        </td>
                        <td>
                            • 最低修訂存續期：<b>2.58 年</b><br>
                            👉 天期極短，對央行利率變化的敏感度與衝擊較低。
                        </td>
                        <td><span class="score-pill">10</span> / 10</td>
                        <td><span class="badge badge-good">✅ 優秀</span></td>
                    </tr>
                    <tr>
                        <td><strong>五、流動性風險</strong></td>
                        <td>現金儲備與營運現金流</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>10分</b>: 現金 &gt;10% 且營運 Cash Flow 為正</li>
                                <li><b>5分</b>: 現金 5%~10%</li>
                                <li><b>0分</b>: 現金 &lt;5% 或流動性緊縮</li>
                            </ul>
                        </td>
                        <td>
                            • 現金及等值：<b>11.26%</b>（約 5.5 億美元）<br>
                            • 2025年營運現金流轉正（+$2.11 億美元）<br>
                            👉 現金池充沛，足以支應短期贖回需求。
                        </td>
                        <td><span class="score-pill">10</span> / 10</td>
                        <td><span class="badge badge-good">✅ 優秀</span></td>
                    </tr>
                    <tr>
                        <td><strong>六、集中度風險</strong></td>
                        <td>前十大發行人持倉占比</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>10分</b>: 前持倉 &lt;20% (極分散)</li>
                                <li><b>5分</b>: 前持倉 20%~30%</li>
                                <li><b>0分</b>: 前持倉 &gt;30%</li>
                            </ul>
                        </td>
                        <td>
                            • 前十大發行人合計占：<b>13.59%</b><br>
                            • 最大單一發行人 (Bausch Health) 僅占 2.40%<br>
                            👉 極度分散，有效避免單一公司爆雷引發連鎖反應。
                        </td>
                        <td><span class="score-pill">10</span> / 10</td>
                        <td><span class="badge badge-good">✅ 優秀</span></td>
                    </tr>
                    <tr>
                        <td><strong>七、匯率風險</strong></td>
                        <td>衍生品對衝與未實現損益</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>10分</b>: 全額對衝且衍生品虧損 &lt;1% NAV</li>
                                <li><b>5分</b>: 部分對衝</li>
                                <li><b>0分</b>: 未對衝且外幣曝險過高</li>
                            </ul>
                        </td>
                        <td>
                            • 各非美元類別均提供衍生品對衝<br>
                            • 2025衍生品未實現淨利益 <b>+$1,224 萬美元</b>（占 NAV <b>0.28%</b>）<br>
                            👉 避險機制運作順暢，衍生品風險極低。
                        </td>
                        <td><span class="score-pill">10</span> / 10</td>
                        <td><span class="badge badge-good">✅ 優秀</span></td>
                    </tr>
                    <tr>
                        <td><strong>八、區域風險</strong></td>
                        <td>單一區域/國家持倉集中度</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>5分</b>: 單一區域 &lt;40%</li>
                                <li><b>2.5分</b>: 單一區域 40%~60%</li>
                                <li><b>0分</b>: 單一區域 &gt;60%</li>
                            </ul>
                        </td>
                        <td>
                            • <b>北美地區：61.3%</b> | 歐洲地區：23.8%<br>
                            👉 重倉北美/美國市場，受美國宏觀經濟與信用週期影響深遠。
                        </td>
                        <td><span class="score-pill">0</span> / 5</td>
                        <td><span class="badge badge-alert">🚨 集中度偏高</span></td>
                    </tr>
                    <tr>
                        <td><strong>九、總開支比率</strong></td>
                        <td>每年管理費 (Management Fee)</td>
                        <td>
                            <ul class="bullet-list">
                                <li><b>5分</b>: 管理費 &lt;1.0%</li>
                                <li><b>2.5分</b>: 管理費 1.0%~1.5%</li>
                                <li><b>0分</b>: 管理費 &gt;1.5%</li>
                            </ul>
                        </td>
                        <td>
                            • G類別（零售）：<b>1.25% / 年</b><br>
                            • F類別（法人）：0% / 年<br>
                            👉 屬於市場高收益債券基金的標準收費區間。
                        </td>
                        <td><span class="score-pill">2.5</span> / 5</td>
                        <td><span class="badge badge-warn">⚠️ 中等</span></td>
                    </tr>
                    <tr style="background-color: #f7fafc; font-weight: bold;">
                        <td colspan="4" style="text-align: right;">綜合評分：</td>
                        <td style="color: var(--primary-color);">{current_fund['score']}</td>
                        <td><span class="badge badge-good">{current_fund['status']}</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
    const ctx = document.getElementById('riskRadarChart').getContext('2d');
    new Chart(ctx, {{
        type: 'radar',
        data: {{
            labels: ['一、派息質量', '二、信用風險', '三、槓桿水平', '四、利率敏感度', '五、流動性風險', '六、集中度風險', '七、匯率風險', '八、區域風險', '九、總開支比率'],
            datasets: [{{
                label: '維度得分率 (%)',
                data: {current_fund['radar_scores']},
                backgroundColor: 'rgba(56, 161, 105, 0.25)',
                borderColor: '#38a169',
                borderWidth: 2,
                pointBackgroundColor: '#1f4e78'
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{ r: {{ suggestedMin: 0, suggestedMax: 100, ticks: {{ display: false }} }} }},
            plugins: {{ legend: {{ display: false }} }}
        }}
    }});
</script>

</body>
</html>
"""

# 在 Streamlit 中渲染 HTML Dashboard
components.html(dashboard_html, height=1350, scrolling=True)
