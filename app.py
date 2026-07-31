import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(
    page_title="智能基金風險評估系統", 
    page_icon="🛡️", 
    layout="wide"
)

# 2. 注入高質感 CSS 樣式（1:1 還原右圖視覺效果）
st.markdown("""
    <style>
    /* 全局背景 */
    .main {
        background-color: #F8FAFC;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 頂部 4 大 KPI 卡片樣式 */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        border-left: 5px solid #10B981;
    }
    .kpi-title {
        font-size: 12px;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .kpi-value-row {
        display: flex;
        align-items: baseline;
        gap: 6px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #1E3A8A;
    }
    .kpi-subtext {
        font-size: 14px;
        color: #64748B;
        font-weight: 600;
    }
    
    /* KPI 卡片內標籤 */
    .badge-green {
        background-color: #D1FAE5;
        color: #065F46;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
    }

    /* 右圖 9 大維度表格專用 HTML/CSS */
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

    /* 右圖右側得分與狀態標籤 */
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

# 3. 頂部抬頭與選擇區
st.title("🛡️ 智能基金風險評估系統")

ctrl_col1, ctrl_col2 = st.columns([2, 1])
with ctrl_col1:
    selected_fund = st.selectbox("📌 選擇評估標的基金：", ["霸菱環球高收益債券基金 (債券型)", "富達基金 - 美元高收益基金 (債券型)"])

# 4. 頂部 4 大 KPI 卡片 (1:1 對齊右圖頂部)
st.markdown("""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">綜合風險評分</div>
        <div class="kpi-value-row">
            <span class="kpi-value">82.5</span>
            <span class="kpi-subtext">/ 100</span>
        </div>
        <div class="badge-green">✔ 健康 (整體財務結構良好)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">資產槓桿水平</div>
        <div class="kpi-value-row">
            <span class="kpi-value">101.1%</span>
        </div>
        <div class="badge-green">✔ 優秀 (無顯著借貸槓桿)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">現金與流動性</div>
        <div class="kpi-value-row">
            <span class="kpi-value">11.26%</span>
        </div>
        <div class="badge-green">✔ 優秀 (~5.5億美元現金儲備)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">從資本派息 (ROC) 狀況</div>
        <div class="kpi-value-row">
            <span class="kpi-value">42%~59%</span>
        </div>
        <div class="badge-green">🟢 總回報覆蓋率佳 (緩衝池擴大)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. 右圖 1:1 精準 HTML/CSS 9 大維度風險評估明細表
st.markdown('### 📋 9 大維度風險評估明細表')

html_table = """
<table class="custom-table">
    <thead>
        <tr>
            <th style="width: 12%;">評估維度</th>
            <th style="width: 18%;">具體檢查指標</th>
            <th style="width: 25%;">專屬評分簡算規則</th>
            <th style="width: 27%;">霸菱基金真實數據與解析</th>
            <th style="width: 8%; text-align: center;">得分 / 滿分</th>
            <th style="width: 10%; text-align: center;">風險狀態</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><b>一、派息質量</b></td>
            <td>從資本派息 (ROC) 與總回報覆蓋率</td>
            <td>
                • <b>20分</b>: ROC &lt; 10% 或 總回報 ≥ 派息率<br>
                • <b>10分</b>: ROC 10%~50% 且總回報覆蓋率 &gt; 70%<br>
                • <b>0分</b>: ROC &gt; 50% 且 總回報為負
            </td>
            <td>
                • ROC 比例：<b>42.2% ~ 59.2%</b><br>
                • 2025總回報：<b>+9.19%</b> | 派息率：<b>~9.87%</b><br>
                👉 2025帳面營運淨利 (3.74億美元) 遠高於派息總額 (1.0億美元)，總回報幾乎完全覆蓋派息，緩衝池實質擴大。
            </td>
            <td style="text-align: center; font-weight: bold;">15 / 20</td>
            <td style="text-align: center;"><span class="status-badge-green">🟢 健康/觀察</span></td>
        </tr>
        <tr>
            <td><b>二、信用風險</b></td>
            <td>評級分佈與非投資級占比</td>
            <td>
                • <b>15分</b>: 平均評級 BBB 以上<br>
                • <b>10分</b>: 平均評級 BB 級<br>
                • <b>5分</b>: Caa/CCC級 &gt; 10% 或未評級 &gt; 15%
            </td>
            <td>
                • 平均評級：<b>BB</b><br>
                • Ba 級 <b>37.91%</b>、B 級 <b>33.75%</b><br>
                • Caa1 及以下占 <b>9.69%</b><br>
                👉 標準高收益債配備，一次投資風險適中可控。
            </td>
            <td style="text-align: center; font-weight: bold;">10 / 15</td>
            <td style="text-align: center;"><span class="status-badge-yellow">⚠️ 中等風險</span></td>
        </tr>
        <tr>
            <td><b>三、槓桿水平</b></td>
            <td>資產膨脹率 (Total / Net Assets)</td>
            <td>
                • <b>15分</b>: 比率 &lt; 105% (無顯著槓桿)<br>
                • <b>10分</b>: 比率 105%~120%<br>
                • <b>0分</b>: 比率 &gt; 120% (槓桿過高)
            </td>
            <td>
                • 總資產 / 淨資產：<b>101.1%</b><br>
                • Amounts due to broker 僅占 NAV <b>0.4%</b><br>
                👉 幾乎無借貸槓桿，結構非常安全透明。
            </td>
            <td style="text-align: center; font-weight: bold;">15 / 15</td>
            <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
        </tr>
        <tr>
            <td><b>四、利率敏感度</b></td>
            <td>有效存續期 (Duration)</td>
            <td>
                • <b>10分</b>: 存續期 &lt; 3年 (抗升息)<br>
                • <b>5分</b>: 存續期 3~6年<br>
                • <b>0分</b>: 存續期 &gt; 6年
            </td>
            <td>
                • 最低修訂存續期：<b>2.58 年</b><br>
                👉 存續期極短，對央行利率变化的敏感度與衝擊較低。
            </td>
            <td style="text-align: center; font-weight: bold;">10 / 10</td>
            <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
        </tr>
        <tr>
            <td><b>五、流動性風險</b></td>
            <td>現金儲備與營運現金流</td>
            <td>
                • <b>10分</b>: 現金 &gt; 10% 且營運 Cash Flow 為正<br>
                • <b>5分</b>: 現金 5%~10%<br>
                • <b>0分</b>: 現金 &lt; 5% 或流動性緊縮
            </td>
            <td>
                • 現金及等值：<b>11.26%</b> (約 5.5 億美元)<br>
                • 2025營運現金流轉正 (+ $2.11 億美元)<br>
                👉 現金充沛，足以支應短期贖回需求。
            </td>
            <td style="text-align: center; font-weight: bold;">10 / 10</td>
            <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
        </tr>
        <tr>
            <td><b>六、集中度風險</b></td>
            <td>前十大發行人持倉占比</td>
            <td>
                • <b>10分</b>: 前持倉 &lt; 20% (極分散)<br>
                • <b>5分</b>: 前持倉 20%~30%<br>
                • <b>0分</b>: 前持倉 &gt; 30%
            </td>
            <td>
                • 前十大發行人合計占：<b>13.59%</b><br>
                • 最大單一發行人 (Bausch Health) 僅占 <b>2.40%</b><br>
                👉 極度分散，有效避免單一公司黑天鵝事件。
            </td>
            <td style="text-align: center; font-weight: bold;">10 / 10</td>
            <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
        </tr>
        <tr>
            <td><b>七、匯率風險</b></td>
            <td>衍生品對衝與未實現損益</td>
            <td>
                • <b>10分</b>: 全額對衝且衍生品虧損 &lt; 1% NAV<br>
                • <b>5分</b>: 部分對衝<br>
                • <b>0分</b>: 未對衝且外幣曝險過高
            </td>
            <td>
                • 各非美元類別均提供衍生品對衝<br>
                • 2025衍生品未實現淨利益 <b>+$1,224 萬美元</b> (占 NAV <b>0.28%</b>)<br>
                👉 避險機制運作順暢，衍生品風險極低。
            </td>
            <td style="text-align: center; font-weight: bold;">10 / 10</td>
            <td style="text-align: center;"><span class="status-badge-green">✔ 優秀</span></td>
        </tr>
        <tr>
            <td><b>八、區域風險</b></td>
            <td>單一區域/國家持倉集中度</td>
            <td>
                • <b>5分</b>: 單一區域 &lt; 40%<br>
                • <b>2.5分</b>: 單一區域 40%~60%<br>
                • <b>0分</b>: 單一區域 &gt; 60%
            </td>
            <td>
                • 北美地區：<b>61.3%</b> | 歐洲地區：<b>23.8%</b><br>
                👉 重倉北美/美國市場，受美國宏觀經濟與信用週期影響深遠。
            </td>
            <td style="text-align: center; font-weight: bold;">0 / 5</td>
            <td style="text-align: center;"><span class="status-badge-red">🚨 集中度偏高</span></td>
        </tr>
        <tr>
            <td><b>九、總開支比率</b></td>
            <td>每年管理費 (Management Fee)</td>
            <td>
                • <b>5分</b>: 管理費 &lt; 1.0%<br>
                • <b>2.5分</b>: 管理費 1.0%~1.5%<br>
                • <b>0分</b>: 管理費 &gt; 1.5%
            </td>
            <td>
                • G類別 (零售)：<b>1.25% / 年</b><br>
                • F類別 (法人)：<b>0% / 年</b><br>
                👉 屬於市場高收益債券基金的標準收費區間。
            </td>
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
