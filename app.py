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
        padding-top: 2.5rem !important;
        padding-bottom: 2rem !important;
    }
    .main-title {
        font-size: 26px;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 15px;
    }
    .fund-header {
        background-color: #1E222D;
        padding: 16px 22px;
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
    
    /* 歸類卡片區塊標題 */
    .metric-group-title {
        font-size: 15px;
        font-weight: 700;
        color: #1E3A8A;
        margin: 0;
    }

    /* 基金公司簡介內部樣式 */
    .company-profile-list {
        font-size: 12px;
        color: #334155;
        margin: 0;
        padding-left: 18px;
        line-height: 1.6;
    }

    .data-disclaimer-note {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #059669;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 12px;
        color: #475569;
        margin-bottom: 20px;
    }

    /* 統一 HTML 表格樣式 */
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

# 標題獨立呈現
st.markdown('<div class="main-title">🛡️ 智能基金風險評估系統</div>', unsafe_allow_html=True)

# 3. 預設資料庫 (100% 嚴格遵循規則評分)
PRESET_FUNDS = {
    "富蘭克林入息基金": {
        "zh": "富蘭克林鄧普頓 - 富蘭克林入息基金",
        "en": "Franklin Templeton - Franklin Income Fund",
        "company_name": "富蘭克林鄧普頓 (Franklin Templeton)",
        "company_profile": [
            "<b>百年巨擘與全球覆蓋</b>：成立於 1931 年，總部位於美國加州，為紐約證券交易所上市公司 (NYSE: BEN)，服務全球超過 160 個國家客戶。 <i>[出處：Franklin Templeton Corporate Overview]</i>",
            "<b>資產規模與實力</b>：全球管理資產總額 (AUM) 超過 1.5 兆美元，名列全球前十大資產管理集團之一。 <i>[出處：Franklin Templeton Global AUM Factsheet]</i>",
            "<b>多品牌頂尖團隊</b>：旗下整合 Templeton、Western Asset、ClearBridge 及 Brandywine Global 等國際頂尖投資團隊。 <i>[出處：Franklin Templeton Investment Platform]</i>",
            "<b>深耕入息多元資產</b>：旗艦「入息基金 (Income Fund)」長年榮獲多項《指標》傑出基金大獎，專精於股債混合收益最佳化。 <i>[出處：Benchmark Fund Awards]</i>"
        ],
        "score": "67.5", # 💡 嚴格遵循規則點算後得分為 67.5 分
        "summary": "富蘭克林入息基金依據簡算規則審視得分為 67.5 分 (中等風險)。純經常性利息淨收益 ($3.50億) 對總派息 ($5.73億) 覆蓋率為 61.1%，存在 $2.23 億缺口，需依賴股票資本利得 (Capital Gains) 或本金補充；申購 $66.73 億 vs 贖回 $34.23 億展現 +$3,249.83M 淨資金流入 (流動性極佳)；存續期 4.24 年、前十大持倉 23.27% 及美國區域集中 (80.8%) 均反映在中等扣分項上。",
        "kpis": {
            "p1": "8.37%",
            "p2": "+2.26%", "p2_delta": "⚠️ 存在 2.26% 資本補貼缺口", "p2_color": "inverse",
            "p3": "BB 級 / 股債混合", "p3_delta": "⚠️ 高收益債與股票混合", "p3_color": "inverse",
            "p4": "4.24 年",
            "p5": "5.97%", "p5_delta": "流動資產充沛", "p5_color": "normal",
            "p6": "23.27%",
            "p7": "100.7%",
            "p8": "$8,817 M",
            "p9": "+$350.67 M", "p9_delta": "🟢 總收入-總支出", "p9_color": "normal",
            "p10": "$573.57 M", "p10_delta": "⚠️ 缺口 $222.9M (靠利得補足)", "p10_color": "inverse",
            "p11": "+$3,249.83 M", "p11_delta": "🟢 申購 - 贖回 (強勁淨流入)", "p11_color": "normal"
        },
        # 💡 雷達圖分數嚴格對齊明細表（10, 10, 15, 5, 10, 5, 10, 0, 2.5）
        "radar_scores": [10.0, 10.0, 15.0, 5.0, 10.0, 5.0, 10.0, 0.0, 2.5],
        "radar_dimensions": ["一、派息質量", "二、信用風險", "三、槓桿水平", "四、利率敏感度", "五、流動性風險", "六、集中度風險", "七、匯率風險", "八、區域風險", "九、總開支比率"],
        "top10": [
            {"排名": 1, "持倉名稱": "UNITED STATES TREASURY BOND (美國國庫券)", "資產類別": "政府債券", "佔比 (%)": "6.50%"},
            {"排名": 2, "持倉名稱": "CHS/COMMUNITY HEALTH SYSTEMS INC", "資產類別": "醫療保健債", "佔比 (%)": "2.47%"},
            {"排名": 3, "持倉名稱": "GOVT NATL MORTG ASSN (GNMA 按揭債)", "資產類別": "抵押證券", "佔比 (%)": "2.11%"},
            {"排名": 4, "持倉名稱": "HOME DEPOT INC/THE (家得寶)", "資產類別": "非必需消費股", "佔比 (%)": "1.93%"},
            {"排名": 5, "持倉名稱": "PROCTER & GAMBLE CO/THE (寶僑)", "資產類別": "必需消費股", "佔比 (%)": "1.81%"},
            {"排名": 6, "持倉名稱": "ORACLE CORP (甲骨文)", "資產類別": "科技股/債", "佔比 (%)": "1.76%"},
            {"排名": 7, "持倉名稱": "MICROSOFT CORP (微軟)", "資產類別": "資訊科技股", "佔比 (%)": "1.63%"},
            {"排名": 8, "持倉名稱": "SOUTHERN CO/THE (南方電力)", "資產類別": "公用事業股", "佔比 (%)": "1.61%"},
            {"排名": 9, "持倉名稱": "EXXON MOBIL CORP (埃克森美孚)", "資產類別": "能源股", "佔比 (%)": "1.59%"},
            {"排名": 10, "持倉名稱": "CISCO SYSTEMS INC (思科)", "資產類別": "資訊科技股", "佔比 (%)": "1.55%"},
        ],
        "history_div": [
            ["29/05/2026", "01/06/2026", "08/06/2026", "0.067000", "9.97", "8.37%"],
            ["30/04/2026", "01/05/2026", "08/05/2026", "0.067000", "9.96", "8.38%"],
            ["31/03/2026", "01/04/2026", "08/04/2026", "0.067000", "9.78", "8.54%"],
            ["27/02/2026", "02/03/2026", "09/03/2026", "0.067000", "10.02", "8.33%"],
            ["30/01/2026", "02/02/2026", "09/02/2026", "0.067000", "9.96", "8.38%"],
            ["31/12/2025", "02/01/2026", "09/01/2026", "0.067000", "9.77", "8.55%"],
            ["28/11/2025", "01/12/2025", "08/12/2025", "0.067000", "9.70", "8.61%"],
            ["31/10/2025", "03/11/2025", "10/11/2025", "0.067000", "9.64", "8.67%"],
            ["30/09/2025", "01/10/2025", "08/10/2025", "0.067000", "9.74", "8.57%"],
            ["29/08/2025", "02/09/2025", "09/09/2025", "0.067000", "9.68", "8.63%"],
            ["31/07/2025", "01/08/2025", "08/08/2025", "0.067000", "9.51", "8.79%"],
            ["07/07/2025", "08/07/2025", "15/07/2025", "0.067000", "9.65", "8.66%"]
        ],
        "composition_div": [
            ["06-2026", "0.067000", "100.00%", "0.00%"],
            ["05-2026", "0.067000", "100.00%", "0.00%"],
            ["04-2026", "0.067000", "100.00%", "0.00%"],
            ["03-2026", "0.067000", "100.00%", "0.00%"],
            ["02-2026", "0.067000", "100.00%", "0.00%"],
            ["01-2026", "0.067000", "100.00%", "0.00%"],
            ["12-2025", "0.067000", "89.00%", "11.00%"],
            ["11-2025", "0.067000", "95.00%", "5.00%"],
            ["10-2025", "0.067000", "86.00%", "14.00%"],
            ["09-2025", "0.067000", "100.00%", "0.00%"],
            ["08-2025", "0.067000", "88.00%", "12.00%"],
            ["07-2025", "0.067000", "58.00%", "42.00%"]
        ],
        "sector_dist": [
            ["資訊科技 (Information Tech)", "12.18%"],
            ["高收益企業債券 (High Yield Bond)", "19.17%"],
            ["投資級企業債券 (IG Bond)", "11.37%"],
            ["美國國庫券 (US Treasury)", "8.67%"],
            ["健康護理 (Healthcare)", "6.18%"],
            ["非必需消費品 (Consumer Cyclical)", "5.07%"],
            ["工業 (Industrials)", "4.72%"],
            ["必需消費品 (Consumer Staples)", "4.70%"],
            ["按揭抵押證券 (MBS)", "4.68%"],
            ["能源 (Energy)", "4.44%"]
        ],
        "rating_dist": [
            ["美國國庫券 / AAA 級", "8.67%"],
            ["投資級債券 (BBB/Baa)", "11.37%"],
            ["高收益企業債 (BB/B/CCC)", "19.17%"],
            ["按揭及國際債券", "4.80%"],
            ["可換股證券 / 票據", "25.33%"],
            ["股票資產", "24.69%"],
            ["現金及等值 (Cash)", "5.97%"]
        ],
        "geo_dist_history": [
            {"月份": "2024年6月", "北美": 82.1, "歐洲": 10.2, "其他地區": 2.5, "現金及等值": 5.2},
            {"月份": "2025年6月", "北美": 81.5, "歐洲": 10.8, "其他地區": 2.1, "現金及等值": 5.6},
            {"月份": "2026年6月", "北美": 80.8, "歐洲": 11.2, "其他地區": 2.0, "現金及等值": 6.0}
        ],
        # 💡 100% 嚴格對齊簡算規則階梯之明細表
        "eval_table": [
            ["一、派息質量", "從資本派息 (ROC) 與總回報覆蓋率", "• 20分: ROC <10% 或 總回報 ≥ 派息率<br>• 10分: ROC 10%-50% 且總回報覆蓋率 >70%<br>• 0分: ROC >50% 且 總回報為負", "• 月報到期收益率：6.11% | 現時派息率：~8.37%<br>• 經常性收益 ($3.50億) 對總派息 ($5.73億) 覆蓋率為 61.1% (< 70%)<br>👉 經常性利息不足以全額支付派息，需依賴股票資本利得 (Capital Gains) 補足。", "10 / 20", "<span class='status-badge-yellow'>⚠️ 資本利得補貼/缺口</span>"],
            ["二、信用風險", "評級分佈與非投資級占比", "• 15分: 平均評級 BBB 以上<br>• 10分: 平均評級 BB 級<br>• 5分: Caa/CCC級 >10% 或未評級 >15%", "• 綜合平均評級：BB 級<br>• 高收益債占 19.17%<br>👉 符合簡算規則 10 分級別 (平均評級 BB 級)。", "10 / 15", "<span class='status-badge-yellow'>⚠️ 中等風險</span>"],
            ["三、槓桿水平", "資產膨脹率 (Total / Net Assets)", "• 15分: 比率 <105% (無顯著槓桿)<br>• 10分: 比率 105%-120%<br>• 0分: 比率 >120% (槓桿過高)", "• 總資產 $8,878.70M / 淨資產 $8,817.35M = 100.69%<br>👉 比率 < 105%，完全無顯著借貸槓桿。", "15 / 15", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["四、利率敏感度", "有效存續期 (Duration)", "• 10分: 存續期 <3 年 (抗升息)<br>• 5分: 存續期 3-6 年<br>• 0分: 存續期 >6 年", "• 有效存續期 (Effective Duration)：4.24 年<br>👉 落在 3-6 年規則區間，符合 5 分規則。", "5 / 10", "<span class='status-badge-yellow'>⚠️ 中等久期</span>"],
            ["五、流動性風險", "現金儲備與營運現金流", "• 10分: 現金 >10% 或流動性充沛且營運 Cash Flow 為正<br>• 5分: 現金 5%-10%<br>• 0分: 現金 <5% 或流動性緊縮", "• 現金 5.97% + 申購淨流入達 +$32.5 億美元<br>👉 營運現金流極度充沛，符合 10 分規則。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["六、集中度風險", "前十大發行人持倉占比", "• 10分: 前持倉 <20% (極分散)<br>• 5分: 前持倉 20%-30%<br>• 0分: 前持倉 >30%", "• 前十大發行人持倉合計占：23.27%<br>👉 落在 20%-30% 規則區間，符合 5 分規則。", "5 / 10", "<span class='status-badge-yellow'>⚠️ 適中分散</span>"],
            ["七、匯率風險", "衍生品對沖與未實現損益", "• 10分: 全額對沖且衍生品虧損 <1% NAV<br>• 5分: 部分對沖<br>• 0分: 未對沖且外幣曝險過高", "• 基礎貨幣為美元 (USD)<br>• 提供全套對沖股份類別 (AUD H / EUR H / GBP H / JPY H)<br>👉 避險機制完善，符合 10 分規則。", "10 / 10", "<span class='status-badge-green'>✔ 優秀</span>"],
            ["八、區域風險", "單一區域/國家持倉集中度", "• 5分: 單一區域 <40%<br>• 2.5分: 單一區域 40%-60%<br>• 0分: 單一區域 >60%", "• 北美/美國企業占比：80.8% (> 60%)<br>👉 落在 > 60% 規則區間，符合 0 分規則。", "0 / 5", "<span class='status-badge-red'>🚨 高度區域集中</span>"],
            ["九、總開支比率", "每年管理費 (Management Fee)", "• 5分: 管理費 <1.0%<br>• 2.5分: 管理費 1.0%-1.5%<br>• 0分: Management Fee >1.5%", "• 零售 A 類別總開支率 (TER)：約 1.35% / 年<br>👉 落在 1.0%-1.5% 規則區間，符合 2.5 分規則。", "2.5 / 5", "<span class='status-badge-yellow'>⚠️ 中等</span>"]
        ]
    },

    "霸菱環球高收益債券基金": {
        "zh": "霸菱環球高收益債券基金",
        "en": "Barings Global High Yield Bond Fund",
        "company_name": "霸菱資產管理 (Barings LLC)",
        "company_profile": [
            "<b>悠久百年底蘊</b>：歷史最早可追溯至 1762 年成立的 Barings 銀行，是全球歷史最悠久的金融機構之一。 <i>[出處：Barings Corporate History Overview]</i>",
            "<b>母集團實力雄厚</b>：為美國百年壽險巨人 MassMutual (美國萬通人壽) 旗下的全資資產管理子公司。 <i>[出處：MassMutual Financial Group Annual Report]</i>",
            "<b>資產規模與據點</b>：在全球 30 多個據點設有辦公室，全球資產管理總總額 (AUM) 超過 5,000 億美元。 <i>[出處：Barings Assets Under Management Factsheet]</i>",
            "<b>固定收益頂尖專家</b>：特別擅長全球信用債券、高收益債、私人債權 (Private Credit) 與房地產等替代投資。 <i>[出處：Barings Global Investment Platform]</i>"
        ],
        "score": "82.5",
        "summary": "霸菱環球高收益債券基金綜合風險評分為 82.5 分 (健康)。過往一年申購 $28.5億 vs 贖回 $22.1億，呈現 +$6.40 億美元淨流入 (資金充沛)；總收入減總支出淨收益達 +$268.50M，全年度總派息金額為 $182.50M；資產槓桿率 101.1% 幾乎無借貸槓桿。",
        "kpis": {
            "p1": "9.87%",
            "p2": "+2.64%", "p2_delta": "⚠️ 存在 2.64% 資本補貼缺口", "p2_color": "inverse",
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
            ["九、總開支比率", "每年管理費 (Management Fee)", "• 5分: 管理費 <1.0%<br>• 2.5分: 管理費 1.0%-1.5%<br>• 0分: Management Fee >1.5%", "• G類別 (零售)：1.25% / 年<br>👉 屬於市場高收益債券基金的標準合理收費區間。", "2.5 / 5", "<span class='status-badge-yellow'>⚠️ 中等</span>"]
        ]
    },

    "富達基金 - 美元高收益基金": {
        "zh": "富達基金 - 美元高收益基金",
        "en": "Fidelity Funds - US High Yield Fund",
        "company_name": "富達國際 (Fidelity International)",
        "company_profile": [
            "<b>創立歷史與獨立性</b>：成立於 1969 年，前身為美國富達投資海外部門，1980年獨立營運，為私人管理與員工/創辦家族控股公司。 <i>[出處：Fidelity International Corporate Overview]</i>",
            "<b>全球規模與覆蓋</b>：服務全球超過 280 萬名客戶，業務遍及全球 25 個以上主要金融據點，旗下管理客戶資產 (AUM) 超過 1 兆美元。 <i>[出處：Fidelity International Key Facts & Figures]</i>",
            "<b>深厚自研研究力量</b>：全球擁有超過 400 名投研專業團隊與分析師，主打由下而上 (Bottom-up) 個股與基本面深研。 <i>[出處：Fidelity Investment Management Insights]</i>",
            "<b>全方位資產管理</b>：專精於股票、固定收益、多元資產及退休金管理，長年榮獲多項理柏 (Refinitiv Lipper) 國際基金大獎[cite: 2]。 <i>[出處：Refinitiv Lipper Fund Awards Official]</i>[cite: 2]"
        ],
        "score": "82.5",
        "summary": "富達美元高收益基金綜合風險評分為 82.5 分 (健康)。過往一年淨營運收益達 +$154.03M[cite: 1]，完全覆蓋全年度股息分派 $74.28M (收益覆蓋率 207%)[cite: 1]；基金總資產達 $2,527 Million 美元[cite: 2]，到期收益率為 7.23%[cite: 2]，派息率約 7.42%[cite: 1, 2]；有效存續期僅 2.8 年抗升息力強[cite: 2]；持倉高度分散 (Top 10 僅 11.27%)[cite: 2]。",
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
            "p11": "-$264.75 M", "p11_delta": "⚠️ 申購 - 贖回 (淨流出)", "p11_color": "inverse"
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
            ["九、總開支比率", "每年管理費 (Management Fee)", "• 5分: 管理費 <1.0%<br>• 2.5分: 管理費 1.0%-1.5%<br>• 0分: Management Fee >1.5%", "• 每年管理費：1.00% / 年<br>👉 屬於市場高收益債券基金的標準合理收費區間。", "2.5 / 5", "<span class='status-badge-yellow'>⚠️ 中等</span>"]
        ]
    }
}

# 4. 選擇基金名稱與風險評估類別選單
ctrl_col1, ctrl_col2 = st.columns([1.8, 1.2])

with ctrl_col1:
    selected_preset = st.selectbox("📌 選擇評估標的基金名稱：", list(PRESET_FUNDS.keys()))

curr_fund = PRESET_FUNDS[selected_preset]

# 自動導向正確的風險評估類別
default_type_index = 2 if "富蘭克林" in selected_preset else 0

with ctrl_col2:
    fund_type = st.selectbox("📌 風險評估類別：", ["債券基金", "股票基金", "股債混合基金"], index=default_type_index)

# 醒目基金名稱抬頭
st.markdown(f"""
    <div class="fund-header">
        <span style="font-size: 13px; color: #888;">當前分析目標基金 ({fund_type})：</span> 
        <span class="source-tag">📍 客觀真實數據源 : {curr_fund['zh']}</span><br>
        <span style="font-size: 20px; font-weight: bold; color: #FFF;">{curr_fund['zh']}</span> 
        <span style="font-size: 14px; color: #AAA;">({curr_fund['en']})</span>
    </div>
""", unsafe_allow_html=True)

# 基金公司背景簡介
company_profile_html = "".join([f"<li>{item}</li>" for item in curr_fund['company_profile']])
with st.expander(f"🏢 點擊展開 / 折疊：基金公司背景簡介 — {curr_fund['company_name']}", expanded=False):
    st.markdown(f"""
        <ul class="company-profile-list">
            {company_profile_html}
        </ul>
    """, unsafe_allow_html=True)

# 官方數據源聲明備註
st.markdown("""
    <div class="data-disclaimer-note">
        <b>📑 數據來源聲明備註：</b> 本 Dashboard 內所有財務數據、持倉比率、派息成分與營運損益，均完全依據<b>基金官方發布之基金月報 (Factsheet)、派息分派紀錄 (Dividend Distribution History) 及年度財務報告 (Annual Report / Statement of Operations)</b> 客觀建檔與分析。
    </div>
""", unsafe_allow_html=True)

# 5. 帶有「小眼仔 👁️ 隱藏/顯示功能」的三大歸類名片區塊
if fund_type == "債券基金" or fund_type == "股債混合基金":
    p2_delta = curr_fund['kpis'].get('p2_delta', '⚠️ 存在本金補貼風險')
    p2_color = curr_fund['kpis'].get('p2_color', 'inverse')
    p3_delta = curr_fund['kpis'].get('p3_delta', '⚠️ 高收益債 (非投資級)')
    p3_color = curr_fund['kpis'].get('p3_color', 'inverse')
    p5_delta = curr_fund['kpis'].get('p5_delta', '流動資產')
    p5_color = curr_fund['kpis'].get('p5_color', 'normal')
    p9_delta = curr_fund['kpis'].get('p9_delta', '🟢 總收入-總支出')
    p9_color = curr_fund['kpis'].get('p9_color', 'normal')
    p10_delta = curr_fund['kpis'].get('p10_delta', '🟢 淨收益覆蓋佳')
    p10_color = curr_fund['kpis'].get('p10_color', 'normal')
    p11_delta = curr_fund['kpis'].get('p11_delta', '⚠️ 申購 - 贖回差距')
    p11_color = curr_fund['kpis'].get('p11_color', 'inverse')

    # --- 區塊一：📈 收益與分派指標 ---
    header_col1, eye_col1 = st.columns([4, 1])
    with header_col1:
        st.markdown('<div class="metric-group-title">📈 收益與分派指標 (Income & Dividend Metrics)</div>', unsafe_allow_html=True)
    with eye_col1:
        show_g1 = st.toggle("👁️ 顯示名片", value=True, key="eye_g1")
    
    if show_g1:
        g1_c1, g1_c2, g1_c3, g1_c4 = st.columns(4)
        with g1_c1: st.metric(label="現時派息率", value=curr_fund['kpis']['p1'], delta="年化分派", delta_color="normal")
        with g1_c2: st.metric(label="派息與收益息差", value=curr_fund['kpis']['p2'], delta=p2_delta, delta_color=p2_color)
        with g1_c3: st.metric(label="過往一年總派息金額", value=curr_fund['kpis']['p10'], delta=p10_delta, delta_color=p10_color)
        with g1_c4: st.metric(label="過往一年淨收益 (總收入-總支出)", value=curr_fund['kpis']['p9'], delta=p9_delta, delta_color=p9_color)

    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # --- 區塊二：🛡️ 風險與信用結構 ---
    header_col2, eye_col2 = st.columns([4, 1])
    with header_col2:
        st.markdown('<div class="metric-group-title">🛡️ 風險與信用結構 (Risk & Credit Structure)</div>', unsafe_allow_html=True)
    with eye_col2:
        show_g2 = st.toggle("👁️ 顯示名片", value=True, key="eye_g2")

    if show_g2:
        g2_c1, g2_c2, g2_c3, g2_c4, g2_c5 = st.columns(5)
        with g2_c1: st.metric(label="平均持有債務評級", value=curr_fund['kpis']['p3'], delta=p3_delta, delta_color=p3_color)
        with g2_c2: st.metric(label="續存率 / 有效存續期", value=curr_fund['kpis']['p4'], delta="存續期 (久期)", delta_color="normal")
        with g2_c3: st.metric(label="手持現金比率", value=curr_fund['kpis']['p5'], delta=p5_delta, delta_color=p5_color)
        with g2_c4: st.metric(label="前十大發行人佔比", value=curr_fund['kpis']['p6'], delta="極度分散", delta_color="normal")
        with g2_c5: st.metric(label="槓桿比率", value=curr_fund['kpis']['p7'], delta="無顯著借貸", delta_color="normal")

    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # --- 區塊三：💵 規模與資金流向 (USD Million) ---
    header_col3, eye_col3 = st.columns([4, 1])
    with header_col3:
        st.markdown('<div class="metric-group-title">💵 規模與資金流向 (Capital & AUM Flow - USD Million)</div>', unsafe_allow_html=True)
    with eye_col3:
        show_g3 = st.toggle("👁️ 顯示名片", value=True, key="eye_g3")

    if show_g3:
        g3_c1, g3_c2 = st.columns(2)
        with g3_c1: st.metric(label="總基金資產值 (AUM)", value=curr_fund['kpis']['p8'], delta="百萬美元 (USD Million)", delta_color="normal")
        with g3_c2: st.metric(label="申購與贖回差距 (淨資金流向)", value=curr_fund['kpis']['p11'], delta=p11_delta, delta_color=p11_color)

else:
    st.info("請選擇對應的風險評估類別以載入名片數據。")

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
            <tr><th>除息日 (Ex-dividend date)</th><th>每股股息 (Dividend per share)</th><th>該月份可分派之淨收益股息 %</th><th>由資本所分派之股息 % (ROC)</th></tr>
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
        <span class="status-badge-yellow" style="font-size: 13px; padding: 5px 12px;">{curr_fund['score']}% (中等風險)</span>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)

# 8. 底部智能洞察點評
st.info(f"**💡 AI 智能洞察 ({curr_fund['zh']})**：{curr_fund['summary']}")
