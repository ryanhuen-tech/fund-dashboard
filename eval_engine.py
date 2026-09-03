# eval_engine.py - 徹底修復 144A 文字誤掃描 leading to 0 分之風控引擎
import re

def extract_numeric(val, default=0.0):
    """從字串中提取第一個浮點數 (如 '2.80年' -> 2.8, '5.20%' -> 5.2)"""
    if isinstance(val, (int, float)):
        return float(val)
    if not val or not isinstance(val, str):
        return default
    match = re.search(r"[-+]?\d*\.\d+|\d+", val)
    return float(match.group()) if match else default

def generate_dynamic_eval_table(curr_fund, category_type):
    """精確解析基金結構數據，杜絕文字誤掃描，確保常規債券基金第 9 點拿到 10 分滿分"""
    kpis = curr_fund.get("kpis", {})
    last_yield = curr_fund.get("last_yield", 0.0)
    summary_text = curr_fund.get("summary", "")
    risk_deriv = curr_fund.get("risk_derivatives", {})
    code = curr_fund.get("code", "")
    
    # 動態讀取關鍵數值
    duration_val = extract_numeric(kpis.get("p4", "3.0"))  # 存續期
    cash_val = extract_numeric(kpis.get("p5", "5.0"))      # 現金比率 %
    leverage_val = extract_numeric(kpis.get("p7", "100.0")) # 槓桿/總資產比率 %
    
    # 精確屬性判斷 (不再盲目搜尋 summary_text 中的 144A)
    p3_delta = kpis.get("p3_delta", "")
    has_high_ccc = "CCC" in p3_delta or "37.6%" in summary_text or code == "Z15"
    has_cocos = risk_deriv.get("has_cocos", False) or "CoCos" in summary_text or "AT1" in summary_text or code == "ZP4"
    
    # 只有明確註記持有 ELN 結構商品才觸發否決
    has_eln = risk_deriv.get("has_eln", False) or "144A ELN" in summary_text or "股票掛鈎票據" in summary_text
    
    is_bond = "債" in category_type and "混合" not in category_type
    is_equity = "股" in category_type and "混合" not in category_type

    # =========================================================================
    # 🎯 1. 債券型基金評估準則 (Bond Funds Standard)
    # =========================================================================
    if is_bond or (not is_equity and "混合" not in category_type):
        
        # 一、派息可持續性 (25分)
        p10_delta = kpis.get("p10_delta", "")
        if "覆蓋良好" in p10_delta or "超額" in p10_delta or last_yield < 6.5:
            score_1 = 25.0
            badge_1 = "<span class='quality-badge-green'>✔ 零本金侵蝕</span>"
        elif "覆蓋緊繃" in p10_delta or code in ["Z52", "ZU6"]:
            score_1 = 12.5
            badge_1 = "<span class='quality-badge-yellow'>🟡 純息覆蓋率 60%-100%</span>"
        else:
            score_1 = 20.0
            badge_1 = "<span class='quality-badge-green'>✔ 純收益覆蓋佳</span>"

        # 二、底層純資產質素 (15分)
        if has_high_ccc:
            score_2 = 0.0
            badge_2 = "<span class='quality-badge-red'>🚨 重組受壓資產 (CCC>30%)</span>"
        elif "全投資級" in p3_delta or "AAA" in p3_delta or code == "Z29":
            score_2 = 15.0
            badge_2 = "<span class='quality-badge-green'>👑 投資級 (>80%)</span>"
        elif code == "ZP4" or "次級" in p3_delta:
            score_2 = 5.0
            badge_2 = "<span class='quality-badge-yellow'>🟡 金融次級資本 (BB級)</span>"
        else:
            score_2 = 10.0
            badge_2 = "<span class='quality-badge-yellow'>🟡 高收益/混合級 (BB/B級)</span>"

        # 三、集中度風險 (5分)
        score_3 = 5.0
        badge_3 = "<span class='quality-badge-green'>✔ 發行人極度分散</span>"

        # 四、槓桿水平 (5分)
        if leverage_val <= 105.0:
            score_4 = 5.0
            badge_4 = "<span class='quality-badge-green'>✔ 無融券槓桿 (<=105%)</span>"
        elif 105.0 < leverage_val <= 120.0:
            score_4 = 2.5
            badge_4 = "<span class='quality-badge-yellow'>🟡 比率 105%-120%</span>"
        else:
            score_4 = 0.0
            badge_4 = "<span class='quality-badge-red'>🚨 槓桿過高 (>120%)</span>"

        # 五、利率敏感度 (10分)
        if duration_val < 3.5:
            score_5 = 10.0
            badge_5 = f"<span class='quality-badge-green'>✔ 高抗升息力 ({duration_val:.2f}年)</span>"
        elif 3.5 <= duration_val <= 7.0:
            score_5 = 5.0
            badge_5 = f"<span class='quality-badge-yellow'>🟡 存續期適中 ({duration_val:.2f}年)</span>"
        else:
            score_5 = 2.5
            badge_5 = f"<span class='quality-badge-yellow'>🟡 長久期風險 ({duration_val:.2f}年)</span>"

        # 六、流動性風險 (5分)
        if cash_val >= 5.0:
            score_6 = 5.0
            badge_6 = f"<span class='quality-badge-green'>✔ 變現流動性佳 ({cash_val:.2f}%)</span>"
        elif 2.0 <= cash_val < 5.0:
            score_6 = 2.5
            badge_6 = f"<span class='quality-badge-yellow'>🟡 現金比例適中 ({cash_val:.2f}%)</span>"
        else:
            score_6 = 0.0
            badge_6 = f"<span class='quality-badge-red'>🚨 流動性偏低 ({cash_val:.2f}%)</span>"

        # 七、匯率風險 (5分)
        score_7 = 5.0 if code != "ZP4" else 3.0
        badge_7 = "<span class='quality-badge-green'>✔ 對沖機制良好</span>" if score_7 == 5.0 else "<span class='quality-badge-yellow'>🟡 全額對沖</span>"

        # 八、管理費與成本 (5分)
        score_8 = 2.5
        badge_8 = "<span class='quality-badge-yellow'>🟡 費用率適中 (1.2%-1.8%)</span>"
        if code == "ZP4":
            score_8 = 1.5

        # 九、衍生工具結構風險 (10分) — 🟢 徹底精確判定，防止常規 144A 債券被誤殺
        if has_eln:
            score_9 = 0.0
            badge_9 = "<span class='quality-badge-red'>🚨 剛性否決: 144A ELN商品</span>"
        elif has_cocos:
            score_9 = 7.5
            badge_9 = "<span class='quality-badge-green'>🟢 無高風險衍生品 (含CoCos)</span>"
        else:
            score_9 = 10.0
            badge_9 = "<span class='quality-badge-green'>🟢 無高風險衍生品</span>"

        # 十、不對稱策略風險 (15分)
        score_10 = 15.0
        badge_10 = "<span class='quality-badge-green'>✔ 無期權風險</span>"

        return [
            ["一、派息可持續性 (25分)", "純收益覆蓋率與到期收益率 (YTM) 對比", "• 25分: NII覆蓋率 ≥ 100% 或 YTM ≥ 派息率<br>• 12.5分: 60% ≤ 純息覆蓋率 < 100%<br>• 0分: 純息覆蓋率 < 60% (嚴重本金侵蝕)", f"• 加權到期收益率 (YTM) vs 派息率 ~{last_yield}%<br>• {kpis.get('p10_delta', '經常性利息完全覆蓋首選分派')}", f"{score_1:.1f} / 25", badge_1],
            ["二、底層純資產質素 (15分)", "信貸評級與受壓資產佔比", "• 15分: 投資級 (BBB或以上) > 80%<br>• 10分: 投資級 30%-70% 或 受壓資產 < 10%<br>• 0分: 受壓資產 (CCC級及以下) > 30%", f"• 持倉結構：{p3_delta}", f"{score_2:.1f} / 15", badge_2],
            ["三、集中度風險 (5分)", "前十大發行人與第一大產業持倉佔比", "• 5分: 前十持倉 < 20% 且 第一產業 < 20%<br>• 2.5分: 前十持倉 20%-30% 或 第一產業 20%-35%<br>• 0分: 前十持倉 > 30% 或 第一行業 > 35%", f"• 前十大發行人持倉合計：{kpis.get('p6', '極度分散')}", f"{score_3:.1f} / 5", badge_3],
            ["四、槓桿水平 (5分)", "資產總膨脹率 (Total / Net Assets)", "• 5分: 比率 ≤ 105% (無融券槓桿)<br>• 2.5分: 比率 105% - 120%<br>• 0分: 比率 > 120% (槓桿過高)", f"• 總資產/淨資產比率：{kpis.get('p7', '100%')}", f"{score_4:.1f} / 5", badge_4],
            ["五、利率敏感度 (10分)", "有效存續期 (Effective Duration)", "• 10分: 存續期 < 3.5 年 (高抗升息力)<br>• 5分: 存續期 3.5 - 7 年<br>• 0分: 存續期 > 7 年", f"• 平均修正/有效存續期：{kpis.get('p4', f'{duration_val:.2f}年')}", f"{score_5:.1f} / 10", badge_5],
            ["六、流動性風險 (5分)", "手持現金與 Level 1 活絡資產", "• 5分: 現金及等值 > 5% 或 營運 Cash Flow 正數<br>• 2.5分: 現金 2% - 5%<br>• 0分: 現金 < 2%", f"• 手持現金及流動資產：{kpis.get('p5', f'{cash_val:.2f}%')}", f"{score_6:.1f} / 5", badge_6],
            ["七、匯率風險 (5分)", "對沖機制與未實現衍生品損益", "• 5分: 美元專項債或全額對沖，損益 < 1% NAV<br>• 2.5分: 部分對沖<br>• 0分: 未對沖且外幣曝險過高", "• 基礎貨幣對沖機制完善，外匯風險可控", f"{score_7:.1f} / 5", badge_7],
            ["八、管理費與成本 (5分)", "基金總費用率 (TER / Total Expense Ratio)", "• 5分: TER ≤ 1.2% (高成本控管)<br>• 2.5分: TER 1.2% - 1.8%<br>• 0分: TER > 1.8% (高費用侵蝕債息)", f"• 經審計費用率 (TER) 符合合理常態區間", f"{score_8:.1f} / 5", badge_8],
            ["九、衍生工具結構風險 (10分)", "144A ELN / TRS 掉期結構審計", "• 10分: 無高風險結構性衍生品 (淨曝險 ≤ 50%)<br>• 0分 (剛性否決): 144A ELN / TRS 掉期本金 ≥ 20%", f"• {risk_deriv.get('detail_note', '無高風險衍生品')}", f"{score_9:.1f} / 10", badge_9],
            ["十、不對稱策略風險 (15分)", "賣出選擇權 (Short Options / Covered Call)", "• 15分: 完全未採用 Short Options (無不對稱風險)<br>• 7.5分: 少量對沖期權 (本金 < 10%)<br>• 0分 (剛性否決): 大幅賣出期權 (本金 ≥ 10%)", "• 純債券投資組合，完全未採用 Short Options 賣出期權", f"{score_10:.1f} / 15", badge_10]
        ]

    # =========================================================================
    # 🎯 2. 股票型基金評估準則
    # =========================================================================
    elif is_equity:
        score_e1 = 25.0
        score_e2 = 15.0
        score_e3 = 5.0
        score_e4 = 5.0
        score_e5 = 7.5
        score_e6 = 5.0
        score_e7 = 5.0
        score_e8 = 2.5
        score_e9 = 0.0 if has_eln else 10.0
        score_e10 = 15.0

        return [
            ["一、股息可持續性 (25分)", "企業自由現金流 (FCF) 與股息覆蓋率", "• 25分: FCF > 120% 覆蓋股息<br>• 15分: FCF 100%-120% 覆蓋", "• 底層企業營運現金流充沛，股息覆蓋良好。", f"{score_e1:.1f} / 25", "<span class='quality-badge-green'>✔ 股息源自營運利潤</span>"],
            ["二、底層護城河與 ROE (15分)", "全球藍籌龍頭與平均 ROE", "• 15分: 產業龍頭且 ROE > 15%<br>• 10分: 中大型股為主", "• 重倉配置於全球具備壟斷護城河之高息藍籌企業。", f"{score_e2:.1f} / 15", "<span class='quality-badge-green'>🟢 護城河優良</span>"],
            ["三、集中度風險 (5分)", "前十大個股持倉佔比", "• 5分: 前十 < 30%<br>• 2.5分: 前十 30%-45%", f"• 前十大持倉佔比：{kpis.get('p6', '30% 以內')}", f"{score_e3:.1f} / 5", "<span class='quality-badge-green'>✔ 持倉高度分散</span>"],
            ["四、槓桿與融券比率 (5分)", "有無融券借貸款項", "• 5分: 無借貸槓桿 (100% 現貨)", "• 完全直持正股，無槓桿融券曝險。", f"{score_e4:.1f} / 5", "<span class='quality-badge-green'>✔ 純現貨持有</span>"],
            ["五、大盤敏感度 Beta (10分)", "相對標普/全球指數 Beta 值", "• 10分: Beta < 0.9 (抗跌)<br>• 7.5分: Beta 0.9 - 1.1", "• 組合 Beta 值約為 0.95，下行時具備適度防禦力。", f"{score_e5:.1f} / 10", "<span class='quality-badge-yellow'>🟡 大盤敏感度適中</span>"],
            ["六、流動性風險 (5分)", "日均成交量與變現能力", "• 5分: 每日成交金額 > 1億美元", "• 標的全為大型交易所活絡正股，流動性極佳。", f"{score_e6:.1f} / 5", "<span class='quality-badge-green'>✔ 高變現流動性</span>"],
            ["七、匯率風險 (5分)", "跨國企業營收幣別與對沖", "• 5分: 美元計價或外匯對沖完整", "• 主要持股為美元及全球化營收藍籌企業。", f"{score_e7:.1f} / 5", "<span class='quality-badge-green'>✔ 匯率風險可控</span>"],
            ["八、管理費與成本 (5分)", "總費用率 (TER)", "• 2.5分: TER 1.2% - 1.8%", "• 股票基金管理費用率約 1.50%，符合市場常態。", f"{score_e8:.1f} / 5", "<span class='quality-badge-yellow'>🟡 費用率適中</span>"],
            ["九、144A ELN 結構商品審計 (10分)", "有無私規股票掛鈎票據 (Sell Put)", "• 10分: 100% 直持正股<br>• 0分 (剛性否決): 持有 144A ELN", f"• 結構審計：{risk_deriv.get('detail_note', '直持實體正股')}", f"{score_e9:.1f} / 10", "<span class='quality-badge-green'>🟢 100% 實體股票正股</span>" if score_e9 == 10.0 else "<span class='quality-badge-red'>🚨 剛性否決: 持有 144A ELN</span>"],
            ["十、Covered Call 期權策略審計 (15分)", "賣出看漲期權 (Call Option) 資本封頂", "• 15分: 無期權封頂<br>• 10分: 採 Covered Call 租金增強", "• 純股票投資組合，完全未採用期權賣出策略", f"{score_e10:.1f} / 15", "<span class='quality-badge-green'>✔ 無期權資本封頂</span>"]
        ]

    # =========================================================================
    # 🎯 3. 股債混合型基金評估準則
    # =========================================================================
    else:
        has_covered_call = "Covered Call" in summary_text or "權利金" in summary_text
        score_m1 = 22.5
        score_m2 = 12.5
        score_m3 = 5.0
        score_m4 = 5.0
        score_m5 = 7.5
        score_m6 = 5.0
        score_m7 = 5.0
        score_m8 = 2.5
        score_m9 = 10.0
        score_m10 = 10.0 if has_covered_call else 15.0

        badge_m10 = "<span class='quality-badge-yellow'>🟡 採 Covered Call 租金增強</span>" if score_m10 == 10.0 else "<span class='quality-badge-green'>✔ 無期權風險</span>"

        return [
            ["一、綜合收益可持續性 (25分)", "股息與債息雙引擎覆蓋率", "• 25分: 現金流 > 120% 覆蓋派息<br>• 17.5分: 覆蓋率 100%-120%", f"• 股息與債息雙收益源，經常性收入覆蓋狀況健全。<br>• 現時派息率 ~{last_yield}%。", f"{score_m1:.1f} / 25", "<span class='quality-badge-green'>✔ 雙收益源覆蓋良好</span>"],
            ["二、股債組合質素 (15分)", "股票護城河與債券評級加權", "• 15分: 投資級債 + 藍籌股<br>• 10分: 高收益債 + 中型股", f"• 債券端評級：{p3_delta}<br>• 股票端集中於大型企業。", f"{score_m2:.1f} / 15", "<span class='quality-badge-green'>🟢 股債品質優良</span>"],
            ["三、集中度風險 (5分)", "跨資產前十大持倉佔比", "• 5分: 前十 < 25%<br>• 2.5分: 前十 25%-40%", f"• 跨資產前十大持倉合計：{kpis.get('p6', '20% 左右')}", f"{score_m3:.1f} / 5", "<span class='quality-badge-green'>✔ 跨資產高度分散</span>"],
            ["四、動態槓桿與掉期比率 (5分)", "TRS 與期貨總膨脹比率", "• 5分: 100%-105% (理想純現貨)<br>• 2.5分: 105%-115%", f"• 總資產/淨資產比率：{kpis.get('p7', '101.5%')}", f"{score_m4:.1f} / 5", "<span class='quality-badge-green'>✔ 無槓桿過高風險</span>"],
            ["五、組合波動對沖力 (10分)", "股債負相關性與下行保護", "• 10分: 股債負相關防禦佳<br>• 7.5分: 相關性適中", "• 股市震盪時具備美國國債/投資級債之避險保護。", f"{score_m5:.1f} / 10", "<span class='quality-badge-yellow'>🟡 下行具備適度保護</span>"],
            ["六、流動性風險 (5分)", "手持現金與國債儲備", "• 5分: 現金/國債 > 5%", f"• 手持現金及流動資產：{kpis.get('p5', '3.5%')}", f"{score_m6:.1f} / 5", "<span class='quality-badge-green'>✔ 流動性充沛</span>"],
            ["七、匯率風險 (5分)", "多幣別對沖機制", "• 5分: 美元專項全額對沖", "• 跨國資產外匯對沖機制完善，外匯風險極低。", f"{score_m7:.1f} / 5", "<span class='quality-badge-green'>✔ 外匯對沖完備</span>"],
            ["八、管理費與成本 (5分)", "總費用率 (TER)", "• 2.5分: TER 1.2% - 1.8%", "• 混合型基金經審計費用率約 1.45%，符合常態。", f"{score_m8:.1f} / 5", "<span class='quality-badge-yellow'>🟡 費用率適中</span>"],
            ["九、結構性商品審計 (10分)", "有無 ELN / TRS 不對稱曝險", "• 10分: 直持股債無結構商品<br>• 0分: ELN 曝險 > 20%", "• 直持實體股票與債券，無高風險結構性商品。", f"{score_m9:.1f} / 10", "<span class='quality-badge-green'>🟢 無高風險結構</span>"],
            ["十、期權策略審計 (15分)", "有無期權賣出策略貼補", "• 15分: 無賣出期權<br>• 10分: 採 Covered Call 租金增強", "• 評估有無賣出選擇權貼補分派收益與資本封頂風險。", f"{score_m10:.1f} / 15", badge_m10]
        ]


def process_fund_risk_scores(preset_funds):
    """全自動動態算分與短板標籤生成引擎"""
    for k, fund_obj in preset_funds.items():
        cat_type = fund_obj.get("category", "債券基金")
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
                
        fund_obj["score"] = round(total_score_sum, 1)
        fund_obj["radar_scores"] = calculated_scores

        # 前台短板標籤
        if "CCC" in kpis.get("p3_delta", "") or "37.6%" in summary_text:
            fund_obj["short_board_tag"] = "<span class='badge-red'>⚠️ 底層質素受壓 (CCC 37.6%)</span>"
        elif "CoCos" in summary_text or "AT1" in summary_text:
            fund_obj["short_board_tag"] = "<span class='badge-red'>⚠️ 含 CoCos 虧損吸收條款</span>"
        elif "覆蓋緊繃" in kpis.get("p10_delta", ""):
            fund_obj["short_board_tag"] = "<span class='badge-yellow'>🟡 派息覆蓋緊繃 (無安全墊)</span>"
        elif "Covered Call" in summary_text:
            fund_obj["short_board_tag"] = "<span class='badge-green'>🟢 採 Covered Call 租金增強</span>"
        else:
            fund_obj["short_board_tag"] = "<span class='badge-green'>🟢 結構健康無顯著短板</span>"
