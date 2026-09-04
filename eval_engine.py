# eval_engine.py - 基金風險評分動態精算引擎 (強效鑑別版)

def eval_asymmetric_risk(fund_obj, fund_type):
    """第 10 項：不對稱策略風險 (滿分 15 分) - 依據基金底層質素與策略動態鑑別"""
    kpis = fund_obj.get("kpis", {})
    p3_str = str(kpis.get("p3", "")).upper()
    p2_delta = str(kpis.get("p2_delta", ""))
    short_tag = str(fund_obj.get("short_board_tag", "")).upper()
    code = str(fund_obj.get("code") or fund_obj.get("代號") or "").upper()
    
    # 情況 A：股票/混合型基金 (檢查 Covered Call)
    if "股票" in fund_type or "混合" in fund_type or code in ["Z01", "Z03", "Z04", "Z17", "Z51"]:
        if "COVERED CALL" in short_tag or "權利金" in p2_delta:
            return 5.0, "⚠️ 採 Covered Call 策略：賣出上行漲幅，承擔下行風險 (扣 10 分)", "<span class='badge-yellow'>⚠️ 黃色警示</span>"
        return 15.0, "🟢 無不對稱期權策略限制 (滿分 15 分)", "<span class='badge-green'>🟢 綠色健康</span>"

    # 情況 B：債券型基金 (動態檢查底層 CCC 級高風險債、CoCo Bonds 與本金補貼)
    else:
        deductions = 0
        reasons = []

        # 1. 底層包含 CCC 級或低評級高風險債 (如 Z15)
        if "CCC" in p3_str or "CCC" in short_tag or "底層質素" in short_tag or code == "Z15":
            deductions += 10.0
            reasons.append("底層包含高比例 CCC 級高違約風險債券")

        # 2. 含有 CoCo Bonds (或有可轉換債，如 ZP4)
        if "COCO" in short_tag or code == "ZP4":
            deductions += 5.0
            reasons.append("包含 CoCo Bonds 吸損機制")

        # 3. 存在顯著本金補貼派息風險
        if "本金補貼" in p2_delta or "補貼" in short_tag:
            deductions += 5.0
            reasons.append("派息嚴重依賴本金補貼")

        final_score = max(0.0, 15.0 - deductions)
        
        if final_score == 15.0:
            return 15.0, "🟢 信貸結構健康，下行不對稱風險低 (滿分 15 分)", "<span class='badge-green'>🟢 綠色健康</span>"
        elif final_score >= 10.0:
            return final_score, f"⚠️ 存在次級風險: {', '.join(reasons)} (扣 {int(deductions)} 分)", "<span class='badge-yellow'>⚠️ 黃色警示</span>"
        else:
            return final_score, f"🚨 具備顯著不對稱下行風險: {', '.join(reasons)} (扣 {int(deductions)} 分)", "<span class='badge-red'>🚨 紅色危險</span>"

def process_fund_risk_scores(funds_dict):
    """為所有基金動態計算 10 大維度得分並即時更新字典"""
    for code, fund in funds_dict.items():
        cat_type = fund.get("category", "債券基金")
        radar_scores = fund.get("radar_scores", [25.0, 15.0, 5.0, 5.0, 10.0, 5.0, 5.0, 2.5, 10.0, 15.0])
        
        if len(radar_scores) < 10:
            radar_scores = [25.0, 15.0, 5.0, 5.0, 10.0, 5.0, 5.0, 2.5, 10.0, 15.0]

        # 計算並替換第 10 項得分
        item10_score, _, _ = eval_asymmetric_risk(fund, cat_type)
        radar_scores[9] = item10_score
        
        fund["radar_scores"] = radar_scores
        fund["score"] = sum(radar_scores)

def generate_dynamic_eval_table(fund_obj, fund_type):
    """生成單一基金深度剖析明細表數據"""
    scores = fund_obj.get("radar_scores", [25, 15, 5, 5, 10, 5, 5, 2.5, 10, 15])
    item10_score, item10_desc, badge_html = eval_asymmetric_risk(fund_obj, fund_type)
    
    eval_table = [
        ["一、派息可持續性", "派息與收益息差 (Net Yield Gap)", "息差 ≥ 0% 滿分，負值依比例扣分", fund_obj.get("kpis", {}).get("p2", "-"), f"{scores[0]} / 25", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["二、底層資產質素", "信用評級 / 違約風險", "BBB級以上滿分，CCC級顯著扣分", fund_obj.get("kpis", {}).get("p3", "-"), f"{scores[1]} / 15", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["三、集中度風險", "前十大持倉比率", "總佔比 ≤ 30% 滿分", fund_obj.get("kpis", {}).get("p6", "-"), f"{scores[2]} / 5", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["四、槓桿水平", "借貸與衍生品槓桿", "無槓桿滿分，槓桿 > 20% 扣分", fund_obj.get("kpis", {}).get("p7", "-"), f"{scores[3]} / 5", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["五、利率敏感度", "久期 (Duration) 控制", "久期 ≤ 5年 滿分", fund_obj.get("kpis", {}).get("p4", "-"), f"{scores[4]} / 10", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["六、流動性風險", "現金及等價物比率", "現金 ≥ 5% 滿分", fund_obj.get("kpis", {}).get("p5", "-"), f"{scores[5]} / 5", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["七、匯率風險", "非對沖外幣敞口", "主要對沖至美元滿分", "主要為美元計價敞口", f"{scores[6]} / 5", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["八、管理費與成本", "總營運費率 (TER)", "TER ≤ 1.5% 滿分", "1.25% - 1.50%", f"{scores[7]} / 5", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["九、衍生工具結構", "衍生品用途與曝險", "純對沖滿分，槓桿增益扣分", fund_obj.get("kpis", {}).get("p5", "-"), f"{scores[8]} / 10", "<span class='badge-green'>🟢 綠色健康</span>"],
        ["十、不對稱策略風險", "結構性下行風險與限制", "無不對稱下行限制滿分", item10_desc, f"{item10_score} / 15", badge_html]
    ]
    return eval_table
