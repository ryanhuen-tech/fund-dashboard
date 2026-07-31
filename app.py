import streamlit as st
import streamlit.components.v1 as components

# 1. 設定 Streamlit 頁面寬度和標題
st.set_page_config(
    page_title="霸菱環球高收益債券基金 - 風險評估 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. 定義 HTML/CSS/JS 代碼（包在 Python 三引號字串中以避免 SyntaxError）
dashboard_html = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>霸菱環球高收益債券基金 - 風險評估 Dashboard</title>
    <!-- 引入 Chart.js 用於繪製雷達圖 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #1f4e78;
            --secondary-color: #2b6cb0;
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-main: #2d3748;
            --text-muted: #718096;
            --border-color: #e2e8f0;
            --success-color: #38a169;
            --warning-color: #dd6b20;
            --danger-color: #e53e3e;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 10px;
            line-height: 1.5;
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
        }

        header {
            margin-bottom: 20px;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }

        h1 {
            color: var(--primary-color);
            font-size: 1.8rem;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        /* 頂部兩大模組區 (雷達圖 + 前十大持倉) */
        .top-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }

        @media (max-width: 900px) {
            .top-section {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
            margin-bottom: 20px;
        }

        .card-title {
            font-size: 1.1rem;
            color: var(--primary-color);
            margin-bottom: 16px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .chart-container {
            position: relative;
            height: 320px;
            width: 100%;
            display: flex;
            justify-content: center;
        }

        /* 表格通用樣式 */
        .table-responsive {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.88rem;
        }

        th {
            background-color: var(--primary-color);
            color: white;
            padding: 10px 14px;
            font-weight: 600;
        }

        td {
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }

        tr:hover {
            background-color: #f8fafc;
        }

        /* 標籤與狀態 */
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            text-align: center;
        }

        .badge-good { background-color: #c6f6d5; color: #22543d; }
        .badge-warn { background-color: #feebc8; color: #742a2a; }
        .badge-alert { background-color: #fed7d7; color: #9b2c2c; }

        .bullet-list {
            padding-left: 16px;
        }

        .bullet-list li {
            margin-bottom: 2px;
        }

        .score-pill {
            font-weight: bold;
            color: var(--primary-color);
        }
    </style>
</head>
<body>

<div class="container">
    <!-- 頁頭 -->
    <header>
        <div>
            <h1>霸菱環球高收益債券基金</h1>
            <p class="subtitle">Barings Global High Yield Bond Fund - 風險評估 Dashboard</p>
        </div>
        <div class="subtitle">綜合評分：<strong>82.5 / 100 (🟢 財務結構健康)</strong></div>
    </header>

    <!-- 1. 上方區域：雷達圖 + 前十大持倉 -->
    <div class="top-section">
        <!-- 左側：雷達圖 -->
        <div class="card">
            <div class="card-title">🕸️ 風險維度雷達圖 (得分率 %)</div>
            <div class="chart-container">
                <canvas id="riskRadarChart"></canvas>
            </div>
        </div>

        <!-- 右側：前十大持倉清單 -->
        <div class="card">
            <div class="card-title">📋 前十大持倉清單 (佔市值 %)</div>
            <div class="table-responsive" style="max-height: 320px; overflow-y: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>發行人 (Issuer)</th>
                            <th>持倉占比 (%)</th>
                            <th>風險備註</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>1</td><td>Bausch Health Companies Inc.</td><td>2.40%</td><td>最大單一持倉</td></tr>
                        <tr><td>2</td><td>Charter Communications Inc.</td><td>1.71%</td><td>媒體與電訊業</td></tr>
                        <tr><td>3</td><td>First Quantum Minerals Ltd</td><td>1.66%</td><td>基礎金屬與採礦</td></tr>
                        <tr><td>4</td><td>Uniti Group Inc.</td><td>1.46%</td><td>不動產/電訊基建</td></tr>
                        <tr><td>5</td><td>Radiology Partners</td><td>1.31%</td><td>醫療保健業</td></tr>
                        <tr><td>6</td><td>LifePoint Health</td><td>1.27%</td><td>醫療保健服務</td></tr>
                        <tr><td>7</td><td>EchoStar</td><td>1.25%</td><td>衛星與電訊服務</td></tr>
                        <tr><td>8</td><td>Herbalife Ltd.</td><td>1.10%</td><td>消費品/保健品</td></tr>
                        <tr><td>9</td><td>PRA Group</td><td>1.06%</td><td>金融服務業</td></tr>
                        <tr><td>10</td><td>Novolex Holdings, Inc.</td><td>1.02%</td><td>基礎工業/包裝材料</td></tr>
                        <tr style="background-color: #f7fafc; font-weight: bold;">
                            <td colspan="2">前十大持倉合計</td>
                            <td>13.59%</td>
                            <td><span class="badge badge-good">極度分散 (＜20%)</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- 2. 下方區域：「底層資產」深度風險評估明細表 -->
    <div class="card">
        <div class="card-title">📋 「底層資產」深度風險評估明細</div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th style="width: 12%;">評估維度</th>
                        <th style="width: 16%;">具體檢查指標</th>
                        <th style="width: 25%;">專屬評分簡算規則</th>
                        <th style="width: 32%;">霸菱基金真實數據與解析</th>
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

                    <!-- 加總列 -->
                    <tr style="background-color: #f7fafc; font-weight: bold; font-size: 0.95rem;">
                        <td colspan="4" style="text-align: right;">綜合評分 / 得分率：</td>
                        <td style="color: var(--primary-color);">82.5 / 100</td>
                        <td><span class="badge badge-good">82.5% (健康)</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Chart.js 雷達圖腳本 -->
<script>
    const ctx = document.getElementById('riskRadarChart').getContext('2d');
    
    const radarData = {
        labels: [
            '一、派息質量', 
            '二、信用風險', 
            '三、槓桿水平', 
            '四、利率敏感度', 
            '五、流動性風險', 
            '六、集中度風險', 
            '七、匯率風險', 
            '八、區域風險', 
            '九、總開支比率'
        ],
        datasets: [{
            label: '維度得分率 (%)',
            data: [75, 66.7, 100, 100, 100, 100, 100, 0, 50],
            backgroundColor: 'rgba(56, 161, 105, 0.25)',
            borderColor: '#38a169',
            borderWidth: 2,
            pointBackgroundColor: '#1f4e78',
            pointBorderColor: '#fff'
        }]
    };

    new Chart(ctx, {
        type: 'radar',
        data: radarData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: '#e2e8f0' },
                    grid: { color: '#cbd5e0' },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: { stepSize: 20, display: false },
                    pointLabels: { font: { size: 10, weight: 'bold' }, color: '#2d3748' }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
</script>

</body>
</html>
"""

# 3. 在 Streamlit 頁面上直接呈現 Dashboard (設定適當的容器高度與滾動功能)
components.html(dashboard_html, height=1350, scrolling=True)
