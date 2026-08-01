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

# 3. 預設資料庫 (包含霸菱與富達真實 PDF 數據)
PRESET_FUNDS = {
    "富達基金 - 美元高收益基金": {
        "zh": "富達基金 - 美元高收益基金",
        "en": "Fidelity Funds - US High Yield Fund",
        "score": "82.5",
        "summary": "富達美元高收益基金綜合風險評分為 82.5 分 (健康)。過往一年申購 $12.65億 vs 贖回 $15.30億，出現 -$2,647.5 萬美元淨流出 (需關注資金流向)；但淨營運收益達 +$154.03M，完全覆蓋全年度股息分派 $74.28M；基金總資產達 $2,527 Million 美元，到期收益率為 7.23%，派息率約 7.42%；有效存續期僅 2.8 年抗升息力強[cite: 2]。",
        "kpis": {
            "p1": "7.42%",
            "p2": "+0.19%", "p2_delta": "🟢 息差小/收益覆蓋佳", "p2_color": "normal",
            "p3": "BB- 級", "p3_delta": "⚠️ 高收益債 (非投資級)", "p3_color": "inverse",
            "p4": "2.80 年",
            "p5": "-0.40%", "p5_delta": "⚠️ 流動性緊貼 (國庫券緩衝)", "p5_color": "inverse",
            "p6": "11.27%",
            "p7": "101.0%",
            "p8": "$2,527 M",
            "p9": "+$154.03 M", "p9_delta": "🟢 總收入-總支出", "p9_color": "normal",
            "p10": "$74.28 M", "p10_delta": "🟢 淨收益 207% 覆蓋", "p10_color": "normal",
            "p11": "-$264.75 M", "p11_delta": "⚠️ 申購 - 贖回 (淨流出)", "p11_color": "inverse" # 💡 新增 申購/贖回差距名片
        },
        "radar_scores": [15.0, 10.0, 15.0, 10.0, 10.0, 10.0, 10.0, 0.0, 2.5],
        "radar_dimensions": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、區域風險", "九、總開支比率"],
        "top10": [
            {"排名": 1, "持倉名稱": "UST BILLS 0% 07/30/26 (美國國庫券)", "資產類別": "美國國庫券", "佔比 (%)": "3.02%"},
            {"排名": 2, "持倉名稱": "UST BILLS 0% 09/10/26 (美國國庫券)", "資產類別": "美國國庫券", "佔比 (%)": "2.02%"},
            {"排名": 3, "持倉名稱": "DIRECTV HLDGS 9.25% 6/32 144A", "資產類別": "通訊服務債", "佔比 (%)": "0.89%"},
            {"排名": 4, "持倉名稱": "VENTURE 9.875% 02/01/32 144A", "資產類別": "能源債", "佔比 (%)": "0.88%"},
            {"排名": 5, "持倉名稱": "WULF COMPUTE 7.75% 10/30 144A", "資產類別": "科技債", "佔比 (%)": "0.84%"},
            {"排名": 6, "持倉名稱": "NISSAN MOTOR 7.5% 7/17/30 144A", "資產類別": "汽車/消費債", "佔比 (%)": "0.82%"},
            {"排名": 7, "持倉名稱": "SWORD PURCH 8.25% 4/15/33 144A", "資產類別": "資本財貨債", "佔比 (%)": "0.82%"},
            {"排名": 8, "持倉名稱": "1261229 BC LTD 10% 4/32 144A", "資產類別": "醫療保健債", "佔比 (%)": "0.80%"},
            {"排名": 9, "持倉名稱": "CARNIVAL CORP 6.125% 2/33 144A", "資產類別": "休閒旅遊債", "佔比 (%)": "0.80%"},
            {"排名": 10, "持倉名稱": "OAK-EAGLE ACQUI 7.25% 7/33 144A", "資產類別": "金融服務債", "佔比 (%)": "0.78%"},
        ],
        "history_div": [
            ["01/06/2026", "02/06/2026", "09/06/2026", "0.046600", "7.7920", "7.42%"],
            ["01/05/2026", "02/05/2026", "09/05/2026", "0.046600", "7.8160", "7.39%"],
            ["01/04/2026", "02/04/2026", "09/04/2026", "0.046600", "7.7450", "7.46%"],
            ["02/03/2026", "03/03/2026", "10/03/2026", "0.046600", "7.8340", "7.38%"],
            ["02/02/2026", "03/02/2026", "10/02/2026", "0.046600", "7.8620", "7.35%"],
            ["02/01/2026", "05/01/2026", "12/01/2026", "0.046600", "7.8800", "7.33%"],
            ["01/12/2025", "02/12/2025", "09/12/2025", "0.046600", "7.8550", "7.36%"],
            ["03/11/2025", "04/11/2025", "11/11/2025", "0.046600", "7.8490", "7.36%"],
            ["01/10/2025", "02/10/2025", "09/10/2025", "0.046600", "7.9080", "7.31%"],
            ["01/09/2025", "02/09/2025", "09/09/2025", "0.046600", "7.8870", "7.33%"],
            ["01/08/2025", "04/08/2025", "11/08/2025", "0.046600", "7.8060", "7.40%"],
            ["01/07/2025", "02/07/2025", "09/07/2025", "0.046600", "7.8430", "7.37%"]
        ],
        "composition_div": [
            ["01-06-2026", "0.046600", "100.00%", "0.00%"],
            ["01-05-2026", "0.046600", "89.00%", "11.00%"],
            ["01-04-2026", "0.046600", "86.00%", "14.00%"],
            ["02-03-2026", "0.046600", "86.00%", "14.00%"],
            ["02-02-2026", "0.046600", "86.00%", "14.00%"],
            ["02-01-2026", "0.046600", "86.00%", "14.00%"],
            ["01-12-2025", "0.046600", "86.00%", "14.00%"],
            ["03-11-2025", "0.046600", "90.00%", "10.00%"],
            ["01-10-2025", "0.046600", "88.00%", "12.00%"],
            ["01-09-2025", "0.046600", "89.00%", "11.00%"],
            ["01-08-2025", "0.046600", "92.00%", "8.00%"],
            ["01-07-2025", "0.046600", "75.00%", "25.00%"]
        ],
        "sector_dist": [
            ["通訊 (Communications)", "16.83%"],
            ["週期性消費品 (Consumer Cyclical)", "16.06%"],
            ["資本財貨 (Capital Goods)", "10.44%"],
            ["能源 (Energy)", "9.64%"],
            ["非週期性消費品 (Consumer Non Cyclical)", "8.94%"],
            ["科技 (Technology)", "8.53%"],
            ["基本工業 (Basic Industry)", "7.72%"],
            ["其他金融 (Other Financials)", "5.93%"],
            ["國庫券 (Treasury)", "5.04%"],
            ["公用事業 (Utility)", "3.49%"]
        ],
        "rating_dist": [
            ["國庫券 / 高評級 (AA/Aa)", "5.04%"],
            ["投資級別 (BBB/Baa)", "3.51%"],
            ["高收益債 (BB/Ba)", "47.70%"],
            ["高收益債 (B)", "34.92%"],
            ["高風險債 (CCC and Below)", "8.45%"],
            ["其他 / 未評級", "0.78%"],
            ["現金 (Cash)", "-0.40%"]
        ],
        "geo_dist_history": [
            {"月份": "2024年6月", "北美": 80.5, "歐洲": 13.1, "其他地區": 2.4, "現金及等值": 4.0},
            {"月份": "2025年6月", "北美": 79.8, "歐洲": 13.5, "其他地區": 2.5, "現金及等值": 4.2},
            {"月份": "2026年6月", "北美": 79.6, "歐洲": 13.8, "其他地區": 7.0, "現金及等值": -0.4}
        ],
        "eval_table": [
            ["一、派息質量", "從資本派息 (ROC) 與總回報覆蓋率", "• 20分: ROC <10% 或 總回報 ≥ 派息率<br>• 10分: ROC 10%-50% 且總回報覆蓋率 >70%<br>• 0分: ROC >50% 且 總回報為負", "• 月報到期收益率：7.23% | 現時派息率：~7.42%<br>• ROC 資本派息率僅 0% ~ 14%<br>👉 營運淨收益 ($1.54 億) 幾乎完全覆蓋股息分派 ($7,428 萬)，本金損耗風險極低。", "15 / 20", "<span class='status-badge-green'>🟢 健康/觀察</span>"],
            ["二、信用風險", "評級分佈與非投資級占比", "• 15分: 平均評級 BBB 以上<br>• 10分: 平均評級 BB 級<br>• 5分: Caa/CCC級 >10% 或未評級 >15%", "• 平均評級：BB- 級<br>• BB 級占 47.70%、B 級占 34.92%、CCC 級占 8.45%<br>👉 標準美國高收益債配備，信用風險適中可控。", "10 / 15", "<span class='status-badge-yellow'>⚠️ 中等風險</span>"],
            ["三、槓桿水平", "資產膨脹率 (Total / Net Assets)", "• 15分: 比率 <105% (無顯著槓桿)<br>• 10分: 比率 105%-120%<br>• 0分: 比率 >120% (槓桿過高)", "• 衍生工具淨曝險上限 50%<br>• 槓桿比率約 101.0%<br>👉 無借貸槓桿，衍生工具僅作輔助避險，結構安全。", "15 / 15", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["四、利率敏感度", "有效存續期 (Duration)", "• 10分: 存續期 <3 年 (抗升息)<br>• 5分: 存續期 3-6 年<br>• 0分: 存續期 >6 年", "• 有效存續期 (Effective Duration)：2.80 年<br>👉 存續期極短，對聯準會利率變動敏感度低，抗升息衝擊強。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["五、流動性風險", "現金儲備與營運現金流", "• 10分: 現金 >10% 且營運 Cash Flow 為正<br>• 5分: 現金 5%-10%<br>• 0分: 現金 <5% 或流動性緊縮", "• 現金及衍生品淨額：-0.40%<br>• 美國國庫券 (UST BILLS) 持倉：5.04%<br>👉 現金流動性緊貼營運需求，主要靠 5.04% 高流動性國庫券緩衝。", "5 / 10", "<span class='status-badge-yellow'>⚠️ 流動性緊貼</span>"],
            ["六、集中度風險", "前十大發行人持倉占比", "• 10分: 前持倉 <20% (極分散)<br>• 5分: 前持倉 20%-30%<br>• 0分: 前持倉 >30%", "• 前十大持倉/發行人合計占：11.27%<br>• 最大單一公司債僅占 0.89%<br>👉 持倉極度分散，可徹底防範單一企業違約黑天鵝事件。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["七、匯率風險", "衍生品對沖與未實現損益", "• 10分: 全額對沖且衍生品虧損 <1% NAV<br>• 5分: 部分對沖<br>• 0分: 未對沖且外幣曝險過高", "• 基礎貨幣為美元 (USD)<br>• 提供對沖股份類別 (RMB H / EUR H / JPY H)<br>👉 避險機制完善，匯率曝險極低。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["八、區域風險", "單一區域/國家持倉集中度", "• 5分: 單一區域 <40%<br>• 2.5分: 單一區域 40%-60%<br>• 0分: 單一區域 >60%", "• 美國地區占比：79.60%<br>• 英國占 2.77%、加拿大占 2.58%<br>👉 高度重倉美國市場，受美國宏觀經濟與信用週期影響深遠。", "0 / 5", "<span class='status-badge-red'>🚨 集中度偏高</span>"],
            ["九、總開支比率", "每年管理費 (Management Fee)", "• 5分: 管理費 <1.0%<br>• 2.5分: 管理費 1.0%-1.5%<br>• 0分: 管理費 >1.5%", "• 每年管理費：1.00% / 年<br>👉 屬於市場高收益債券基金的標準合理收費區間。", "2.5 / 5", "<span class='status-badge-yellow'>⚠️ 中等</span>"]
        ]
    },
    
    "霸菱環球高收益債券基金": {
        "zh": "霸菱環球高收益債券基金",
        "en": "Barings Global High Yield Bond Fund",
        "score": "82.5",
        "summary": "霸菱環球高收益債券基金綜合風險評分為 82.5 分 (健康)。過往一年申購 $28.5億 vs 贖回 $22.1億，呈現 +$6.40 億美元淨流入 (資金充沛)；總收入減總支出淨收益達 +$268.50M，全年度總派息金額為 $182.50M；資產槓桿率 101.1% 幾乎無借貸槓桿。",
        "kpis": {
            "p1": "9.87%",
            "p2": "+2.64%", "p2_delta": "⚠️ 存在本金補貼風險", "p2_color": "inverse",
            "p3": "BB 級", "p3_delta": "⚠️ 高收益債 (非投資級)", "p3_color": "inverse",
            "p4": "2.58 年",
            "p5": "11.26%", "p5_delta": "流動資產", "p5_color": "normal",
            "p6": "13.59%",
            "p7": "101.1%",
            "p8": "$4,380 M",
            "p9": "+$268.50 M", "p9_delta": "🟢 總收入-總支出", "p9_color": "normal",
            "p10": "$182.50 M", "p10_delta": "🟢 淨收益 147% 覆蓋", "p10_color": "normal",
            "p11": "+$640.00 M", "p11_delta": "🟢 申購 - 贖回 (淨流入)", "p11_color": "normal"
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
            ["電訊", "12.19%"], ["醫療保健", "11.69%"], ["能源", "9.38%"], ["金融服務", "6.91%"], ["媒體", "6.61%"],
            ["基本工業", "5.05%"], ["資本物品", "4.62%"], ["休閒", "4.49%"], ["服務", "4.47%"], ["科技及電子", "4.26%"]
        ],
        "rating_dist": [
            ["Baa及以上", "5.40%"], ["Ba", "37.91%"], ["B", "33.75%"], ["Caa1及以下", "9.69%"], ["尚未評級", "2.00%"], ["現金及等值", "11.26%"]
        ],
        "geo_dist_history": [
            {"月份": "25年6月", "北美": 66.2, "歐洲": 27.6, "其他地區": 1.6, "現金及等值": 4.6},
            {"月份": "25年9月", "北美": 67.4, "歐洲": 25.9, "其他地區": 2.4, "現金及等值": 4.3},
            {"月份": "25年12月", "北美": 66.7, "歐洲": 24.6, "其他地區": 2.7, "現金及等值": 6.0},
            {"月份": "26年3月", "北美": 68.3, "歐洲": 22.9, "其他地區": 3.1, "現金及等值": 5.7},
            {"月份": "26年5月", "北美": 61.3, "歐洲": 23.8, "其他地區": 3.6, "現金及等值": 11.3}
        ],
        "eval_table": [
            ["一、派息質量", "從資本派息 (ROC) 與總回報覆蓋率", "• 20分: ROC <10% 或 總回報 ≥ 派息率<br>• 10分: ROC 10%-50% 且總回報覆蓋率 >70%<br>• 0分: ROC >50% 且 總回報為負", "• ROC 比例：42.2% ~ 59.2%<br>• 2025總回報：+9.19% | 派息率：~9.87%<br>👉 帳面營運淨利遠高於派息總額，總回報幾乎完全覆蓋派息。", "15 / 20", "<span class='status-badge-green'>🟢 健康/觀察</span>"],
            ["二、信用風險", "評級分佈與非投資級占比", "• 15分: 平均評級 BBB 以上<br>• 10分: 平均評級 BB 級<br>• 5分: Caa/CCC級 >10% 或未評級 >15%", "• 平均評級：BB<br>• Ba 級 37.91%、B 級 33.75%<br>👉 標準高收益債配備，一次投資風險適中可控。", "10 / 15", "<span class='status-badge-yellow'>⚠️ 中等風險</span>"],
            ["三、槓桿水平", "資產膨脹率 (Total / Net Assets)", "• 15分: 比率 <105% (無顯著槓桿)<br>• 10分: 比率 105%-120%<br>• 0分: 比率 >120% (槓桿過高)", "• 總資產 / 淨資產：101.1%<br>👉 幾乎無借貸槓桿，結構非常安全透明。", "15 / 15", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["四、利率敏感度", "有效存續期 (Duration)", "• 10分: 存續期 <3 年 (抗升息)<br>• 5分: 存續期 3-6 年<br>• 0分: 存續期 >6 年", "• 最低修訂存續期：2.58 年<br>👉 存續期極短，對央行利率變化的敏感度與衝擊較低。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["五、流動性風險", "現金儲備與營運現金流", "• 10分: 現金 >10% 且營運 Cash Flow 為正<br>• 5分: 現金 5%-10%<br>• 0分: 現金 <5% 或流動性緊縮", "• 現金及等值：11.26% (約 5.5 億美元)<br>👉 現金充沛，足以支應短期贖回需求。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["六、集中度風險", "前十大發行人持倉占比", "• 10分: 前持倉 <20% (極分散)<br>• 5分: 前持倉 20%-30%<br>• 0分: 前持倉 >30%", "• 前十大發行人合計占：13.59%<br>• 最大單一發行人僅占 2.40%<br>👉 極度分散，有效避免單一公司黑天鵝事件。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["七、匯率風險", "衍生品對沖與未實現損益", "• 10分: 全額對沖且衍生品虧損 <1% NAV<br>• 5分: 部分對沖<br>• 0分: 未對沖且外幣曝險過高", "• 各非美元類別均提供衍生品對沖<br>👉 避險機制運作順暢，衍生品風險極低。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["八、區域風險", "單一區域/國家持倉集中度", "• 5分: 單一區域 <40%<br>• 2.5分: 單一區域 40%-60%<br>• 0分: 單一區域 >60%", "• 北美地區：61.3% | 歐洲地區：23.8%<br>👉 重倉北美/美國市場，受美國信用週期影響深遠。", "0 / 5", "<span class='status-badge-red'>🚨 集中度偏高</span>"],
            ["九、總開支比率", "每年管理費 (Management Fee)", "• 5分: 管理費 <1.0%<br>• 2.5分: 管理費 1.0%-1.5%<br>• 0分: 管理費 >1.5%", "• G類別 (零售)：1.25% / 年<br>👉 屬於市場高收益債券基金的標準收費區間。", "2.5 / 5", "<span class='status-badge-yellow'>⚠️ 中等</span>"]
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

# 5. 核心數據名片 (第一排 7 大結構名片)
kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5, kpi_c6, kpi_c7 = st.columns(7)

if fund_type == "債券基金":
    p2_delta = curr_fund['kpis'].get('p2_delta', '⚠️ 存在本金補貼風險')
    p2_color = curr_fund['kpis'].get('p2_color', 'inverse')
    p3_delta = curr_fund['kpis'].get('p3_delta', '⚠️ 高收益債 (非投資級)')
    p3_color = curr_fund['kpis'].get('p3_color', 'inverse')
    p5_delta = curr_fund['kpis'].get('p5_delta', '流動資產')
    p5_color = curr_fund['kpis'].get('p5_color', 'normal')

    with kpi_c1: st.metric(label="現時派息率", value=curr_fund['kpis']['p1'], delta="年化分派", delta_color="normal")
    with kpi_c2: st.metric(label="派息與收益息差", value=curr_fund['kpis']['p2'], delta=p2_delta, delta_color=p2_color)
    with kpi_c3: st.metric(label="平均持有債務評級", value=curr_fund['kpis']['p3'], delta=p3_delta, delta_color=p3_color)
    with kpi_c4: st.metric(label="續存率 / 有效期", value=curr_fund['kpis']['p4'], delta="存續期 (久期)", delta_color="normal")
    with kpi_c5: st.metric(label="手持現金比率", value=curr_fund['kpis']['p5'], delta=p5_delta, delta_color=p5_color)
    with kpi_c6: st.metric(label="前十大發行人佔比", value=curr_fund['kpis']['p6'], delta="極度分散", delta_color="normal")
    with kpi_c7: st.metric(label="槓桿比率", value=curr_fund['kpis']['p7'], delta="無顯著借貸", delta_color="normal")
else:
    for c, title in zip([kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5, kpi_c6, kpi_c7], ["現時派息率", "息差 / Beta", "平均持股/債評級", "續存率 / 波動率", "手持現金比率", "前十大發行人佔比", "槓桿比率"]):
        with c: st.metric(label=title, value="待核對", delta="請上傳PDF")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# 💡 第二排：重點展示 4 大核心財務流量名片 (總資產、淨營運收益、總派息金額、贖回/申購差距)
fin_c1, fin_c2, fin_c3, fin_c4 = st.columns(4)

if fund_type == "債券基金":
    p9_delta = curr_fund['kpis'].get('p9_delta', '🟢 總收入-總支出')
    p9_color = curr_fund['kpis'].get('p9_color', 'normal')
    p10_delta = curr_fund['kpis'].get('p10_delta', '🟢 淨收益覆蓋佳')
    p10_color = curr_fund['kpis'].get('p10_color', 'normal')
    p11_delta = curr_fund['kpis'].get('p11_delta', '⚠️ 申購 - 贖回差距')
    p11_color = curr_fund['kpis'].get('p11_color', 'inverse')

    with fin_c1: st.metric(label="總基金資產值 (AUM)", value=curr_fund['kpis']['p8'], delta="百萬美元 (USD Million)", delta_color="normal")
    with fin_c2: st.metric(label="過往一年淨收益 (總收入-總支出)", value=curr_fund['kpis']['p9'], delta=p9_delta, delta_color=p9_color)
    with fin_c3: st.metric(label="過往一年總派息金額", value=curr_fund['kpis']['p10'], delta=p10_delta, delta_color=p10_color)
    with fin_c4: st.metric(label="申購與贖回差距 (淨資金流向)", value=curr_fund['kpis']['p11'], delta=p11_delta, delta_color=p11_color) # 💡 新增 申購與贖回差距 名片
else:
    with fin_c1: st.metric(label="總基金資產值 (AUM)", value="待核對", delta="請上傳PDF")
    with fin_c2: st.metric(label="過往一年淨收益", value="待核對", delta="請上傳PDF")
    with fin_c3: st.metric(label="過往一年總派息金額", value="待核對", delta="請上傳PDF")
    with fin_c4: st.metric(label="申購與贖回差距", value="待核對", delta="請上傳PDF")

st.markdown("<br>", unsafe_allow_html=True)

# 6. 風險維度分析及基金底層資產數據 (7 大 TAB)
st.markdown("### 📊 風險維度分析及基金底層資產數據")

main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6, main_tab7 = st.tabs([
    "🕸️ 風險維度雷達圖", 
    "📋 底層資產清單",
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

# Tab 2: 底層資產清單
with main_tab2:
    top10_rows_html = "".join([f"<tr><td style='width: 10%;'><b>{row['排名']}</b></td><td style='width: 45%;'><b>{row['持倉名稱']}</b></td><td style='width: 30%;'>{row['資產類別']}</td><td style='width: 15%; font-weight: bold;'>{row['佔比 (%)']}</td></tr>" for row in curr_fund["top10"]])
    st.markdown(f"""
    <table class="custom-table">
        <thead><tr><th>排名</th><th>底層資產名稱</th><th>資產類別</th><th>佔比 (%)</th></tr></thead>
        <tbody>{top10_rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

# Tab 3: 歷史派息紀錄
with main_tab3:
    h_rows = "".join([f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td><b>{r[3]}</b></td><td>{r[4]}</td><td style='font-weight:bold; color:#059669;'>{r[5]}</td></tr>" for r in curr_fund["history_div"]])
    st.markdown(f"""
    <table class="custom-table">
        <thead>
            <tr><th>除息日</th><th>記錄日</th><th>派息日</th><th>每單位股息 (美元)</th><th>除息日每單位資產淨值 (美元)</th><th>年度化派息率</th></tr>
        </thead>
        <tbody>{h_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

# Tab 4: 派息組成
with main_tab4:
    st.caption("📌 註：可分派淨收入股息 vs 由資本所分派之股息 (ROC)")
    c_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td style='font-weight:bold; color:#D97706;'>{r[3]}</td></tr>" for r in curr_fund["composition_div"]])
    st.markdown(f"""
    <table class="custom-table">
        <thead>
            <tr><th>除息日 (Ex-dividend date)</th><th>每股股息 (Dividend per share)</th><th>該月份可分派之淨收入股息 %</th><th>由資本所分派之股息 % (ROC)</th></tr>
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

# 7. 隱藏摺疊：基金深度風險評估明細表
with st.expander("📋 點擊展開 / 折疊：基金深度風險評估明細表", expanded=True):
    if fund_type == "債券基金":
        eval_rows_html = "".join([
            f"<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td style='text-align:center; font-weight:bold;'>{r[4]}</td><td style='text-align:center;'>{r[5]}</td></tr>"
            for r in curr_fund["eval_table"]
        ])
        
        html_table = f"""
        <table class="custom-table">
            <thead>
                <tr>
                    <th style="width: 14%;">評估維度</th>
                    <th style="width: 18%;">具體檢查指標</th>
                    <th style="width: 25%;">專屬評分簡算規則</th>
                    <th style="width: 27%;">基金真實數據與解析</th>
                    <th style="width: 8%; text-align: center;">得分/滿分</th>
                    <th style="width: 8%; text-align: center;">風險狀態</th>
                </tr>
            </thead>
            <tbody>
                {eval_rows_html}
            </tbody>
        </table>
        <div class="summary-footer">
            <span class="summary-title">總得分 / 得分率：</span>
            <span class="summary-score">{curr_fund['score']} / 100</span>
            <span class="status-badge-green" style="font-size: 13px; padding: 5px 12px;">{curr_fund['score']}% (健康)</span>
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
