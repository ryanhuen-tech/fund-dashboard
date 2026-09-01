# funds/fund_z04.py

DATA_Z04 = {
    "Z04 安聯環球高息股票基金 (上月派息: 7.85%)": {
        "code": "Z04",
        "zh": "安聯環球投資選擇基金 - 安聯環球高息股票基金 (AMg每月派息類股份 美元)",
        "en": "Allianz Global Investors Fund - Allianz Global Equity Income (Class AMg USD)",
        "category": "股票基金",
        "star": "⭐⭐⭐⭐",
        "star_num": 4,
        "last_yield": 7.85,  # 最新年化派息率
        "return_1y": 13.80,  # 1 年 NAV-to-NAV 總回報
        "return_3y": 15.60,  # 3 年累積年化總回報
        "holdings_count": "70+ 隻資產",
        "company_name": "安聯環球投資 (Allianz Global Investors)",
        "company_profile": [
            "<b>全球高股息資產專家</b>：安聯環球投資旗艦純股票高息產品，聚焦全球優質高股息藍籌企業。",
            "<b>Covered Call 權利金增強</b>：採用安聯經典 Covered Call 期權覆蓋策略，賣出交易所掛牌看漲期權，鎖定穩定現金流。",
            "<b>嚴格品質與護城河篩選</b>：結合嚴格財報資產負債表審核，嚴防高股息陷阱 (Dividend Traps)。"
        ],
        "score": "82.5",
        "score_ratio": "13.80",
        "risk_derivatives": {
            "has_high_risk": False,
            "primary_type": "Covered Call (ETD)",
            "exposure_pct": "25.00%+",
            "display_html": "<span class='badge-yellow'>🟡 Covered Call (L2)</span>",
            "risk_level": "L2",
            "detail_note": "約 25%+ 賣出 Call Option (交易所 ETD 掛牌，無 144A 私募信用風險)"
        },
        "summary": "安聯環球高息股票基金 (Z04) 綜合風險評估得分為 82.5 分 (健康度綠燈良好)。經風控核算：雖然分類為股票基金，但實務上運用約 25%+ 之 Covered Call 覆蓋策略獲取權利金，故在 Dashboard 上更正補回『 Covered Call (L2) 』結構標籤；因其期權均為交易所 ETD 掛牌，無 144A 私募 ELN 違約爆點，維度三取得 10.0/10 滿分。",
        "kpis": {
            "p1": "7.85%",
            "p2": "4.10% 股票股息", "p2_delta": "🟢 股票股息 + Option 權利金雙增強", "p2_color": "normal",
            "p3": "股票基金", "p3_delta": "🟢 全球高股息藍籌 100%", "p3_color": "normal",
            "p4": "Beta 0.85", "p4_delta": "🟢 3年波幅 10.80% | 降噪能力優良", "p4_color": "normal",
            "p5": "6.10%", "p5_delta": "🟢 現金與期權保證金 6.10%", "p5_color": "normal",
            "p6": "24.2%",
            "p7": "0.00%", "p7_delta": "🟢 無槓桿借貸風險", "p7_color": "normal",
            "p8": "$2,150.0 M",
            "p9": "+$95.00 M", "p9_delta": "🟢 財年實質投資淨收益與權利金", "p9_color": "normal",
            "p10": "$115.00 M", "p10_delta": "🟢 派息持續性良好", "p10_color": "normal",
            "p11": "+$180.00 M", "p11_delta": "🟢 申購大於贖回 (淨資金流入)", "p11_color": "normal"
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
            {"排名": 1, "持倉名稱": "Microsoft Corp", "資產類別": "股票及 Option / 科技龍頭", "佔比 (%)": "3.50%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "微軟，全球軟體與 AI 雲端平台巨人。"},
            {"排名": 2, "持倉名稱": "Broadcom Inc", "資產類別": "股票及 Option / 通訊半導體", "佔比 (%)": "2.80%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "博通，客製化 AI 晶片與網通半導體巨頭。"},
            {"排名": 3, "持倉名稱": "Shell plc", "資產類別": "股票 / 能源龍頭", "佔比 (%)": "2.60%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "殼牌公司，全球跨國天然氣與石油能源巨擘。"},
            {"排名": 4, "持倉名稱": "AstraZeneca plc", "資產類別": "股票 / 製藥龍頭", "佔比 (%)": "2.40%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "阿斯利康，全球腫瘤與生物製藥巨擘。"},
            {"排名": 5, "持倉名稱": "JPMorgan Chase & Co", "資產類別": "股票 / 金融龍頭", "佔比 (%)": "2.20%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "摩根大通，美國最大商業金融巨擘。"},
            {"排名": 6, "持倉名稱": "Nestle SA", "資產類別": "股票 / 消費龍頭", "佔比 (%)": "2.00%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "雀巢，全球食品與飲料龍頭。"},
            {"排名": 7, "持倉名稱": "Procter & Gamble Co", "資產類別": "股票 / 日常消費", "佔比 (%)": "1.90%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "寶潔公司，日常消費龍頭。"},
            {"排名": 8, "持倉名稱": "Taiwan Semiconductor (TSMC)", "資產類別": "股票 / 晶圓代工", "佔比 (%)": "1.80%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "台積電，全球晶圓代工龍頭。"},
            {"排名": 9, "持倉名稱": "Exxon Mobil Corp", "資產類別": "股票 / 能源龍頭", "佔比 (%)": "1.70%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "埃克森美孚，全球最大石油企業之一。"},
            {"排名": 10, "持倉名稱": "Novartis AG", "資產類別": "股票 / 生物製藥", "佔比 (%)": "1.60%", "品質": "極佳", "badge": "<span class='quality-badge-green'>🟢 極佳 (藍籌)</span>", "bg": "諾華藥廠，全球大型生技製藥巨擘。"}
        ],
        "history_div": [],
        "composition_div": [],
        "sector_dist": [
            ["資訊科技", "24.50%"],
            ["金融", "18.20%"],
            ["健康護理", "14.60%"],
            ["必需消費", "12.10%"],
            ["能源", "9.50%"]
        ],
        "rating_dist": [
            ["環球高股息藍籌股票", "100.00%"]
        ],
        "geo_dist_history": [],
        "eval_table": [
            ["一、派息可持續性", "純股息與 Option 權利金覆蓋率", "• 20分: 覆蓋率 ≥ 100%<br>• 10分: 60% ≤ 覆蓋率 < 100%", "• 股息收益率約 4.1%，其餘 3.75% 由 Covered Call 權利金補足。<br>👉 評予 10 分。", "10.0 / 20", "<span class='quality-badge-yellow'>🟡 Option 權利金補足</span>"],
            ["二、底層純資產質素", "持倉藍籌度與企業護城河", "• 15分: 頂級藍籌<br>• 0分: 投機股過高", "• 100% 重倉微軟, 殼牌, 諾華等環球頂級高股息藍籌正股。<br>👉 獲 15 分滿分。", "15.0 / 15", "<span class='quality-badge-green'>✔ 環球高股息藍籌正股</span>"],
            ["三、集中度風險", "前十大持倉佔比", "• 5分: 前十 < 30%", "• 前 10 大持倉合計 21.40%。<br>👉 持倉極度分散，獲 5 分滿分。", "5.0 / 5", "<span class='quality-badge-green'>✔ 極度分散 (21.4%)</span>"],
            ["四、風險調整後回報", "夏普比率 (Sharpe)", "• 10分: Sharpe > 0.8", "• 近 3 年年化總回報 +15.60%，風險收益比優良。<br>👉 獲 10 分滿分。", "10.0 / 10", "<span class='quality-badge-green'>✔ 歷史回報優良</span>"],
            ["五、衍生工具與槓桿風險", "Covered Call 結構審計", "• 10分: 無 144A ELN 剛性熔斷", "• 採用 Covered Call 策略 (L2 級 ETD)，未持有一切 144A ELN 私募商品，無對手方違約爆點。<br>👉 獲 10 分滿分。", "10.0 / 10", "<span class='quality-badge-green'>🟢 Covered Call (無 ELN)</span>"]
        ]
    }
}
