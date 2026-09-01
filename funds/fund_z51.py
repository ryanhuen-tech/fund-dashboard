# funds/fund_z51.py

DATA_Z51 = {
    "Z51 友邦股票入息基金 (上月派息: 8.10%)": {
        "code": "Z51",
        "zh": "友邦保險 - 友邦股票入息基金",
        "en": "AIA Investment Funds - AIA Equity Income Fund",
        "category": "股票基金",
        "star": "⭐⭐⭐",
        "star_num": 3,
        "last_yield": 8.10,  # 最新年化派息率
        "return_1y": 16.52,  # 1 年 NAV-to-NAV 總回報
        "return_3y": 14.80,  # 3 年累積年化總回報
        "holdings_count": "80+ 隻資產",
        "company_name": "友邦保險 (AIA Investment Management)",
        "company_profile": [
            "<b>亞太壽險與資產管理巨擘</b>：友邦保險為亞太區最大獨立上市壽險集團，旗下投資團隊管理龐大長期資產。",
            "<b>亞太/環球高股息股票策略</b>：聚焦具備高股息、強勁自由現金流與資本增長潛力之藍籌企業。",
            "<b>期權權利金覆蓋增強 (Option Overlay)</b>：透過適度賣出看漲期權 (Covered Call) 獲取權利金，補足派息並平滑波動。"
        ],
        "score": "77.5",
        "score_ratio": "16.52",
        "risk_derivatives": {
            "has_high_risk": False,
            "primary_type": "Covered Call (Option Overlay)",
            "exposure_pct": "15.00%+",
            "display_html": "<span class='badge-yellow'>🟡 Covered Call (L2)</span>",
            "risk_level": "L2",
            "detail_note": "運用期權覆蓋策略 (Covered Call) 賣出 Call Option 獲取額外權利金增強收益 (無 144A 私募 ELN 風險)"
        },
        "summary": "友邦股票入息基金 (Z51) 綜合風險評估得分為 77.5 分 (健康度黃/綠燈良好)。經風控核算：雖然分類為股票基金，但實務上運用約 15%+ 之 Covered Call 看漲期權覆蓋策略獲取權利金，故在 Dashboard 上更正補回『 Covered Call (L2) 』結構標籤；因其期權均建立於實體持有正股之上，無 144A 私募 ELN 違約爆點，維度三取得 5.0/5 滿分。",
        "kpis": {
            "p1": "8.10%",
            "p2": "4.20% 股票股息", "p2_delta": "🟢 股票股息 + Option 權利金雙收益", "p2_color": "normal",
            "p3": "股票基金", "p3_delta": "🟢 全球與亞太高股息藍籌 100%", "p3_color": "normal",
            "p4": "Beta 0.92", "p4_delta": "🟢 3年波幅 12.10% | 降噪能力優良", "p4_color": "normal",
            "p5": "4.50%", "p5_delta": "🟢 自由現金與保證金 4.50%", "p5_color": "normal",
            "p6": "22.5%",
            "p7": "0.00%", "p7_delta": "🟢 無槓桿借貸風險", "p7_color": "normal",
            "p8": "$1,250.0 M",
            "p9": "+$52.00 M", "p9_delta": "🟢 財年實質投資淨收益與權利金", "p9_color": "normal",
            "p10": "$65.00 M", "p10_delta": "🟡 純息與權利金高覆蓋", "p10_color": "normal",
            "p11": "+$120.00 M", "p11_delta": "🟢 申購大於贖回 (淨資金流入)", "p11_color": "normal"
        },
        "radar_scores": [10.0, 15.0, 5.0, 10.0, 10.0, 10.0, 10.0, 10.0, 5.0, 5.0],
        "radar_dimensions": [
            "一、派息可持續性 (20分)", 
            "二、底層純資產質素 (15分)", 
            "三、集中度風險 (5分)", 
            "四、風險調整後回報 (10分)", 
            "五、衍生工具與槓桿 (10分)", 
            "六、大盤敏感度 (10分)", 
            "七、流動性與規模 (10分)", 
            "八、匯率風險 (10分)", 
            "九、區域集中度 (5分)", 
            "十、歷史相對波動 (5分)"
        ],
        "top10": [
            {"排名": 1, "持倉名稱": "Taiwan Semiconductor (TSMC)", "資產類別": "股票 / 晶圓代工", "佔比 (%)": "3.50%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "台積電，全球先進製程晶圓代工龍頭。"},
            {"排名": 2, "持倉名稱": "Samsung Electronics", "資產類別": "股票 / 消費電子", "佔比 (%)": "2.80%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "三星電子，全球記憶體與面板巨擘。"},
            {"排名": 3, "持倉名稱": "Microsoft Corp", "資產類別": "股票及 Option / 科技龍頭", "佔比 (%)": "2.50%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "微軟，全球軟體與 AI 雲端平台巨人。"},
            {"排名": 4, "持倉名稱": "AIA Group Ltd", "資產類別": "股票 / 金融保險", "佔比 (%)": "2.10%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "友邦保險，亞太壽險龍頭。"},
            {"排名": 5, "持倉名稱": "Tencent Holdings Ltd", "資產類別": "股票及 Option / 網絡服務", "佔比 (%)": "1.90%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "騰訊，全球社群與遊戲娛樂巨擘。"},
            {"排名": 6, "持倉名稱": "BHP Group Ltd", "資產類別": "股票 / 資源採礦", "佔比 (%)": "1.70%", "品質": "良好", "badge": "<span class='quality-badge-green'>🟢 良好 (高息)</span>", "bg": "必和必拓，全球最大資源採礦龍頭之一。"},
            {"排名": 7, "持倉名稱": "DBS Group Holdings", "資產類別": "股票 / 區域金融", "佔比 (%)": "1.60%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "星展銀行，東南亞最大商業銀行。"},
            {"排名": 8, "持倉名稱": "Commonwealth Bank of Australia", "資產類別": "股票 / 澳洲金融", "佔比 (%)": "1.50%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "澳洲聯邦銀行，澳洲資產規模最大商業銀行。"},
            {"排名": 9, "持倉名稱": "Broadcom Inc", "資產類別": "股票 / 通訊半導體", "佔比 (%)": "1.40%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "博通，客製化 AI 晶片龍頭。"},
            {"排名": 10, "持倉名稱": "Reliance Industries Ltd", "資產類別": "股票 / 新興綜合", "佔比 (%)": "1.30%", "品質": "良好", "badge": "<span class='quality-badge-green'>🟢 良好 (新興)</span>", "bg": "信實工業，印度最大民營綜合企業。"}
        ],
        "history_div": [],
        "composition_div": [],
        "sector_dist": [
            ["資訊科技", "26.50%"],
            ["金融", "22.10%"],
            ["非必需消費", "11.20%"],
            ["通訊服務", "9.50%"],
            ["工業及資源", "8.70%"]
        ],
        "rating_dist": [
            ["亞太及環球高股息股票", "100.00%"]
        ],
        "geo_dist_history": [],
        "eval_table": [
            ["一、派息可持續性", "純股息與 Option 權利金覆蓋率", "• 20分: 覆蓋率 ≥ 100%<br>• 10分: 60% ≤ 覆蓋率 < 100%", "• 股息收益率約 4.2%，其餘 3.9% 由 Covered Call 權利金補足。<br>👉 評予 10 分。", "10.0 / 20", "<span class='quality-badge-yellow'>🟡 Option 權利金補足</span>"],
            ["二、底層純資產質素", "持倉藍籌度與企業護城河", "• 15分: 頂級藍籌<br>• 0分: 投機股過高", "• 100% 重倉亞太及環球高股息藍籌正股 (台積電, 三星, 微軟)。<br>👉 獲 15 分滿分。", "15.0 / 15", "<span class='quality-badge-green'>✔ 高股息藍籌正股</span>"],
            ["三、集中度風險", "前十大持倉佔比", "• 5分: 前十 < 30%", "• 前 10 大持倉合計 21.80%。<br>👉 持倉極度分散，獲 5 分滿分。", "5.0 / 5", "<span class='quality-badge-green'>✔ 極度分散 (21.8%)</span>"],
            ["四、風險調整後回報", "夏普比率 (Sharpe)", "• 10分: Sharpe > 0.8", "• 近 3 年年化總回報 +14.80%，風險收益比優良。<br>👉 獲 10 分滿分。", "10.0 / 10", "<span class='quality-badge-green'>✔ 歷史回報優良</span>"],
            ["五、衍生工具與槓桿風險", "Covered Call 結構審計", "• 10分: 無 144A ELN 剛性熔斷", "• 採用 Covered Call 策略，未持有一切 144A ELN 私募商品，無對手方違約爆點。<br>👉 獲 10 分滿分。", "10.0 / 10", "<span class='quality-badge-green'>🟢 Covered Call (無 ELN)</span>"]
        ]
    }
}
