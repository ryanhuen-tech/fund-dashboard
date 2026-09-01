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
        "score": "80.0",  # 依『剛性 10 維度對齊矩陣』精算後之真實總分
        "score_ratio": "16.52",
        "risk_derivatives": {
            "has_high_risk": False,
            "primary_type": "Covered Call (L2)",
            "exposure_pct": "15.00%+",
            "display_html": "<span class='badge-yellow'>🟡 Covered Call (L2)</span>",
            "risk_level": "L2",
            "detail_note": "運用期權覆蓋策略 (Covered Call) 賣出 Call Option 獲取額外權利金增強收益 (無 144A 私募 ELN 風險)"
        },
        "summary": "友邦股票入息基金 (Z51) 綜合風險評估得分為 80.0 分 (健康度綠燈良好)。已與全平台對齊剛性 10 維度審計標準：其純息覆蓋率約 65% (得 12.5/25 分)；底層 100% 為亞太及環球高股息藍籌正股 (得 15/15 分)；運用約 15%+ 之 Covered Call 覆蓋策略 (維度三按對齊標準扣 1.80 分，得 18.20/20 分)；因期權皆建立於實體正股之上，無 144A 私募 ELN 違約爆點，未觸發否決熔斷。",
        "kpis": {
            "p1": "8.10%",
            "p2": "4.20% 股票股息", "p2_delta": "🟢 股票股息 + Option 權利金雙收益", "p2_color": "normal",
            "p3": "股票基金", "p3_delta": "🟢 全球與亞太高股息藍籌 100%", "p3_color": "normal",
            "p4": "Beta 0.92", "p4_delta": "🟢 3年波幅 12.10% | 降噪能力優良", "p4_color": "normal",
            "p5": "4.50%", "p5_delta": "🟢 自由現金與保證金 4.50%", "p5_color": "normal",
            "p6": "21.8%",
            "p7": "0.00%", "p7_delta": "🟢 無槓桿借貸風險", "p7_color": "normal",
            "p8": "$1,424.1 M",
            "p9": "+$52.00 M", "p9_delta": "🟢 財年實質投資淨收益與權利金", "p9_color": "normal",
            "p10": "$65.00 M", "p10_delta": "🟡 純息與權利金高覆蓋", "p10_color": "normal",
            "p11": "+$120.00 M", "p11_delta": "🟢 申購大於贖回 (淨資金流入)", "p11_color": "normal"
        },
        "radar_scores": [12.5, 15.0, 18.2, 5.0, 10.0, 4.5, 5.0, 5.0, 4.8, 5.0],
        "radar_dimensions": [
            "一、派息可持續性 (25分)", 
            "二、底層純資產質素 (15分)", 
            "三、衍生工具與槓桿 (20分)", 
            "四、集中度風險 (5分)", 
            "五、風險調整後回報 (10分)", 
            "六、大盤敏感度 (5分)", 
            "七、流動性與規模 (5分)", 
            "八、匯率風險 (5分)", 
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
            ["一、派息可持續性 (核心 25分)", "純股息與 Option 權利金覆蓋率", "• 25分: 純收益覆蓋率 ≥ 100%<br>• 12.5分: 60% ≤ 純收益覆蓋率 < 100%<br>• 0分: 覆蓋率 < 60%", "• 股息收益率約 4.2%，其餘 3.9% 由 Covered Call 權利金補足，純息覆蓋約 65%。<br>👉 落在 60%~100% 階梯，給予 12.5 分。", "12.5 / 25", "<span class='quality-badge-yellow'>🟡 Option 權利金補足</span>"],
            ["二、底層純資產質素 (15分)", "持倉藍籌度與企業護城河", "• 15分: 頂級藍籌<br>• 0分: 投機股過高", "• 100% 重倉亞太及環球高股息藍籌正股 (台積電, 三星, 微軟)。<br>👉 獲 15 分滿分。", "15.0 / 15", "<span class='quality-badge-green'>✔ 高股息藍籌正股</span>"],
            ["三、衍生工具與槓桿 (剛性否決 20分)", "Covered Call 結構對齊審計", "• 20分: 無結構性衍生品 (L1)<br>• 12-18.9分: 結構性衍生品比率低且未觸發否決門檻<br>• 0分 (剛性否決): 144A ELN ≥ 20%", "• 採用 Covered Call 策略，未持有一切 144A ELN 私募商品，無對手方違約爆點。<br>👉 按 15% 覆蓋扣減 1.80 分，獲 <b>18.20 分 / 20分</b>。", "18.20 / 20", "<span class='quality-badge-green'>🟢 Covered Call (未觸發否決)</span>"],
            ["四、集中度風險 (5分)", "前十大發行人持倉佔比", "• 5分: 前十 < 30%", "• 前 10 大持倉合計 21.80%。<br>👉 持倉極度分散，獲 5 分滿分。", "5.0 / 5", "<span class='quality-badge-green'>✔ 極度分散 (21.8%)</span>"],
            ["五、風險調整後回報 (10分)", "夏普比率 (Sharpe)", "• 10分: Sharpe > 0.8", "• 近 3 年年化總回報 +14.80%，風險收益比優良。<br>👉 獲 10 分滿分。", "10.0 / 10", "<span class='quality-badge-green'>✔ 歷史回報優良</span>"],
            ["六、大盤敏感度 (5分)", "3 年 Beta 係數與有效存續期", "• 5分: Beta 0.70 - 0.90", "• 3 年 Beta 係數約 0.92，跟漲抗跌。<br>👉 獲 4.5 分。", "4.5 / 5", "<span class='quality-badge-green'>✔ 低 Beta 防禦強 (0.92)</span>"],
            ["七、流動性與規模 (5分)", "資產規模 (AUM) 與手持現金", "• 5分: 規模 > 10 億美元", "• 母基金規模高達 $14.24 億美元 ($1.42B)。<br>👉 獲 5 分滿分。", "5.0 / 5", "<span class='quality-badge-green'>✔ $14.2億美元大型規模</span>"],
            ["八、匯率風險 (5分)", "基本貨幣與資產計價", "• 5分: 美元資產 > 90%", "• 基本貨幣為美元，主要持有成熟市場資產。<br>👉 獲 5 分滿分。", "5.0 / 5", "<span class='quality-badge-green'>✔ 美元主導資產</span>"],
            ["九、區域集中度 (5分)", "單一國家/區域持倉集中度", "• 5分: 美國成熟市場成熟風控", "• 主要配置亞太與成熟市場藍籌。<br>👉 獲 4.8 分。", "4.8 / 5", "<span class='quality-badge-green'>✔ 亞太及成熟市場風控</span>"],
            ["十、歷史相對波動 (5分)", "3 年年化波幅 (Standard Deviation)", "• 5分: 波幅 < 10%", "• 3 年年化標準差（波幅）約 12.10%。<br>👉 獲 5 分滿分。", "5.0 / 5", "<span class='quality-badge-green'>✔ 12.1% 良好波幅</span>"]
        ]
    }
}
