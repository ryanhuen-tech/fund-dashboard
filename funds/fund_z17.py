# funds/fund_z17.py

DATA_Z17 = {
    "Z17 貝萊德系統分析環球股票高息基金 (上月派息: 7.90%)": {
        "code": "Z17",
        "zh": "貝萊德環球基金 - 系統分析環球股票高息基金 (A2 美元)",
        "en": "BlackRock Global Funds - Systematic Global Equity High Income Fund (Class A2 USD)",
        "category": "股票基金",
        "star": "⭐⭐⭐⭐",
        "star_num": 4,
        "last_yield": 7.90,  # 最新年化派息率
        "return_1y": 15.21,  # 1 年 NAV-to-NAV 總回報
        "return_3y": 14.17,  # 3 年累積年化總回報
        "holdings_count": "350+ 隻資產",
        "company_name": "貝萊德資產管理 (BlackRock)",
        "company_profile": [
            "<b>全球最大資產管理巨擘</b>：貝萊德為全球資產管理龍頭，旗下系統分析高息策略運用量化模型進行全球股票挑選。",
            "<b>Covered Call 權利金收益增強</b>：透過系統化賣出股票看漲期權 (Call Options) 獲取額外權利金，平滑組合波動並提供高派息。",
            "<b>量化模型動態選股</b>：結合大數據與AI機器學習，針對全球超過千隻藍籌股票進行多因子量化篩選。"
        ],
        "score": "87.5",
        "score_ratio": "15.21",
        "risk_derivatives": {
            "has_high_risk": False,
            "primary_type": "Covered Call / Swaps",
            "exposure_pct": "30.00%+",
            "display_html": "<span class='badge-yellow'>🟡 Covered Call / Swaps (L2/L4)</span>",
            "risk_level": "L2/L4",
            "detail_note": "運用系統化賣出 Covered Call 期權與 Swaps 獲取權利金增強收益 (封頂上漲空間)"
        },
        "summary": "貝萊德系統分析環球股票高息基金 (Z17) 綜合風險評估得分為 87.5 分 (健康度綠燈極佳)。經買方風控核算：雖然分類為股票基金，但實務上運用約 30%+ 之 Covered Call 看漲期權與衍生品合約獲取權利金補貼，故在 Dashboard 上更正補回『 Covered Call / Swaps 』結構標籤；因其期權均建立於實體持有正股之上，無 144A 私募 ELN 違約爆點，維度三取得 10.0/10 滿分。",
        "kpis": {
            "p1": "7.90%",
            "p2": "3.50% 股息收益", "p2_delta": "🟢 股票股息 + Option 權利金雙增強", "p2_color": "normal",
            "p3": "股票基金", "p3_delta": "🟢 全球高股息藍籌 100%", "p3_color": "normal",
            "p4": "Beta 0.88", "p4_delta": "🟢 3年波幅 11.20% | 降噪能力優良", "p4_color": "normal",
            "p5": "5.20%", "p5_delta": "🟢 自由現金與衍生品保證金 5.20%", "p5_color": "normal",
            "p6": "15.8%",
            "p7": "0.10%", "p7_delta": "🟢 無槓桿借貸風險", "p7_color": "normal",
            "p8": "$3,850.0 M",
            "p9": "+$180.00 M", "p9_delta": "🟢 財年實質投資淨收益與權利金", "p9_color": "normal",
            "p10": "$210.00 M", "p10_delta": "🟢 派息持續性良好", "p10_color": "normal",
            "p11": "+$450.00 M", "p11_delta": "🟢 申購大於贖回 (淨資金流入)", "p11_color": "normal"
        },
        "radar_scores": [10.0, 15.0, 2.5, 10.0, 10.0, 10.0, 10.0, 10.0, 5.0, 5.0],
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
            {"排名": 1, "持倉名稱": "Microsoft Corp", "資產類別": "股票及 Option / 科技龍頭", "佔比 (%)": "3.80%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "微軟，全球 AI 與雲端軟體巨人。"},
            {"排名": 2, "持倉名稱": "Apple Inc", "資產類別": "股票及 Option / 消費電子", "佔比 (%)": "3.20%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "蘋果公司，全球消費電子巨擘。"},
            {"排名": 3, "持倉名稱": "NVIDIA Corp", "資產類別": "股票及 Option / 半導體霸主", "佔比 (%)": "2.90%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "輝達，全球 AI 晶片龍頭。"},
            {"排名": 4, "持倉名稱": "Amazon.com Inc", "資產類別": "股票及 Option / 零售與雲端", "佔比 (%)": "2.10%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "亞馬遜，全球電商與 AWS 雲端巨頭。"},
            {"排名": 5, "持倉名稱": "Alphabet Inc", "資產類別": "股票及 Option / 網絡服務", "佔比 (%)": "1.80%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "Google 母公司，數位廣告與搜尋霸主。"},
            {"排名": 6, "持倉名稱": "Meta Platforms Inc", "資產類別": "股票 / 社群平台", "佔比 (%)": "1.50%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "Meta，全球社群網路龍頭。"},
            {"排名": 7, "持倉名稱": "Broadcom Inc", "資產類別": "股票 / 通訊半導體", "佔比 (%)": "1.30%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "博通，客製化 AI 晶片龍頭。"},
            {"排名": 8, "持倉名稱": "JPMorgan Chase & Co", "資產類別": "股票 / 金融龍頭", "佔比 (%)": "1.10%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "摩根大通，美國最大商業銀行。"},
            {"排名": 9, "持倉名稱": "Eli Lilly & Co", "資產類別": "股票 / 生物製藥", "佔比 (%)": "1.00%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "禮來藥廠，減重藥龍頭。"},
            {"排名": 10, "持倉名稱": "Exxon Mobil Corp", "資產類別": "股票 / 能源龍頭", "佔比 (%)": "0.90%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "埃克森美孚，全球最大石油企業之一。"}
        ],
        "history_div": [],
        "composition_div": [],
        "sector_dist": [
            ["資訊科技", "28.50%"],
            ["金融", "16.20%"],
            ["健康護理", "12.40%"],
            ["非必需消費", "10.50%"],
            ["通訊服務", "9.80%"]
        ],
        "rating_dist": [
            ["環球藍籌股票", "100.00%"]
        ],
        "geo_dist_history": [],
        "eval_table": [
            ["一、派息可持續性", "純投資淨收益與 Covered Call 權利金覆蓋率", "• 20分: 覆蓋率 ≥ 100%<br>• 10分: 60% ≤ 覆蓋率 < 100%", "• 股息收益率約 3.5%，其餘 4.4% 由賣出 Call Option 權利金補足。<br>👉 評予 10 分。", "10.0 / 20", "<span class='quality-badge-yellow'>🟡 Option 權利金補足</span>"],
            ["二、底層純資產質素", "持倉藍籌度與企業護城河", "• 15分: 頂級藍籌<br>• 0分: 垃圾股過高", "• 100% 重倉美股與環球頂級科技、金融藍籌正股。<br>👉 獲 15 分滿分。", "15.0 / 15", "<span class='quality-badge-green'>✔ 環球藍籌正股</span>"],
            ["三、集中度風險", "前十大持倉佔比", "• 5分: 前十 < 30%", "• 前 10 大持倉僅佔 19.4%。<br>👉 持倉極度分散，獲 2.5 分。", "2.5 / 5", "<span class='quality-badge-green'>✔ 極度分散 (19.4%)</span>"],
            ["四、風險調整後回報", "夏普比率 (Sharpe)", "• 10分: Sharpe > 0.8", "• 近 3 年年化總回報 +14.17%，風險收益比優良。<br>👉 獲 10 分滿分。", "10.0 / 10", "<span class='quality-badge-green'>✔ 歷史回報優良</span>"],
            ["五、衍生工具與槓桿風險", "Covered Call / Swaps 結構審計", "• 10分: 無 144A ELN 剛性熔斷", "• 採用系統化 Covered Call 策略 (L2 級 ETD)，未持有一切 144A ELN 私募商品，無違約爆點。<br>👉 獲 10 分滿分。", "10.0 / 10", "<span class='quality-badge-green'>🟢 Covered Call (無 ELN)</span>"]
        ]
    }
}
