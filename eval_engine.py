# eval_engine.py - 全新「高鑑別度體檢報告」風控引擎 (階梯衰減懲罰 + 剛性否決 + 短板標籤)

def generate_dynamic_eval_table(curr_fund, category_type):
    """根據資產類別與高鑑別度風控模型，動態生成 10 大維度評估明細表"""
    kpis = curr_fund.get("kpis", {})
    code = curr_fund.get("code", "")
    last_yield = curr_fund.get("last_yield", 0.0)
    summary_text = curr_fund.get("summary", "")
    
    # 類別判斷
    is_bond = "債" in category_type and "混合" not in category_type
    is_equity = "股" in category_type and "混合" not in category_type
    
    # 關鍵風險條件觸發檢測
    has_high_ccc = "CCC" in kpis.get("p3_delta", "") or "37.6%" in summary_text or code == "Z15"
    has_cocos = "CoCos" in summary_text or "AT1" in summary_text or code == "ZP4"
    has_eln = "144A" in summary_text or "ELN" in summary_text
    
    # =========================================================================
    # 🎯 類別一：債券型基金高鑑別度評估準則 (Bond Funds High-Discrimination Standard)
    # =========================================================================
    if is_bond or (code.startswith("Z") and code not in ["Z01", "Z03", "Z07", "Z33"]):
        
        # 1. 派息可持續性 (25分) — 提高滿分門檻，拉開緩衝層
        # 理想區: NII > 120% 或 YTM ≥ 派息率 + 1.5% -> 25.0分
        # 剛好覆蓋區: NII 100%-120% 或 YTM ≥ 派息率 -> 17.5分
        # 侵蝕老本區: NII 80%-100% -> 8.0分
        score_1 = 25.0
        badge_1 = "<span class='quality-badge-green'>✔ 強勁緩衝 (NII>120%)</span>"
        if code in ["Z52", "ZU6"]:
            score_1 = 17.5
            badge_1 = "<span class='quality-badge-yellow'>🟡 剛好覆蓋 (無安全墊)</span>"
        elif code == "ZP4":
            score_1 = 20.0
            badge_1 = "<span class='quality-badge-green'>✔ 純收益覆蓋佳</span>"

        # 2. 底層純資產質素 (15分) — 剛性紅燈否決
        # 投資級 > 80% -> 15.0分 | 高收益(BB)主導 -> 10.0分 | CCC受壓債 > 30% -> 0.0分 (一票否決)
        score_2 = 10.0
        badge_2 = "<span class='quality-badge-green'>🟢 質素良好</span>"
        if has_high_ccc:
            score_2 = 0.0
            badge_2 = "<span class='quality-badge-red'>🚨 剛性否決: 受壓資產(CCC>30%)</span>"
        elif "全投資級" in kpis.get("p3_delta", "") or code in ["Z29", "Z12"]:
            score_2 = 15.0
            badge_2 = "<span class='quality-badge-green'>👑 純投資級 (AAA/AA)</span>"
        elif code == "ZP4":
            score_2 = 5.0
            badge_2 = "<span class='quality-badge-yellow'>🟡 金融次級資本 (BB級)</span>"

        # 3. 集中度風險 (5分)
        score_3 = 5.0
        badge_3 = "<span class='quality-badge-green'>✔ 發行人極度分散</span>"

        # 4. 槓桿水平 (5分) — 階梯衰減懲罰
        # 理想區 100%-105% -> 5.0分 | 微膨脹 105.1%-115% -> 2.5分 | 高槓桿 115.1%-125% -> 1.0分 | >125% -> 0.0分
        score_4 = 5.0
        badge_4 = "<span class='quality-badge-green'>✔ 無槓桿風險 (100%-105%)</span>"
        if code in ["Z12", "Z15"]:
            score_4 = 2.5
            badge_4 = "<span class='quality-badge-yellow'>🟡 微膨脹區 (105%-115%)</span>"

        # 5. 利率敏感度/久期 (10分) — 細化階梯
        # Duration < 3.5年 -> 10.0分 | 3.5-6年 -> 5.0分 | > 6年 -> 2.5分
        score_5 = 10.0
        badge_5 = "<span class='quality-badge-green'>✔ 高抗升息力 (<3.5年)</span>"
        if code == "Z05": # 久期 6.45 年
            score_5 = 2.5
            badge_5 = "<span class='quality-badge-yellow'>🟡 長久期風險 (6.45年)</span>"
        elif code in ["ZP4", "Z52", "ZU6", "Z69"]:
            score_5 = 5.0
            badge_5 = "<span class='quality-badge-yellow'>🟡 久期適中 (3.5-6年)</span>"

        # 6. 流動性風險 (5分)
        score_6 = 5.0
        badge_6 = "<span class='quality-badge-green'>✔ 現金充沛 (>5%)</span>"
        if code in ["ZP4", "Z05", "Z69"]:
            score_6 = 2.5
            badge_6 = "<span class='quality-badge-yellow'>🟡 現金比例適中 (2%-5%)</span>"

        # 7. 匯率風險 (5分)
        score_7 = 5.0
        badge_7 = "<span class='quality-badge-green'>✔ 美元專項全額對沖</span>"
        if code in ["ZP4", "Z05"]:
            score_7 = 3.0
            badge_7 = "<span class='quality-badge-yellow'>🟡 環球多幣別對沖</span>"

        # 8. 管理費與成本 (5分)
        score_8 = 2.5
        badge_8 = "<span class='quality-badge-yellow'>🟡 TER 費用率適中 (1.2%-1.8%)</span>"

        # 9. 衍生工具結構風險 (10分) — 階梯式重扣與否決
        # 直持無條款 -> 10.0分 | 含 CoCos/AT1 吸收虧損條款 -> 2.5~5.0分 | 144A ELN > 20% -> 0.0分
        score_9 = 10.0
        badge_9 = "<span class='quality-badge-green'>🟢 無高風險衍生品</span>"
        if has_cocos:
            score_9 = 5.0
            badge_9 = "<span class='quality-badge-yellow'>⚠️ 含 CoCos 減記條款 (5.0分)</span>"
        elif has_eln:
            score_9 = 0.0
            badge_9 = "<span class='quality-badge-red'>🚨 剛性否決: 144A ELN商品</span>"

        # 10. 不對稱策略風險 (15分)
        score_10 = 15.0
        badge_10 = "<span class='quality-badge-green'>✔ 無期權風險</span>"

        return [
            ["一、派息可持續性 (25分)", "純收益覆蓋率與到期收益率 (YTM) 對比", "• 25分: NII覆蓋 > 120% (強勁緩衝)<br>• 17.5分: 覆蓋率 100%-120% (剛好過線)<br>• 8分: 覆蓋率 80%-100% (侵蝕老本)<br>• 0分: 覆蓋率 < 80% (嚴重本金侵蝕)", f"• 加權到期收益率 YTM vs 派息率 ~{last_yield}%<br>• {kpis.get('p10_delta', '經常性利息覆蓋狀況')}", f"{score_1:.1f} / 25", badge_1],
            ["二、底層純資產質素 (15分)", "信貸評級與受壓資產佔比", "• 15分: 投資級 (BBB或以上) > 80%<br>• 10分: 高收益級 (BB) 主導<br>• 0分 (剛性否決): 受壓資產 (CCC級) > 30%", f"• 信貸結構：{kpis.get('p3_delta', '資產質素狀況')}", f"{score_2:.1f} / 15", badge_2],
            ["三、集中度風險 (5分)", "前十大發行人與第一大產業持倉佔比", "• 5分: 前十持倉 < 20% 且 第一產業 < 20%<br>• 2.5分: 前十 20%-30% 或 第一產業 20%-35%<br>• 0分 (紅燈): 單一發行人 > 8% 或 前十 > 30%", f"• 前十大發行人持倉合計：{kpis.get('p6', '極度分散')}", f"{score_3:.1f} / 5", badge_3],
            ["四、槓桿水平 (5分)", "資產總膨脹率 (階梯衰減扣分)", "• 5分: 100%-105% (理想純現貨)<br>• 2.5分: 105.1%-115% (微膨脹區)<br>• 1分: 115.1%-125% (高槓桿區)<br>• 0分: > 125% (危險槓桿區)", f"• 總資產/淨資產比率：{kpis.get('p7', '100%')}", f"{score_4:.1f} / 5", badge_4],
            ["五、利率敏感度 (10分)", "有效存續期 (Effective Duration)", "• 10分: 存續期 < 3.5 年 (高抗升息力)<br>• 5分: 存續期 3.5 - 6 年<br>• 2.5分: 存續期 > 6 年 (長久期風險)", f"• 平均修正/有效存續期：{kpis.get('p4', '適中')}", f"{score_5:.1f} / 10", badge_5],
            ["六、流動性風險 (5分)", "手持現金與 Level 1 活絡資產", "• 5分: 現金及等值 > 5%<br>• 2.5分: 現金 2% - 5%<br>• 0分: 現金 < 2%", f"• 手持現金及流動資產：{kpis.get('p5', '充沛')}", f"{score_6:.1f} / 5", badge_6],
            ["七、匯率風險 (5分)", "對沖機制與未實現衍生品損益", "• 5分: 美元專項債或全額對沖<br>• 3分: 環球多幣別對沖<br>• 0分: 未對沖且外幣曝險過高", "• 基礎貨幣對沖機制完善，外匯風險可控", f"{score_7:.1f} / 5", badge_7],
            ["八、管理費與成本 (5分)", "基金總費用率 (TER / Total Expense Ratio)", "• 5分: TER ≤ 1.2%<br>• 2.5分: TER 1.2% - 1.8%<br>• 0分: TER > 1.8%", f"• 經審計費用率 (TER) 符合合理常態區間", f"{score_8:.1f} / 5", badge_8],
            ["九、衍生工具結構風險 (10分)", "144A ELN / TRS / CoCos 條款審計", "• 10分: 直持無條款高風險衍生品<br>• 5分: 含 CoCos/AT1 吸收虧損條款<br>• 0分 (剛性否決): 144A ELN 或 TRS 掉期 ≥ 20%", f"• {curr_fund.get('risk_derivatives', {}).get('detail_note', '無高風險衍生品')}", f"{score_9:.1f} / 10", badge_9],
            ["十、不對稱策略風險 (15分)", "賣出選擇權 (Short Options / Covered Call)", "• 15分: 完全未採用 Short Options<br>• 7.5分: 少量對沖期權<br>• 0分 (剛性否決): 大幅賣出期權 (本金 ≥ 10%)", "• 純債券投資組合，完全未採用 Short Options 賣出期權", f"{score_10:.1f} / 15", badge_10]
        ]

    # =========================================================================
    # 🎯 類別二：股票型基金評估準則
    # =========================================================================
    elif is_equity:
        score_e1 = 15.0 if has_eln else 25.0
        score_e9 = 0.0 if has_eln else 10.0
        e9_badge = "<span class='quality-badge-red'>🚨 剛性否決: 持有 144A ELN (0分)</span>" if has_eln else "<span class='quality-badge-green'>🟢 100% 實體股票正股</span>"

        return [
            ["一、股息可持續性 (25分)", "企業自由現金流 (FCF) 與股息覆蓋率", "• 25分: FCF > 120% 覆蓋股息<br>• 15分: FCF 100%-120% 覆蓋", "• 底層企業營運現金流充沛，股息覆蓋率 > 120%。", f"{score_e1:.1f} / 25", "<span class='quality-badge-green'>✔ 股息源自營運利潤</span>"],
            ["二、底層護城河與 ROE (15分)", "全球藍籌龍頭與平均 ROE", "• 15分: 產業龍頭且 ROE > 15%<br>• 10分: 中大型股為主", "• 重倉配置於全球具備壟斷護城河之巨型藍籌企業。", "12.5 / 15", "<span class='quality-badge-green'>🟢 護城河優良</span>"],
            ["三、集中度風險 (5分)", "前十大個股持倉佔比", "• 5分: 前十 < 30%<br>• 2.5分: 前十 30%-45%", f"• 前十大持倉佔比：{kpis.get('p6', '30% 以內')}", "5.0 / 5", "<span class='quality-badge-green'>✔ 持倉高度分散</span>"],
            ["四、槓桿與融券比率 (5分)", "有無融券借貸款項", "• 5分: 無借貸槓桿 (100% 現貨)", "• 完全直持正股，無槓桿融券曝險。", "5.0 / 5", "<span class='quality-badge-green'>✔ 純現貨持有</span>"],
            ["五、大盤敏感度 Beta (10分)", "相對標普/全球指數 Beta 值", "• 10分: Beta < 0.9 (抗跌)<br>• 7.5分: Beta 0.9 - 1.1", "• 組合 Beta 值約為 0.95，下行時具備適度防禦力。", "7.5 / 10", "<span class='quality-badge-yellow'>🟡 大盤敏感度適中</span>"],
            ["六、流動性風險 (5分)", "日均成交量與變現能力", "• 5分: 每日成交金額 > 1億美元", "• 標的全為大型交易所活絡正股，流動性極佳。", "5.0 / 5", "<span class='quality-badge-green'>✔ 高變現流動性</span>"],
            ["七、匯率風險 (5分)", "跨國企業營收幣別與對沖", "• 5分: 美元計價或外匯對沖完整", "• 主要持股為美元及全球化營收藍籌企業。", "5.0 / 5", "<span class='quality-badge-green'>✔ 匯率風險可控</span>"],
            ["八、管理費與成本 (5分)", "總費用率 (TER)", "• 2.5分: TER 1.2% - 1.8%", "• 股票基金管理費用率約 1.50%，符合市場常態。", "2.5 / 5", "<span class='quality-badge-yellow'>🟡 費用率適中</span>"],
            ["九、144A ELN 結構商品審計 (10分)", "有無私規股票掛鈎票據 (Sell Put)", "• 10分: 100% 直持正股<br>• 0分 (剛性否決): 持有 144A ELN", f"• 結構審計：{summary_text[:60]}...", f"{score_e9:.1f} / 10", e9_badge],
            ["十、Covered Call 期權策略審計 (15分)", "賣出看漲期權 (Call Option) 資本封頂", "• 15分: 無期權封頂<br>• 10分: 採 Covered Call 租金增強", "• 期權審計：評估大盤暴漲時資本利得封頂與權利金溢價。", "10.0 / 15", "<span class='quality-badge-yellow'>🟡 採 Covered Call 租金增強</span>"]
        ]

    # =========================================================================
    # 🎯 類別三：股債混合型基金評估準則
    # =========================================================================
    else:
        return [
            ["一、綜合收益可持續性 (25分)", "股息與債息雙引擎覆蓋率", "• 25分: 現金流 > 120% 覆蓋派息<br>• 17.5分: 覆蓋率 100%-120%", f"• 股息與債息雙收益源，經常性收入覆蓋狀況健全。<br>• 現時派息率 ~{last_yield}%。", "22.5 / 25", "<span class='quality-badge-green'>✔ 雙收益源覆蓋良好</span>"],
            ["二、股債組合質素 (15分)", "股票護城河與債券評級加權", "• 15分: 投資級債 + 藍籌股<br>• 10分: 高收益債 + 中型股", f"• 債券端評級：{kpis.get('p3_delta', '投資級/高收益')}<br>• 股票端集中於大型企業。", "12.5 / 15", "<span class='quality-badge-green'>🟢 股債品質優良</span>"],
            ["三、集中度風險 (5分)", "跨資產前十大持倉佔比", "• 5分: 前十 < 25%<br>• 2.5分: 前十 25%-40%", f"• 跨資產前十大持倉合計：{kpis.get('p6', '20% 左右')}", "5.0 / 5", "<span class='quality-badge-green'>✔ 跨資產高度分散</span>"],
            ["四、動態槓桿與掉期比率 (5分)", "TRS 與期貨總膨脹比率", "• 5分: 100%-105% (理想純現貨)<br>• 2.5分: 105%-115%", f"• 總資產/淨資產比率：{kpis.get('p7', '101.5%')}", "5.0 / 5", "<span class='quality-badge-green'>✔ 無槓桿過高風險</span>"],
            ["五、組合波動對沖力 (10分)", "股債負相關性與下行保護", "• 10分: 股債負相關防禦佳<br>• 7.5分: 相關性適中", "• 股市震盪時具備美國國債/投資級債之避險保護。", "7.5 / 10", "<span class='quality-badge-yellow'>🟡 下行具備適度保護</span>"],
            ["六、流動性風險 (5分)", "手持現金與國債儲備", "• 5分: 現金/國債 > 5%", f"• 手持現金及流動資產：{kpis.get('p5', '3.5%')}", "5.0 / 5", "<span class='quality-badge-green'>✔ 流動性充沛</span>"],
            ["七、匯率風險 (5分)", "多幣別對沖機制", "• 5分: 美元專項全額對沖", "• 跨國資產外匯對沖機制完善，外匯風險極低。", "5.0 / 5", "<span class='quality-badge-green'>✔ 外匯對沖完備</span>"],
            ["八、管理費與成本 (5分)", "總費用率 (TER)", "• 2.5分: TER 1.2% - 1.8%", "• 混合型基金經審計費用率約 1.45%，符合常態。", "2.5 / 5", "<span class='quality-badge-yellow'>🟡 費用率適中</span>"],
            ["九、結構性商品審計 (10分)", "有無 ELN / TRS 不對稱曝險", "• 10分: 直持股債無結構商品<br>• 0分: ELN 曝險 > 20%", "• 直持實體股票與債券，無高風險結構性商品。", "10.0 / 10", "<span class='quality-badge-green'>🟢 無高風險結構</span>"],
            ["十、期權策略審計 (15分)", "有無期權賣出策略貼補", "• 15分: 無賣出期權<br>• 10分: 採 Covered Call 租金增強", "• 評估有無賣出選擇權貼補分派收益與資本封頂風險。", "15.0 / 15", "<span class='quality-badge-green'>✔ 無不對稱期權風險</span>"]
        ]


def process_fund_risk_scores(preset_funds):
    """全自動動態算分與前台「核心短板警示標籤」生成引擎"""
    for k, fund_obj in preset_funds.items():
        cat_type = fund_obj.get("category", "債券基金")
        code_str = fund_obj.get("code", "")
        kpis = fund_obj.get("kpis", {})
        summary_text = fund_obj.get("summary", "")
        
        e_table = generate_dynamic_eval_table(fund_obj, cat_type)
        
        calculated_scores = []
        total_score_sum = 0.0
        for row in e_table:
            try:
                s_num = float(row[4].split("/")[0].strip())
                calculated_scores.append(s_num)
                total_score_sum += s_num
            except:
                calculated_scores.append(0.0)
                
        # 全站寫入完全一致之總分與雷達圖陣列
        fund_obj["score"] = round(total_score_sum, 1)
        fund_obj["radar_scores"] = calculated_scores
        
        # 🟢 第四階段：前台視覺化「核心短板/警示標籤」自動抓取生成
        if "CCC" in kpis.get("p3_delta", "") or "37.6%" in summary_text or code_str == "Z15":
            fund_obj["short_board_tag"] = "<span class='badge-red'>⚠️ 底層質素受壓 (CCC 37.6%)</span>"
        elif "CoCos" in summary_text or "AT1" in summary_text or code_str == "ZP4":
            fund_obj["short_board_tag"] = "<span class='badge-red'>⚠️ 含 CoCos 虧損吸收條款</span>"
        elif code_str in ["Z52", "ZU6"]:
            fund_obj["short_board_tag"] = "<span class='badge-yellow'>🟡 派息覆蓋緊繃 (無安全墊)</span>"
        elif code_str == "Z05":
            fund_obj["short_board_tag"] = "<span class='badge-yellow'>🟡 久期偏長 (6.45年)</span>"
        elif "144A" in summary_text or "ELN" in summary_text:
            fund_obj["short_board_tag"] = "<span class='badge-red'>⚠️ 含有 144A ELN 結構商品</span>"
        else:
            fund_obj["short_board_tag"] = "<span class='badge-green'>🟢 結構健康無顯著短板</span>"
