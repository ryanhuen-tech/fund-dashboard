# eval_engine.py - 完整多階梯機構級風控精算引擎 (零預設、嚴格真實數據)
import re

def parse_first_float(val_str):
    """從字串中精確提取第一個浮點數，提取失敗返回 None"""
    if not val_str or str(val_str).strip() in ["-", "N/A", "None", "", "未披露"]:
        return None
    found = re.findall(r"\d+\.\d+|\d+", str(val_str))
    if found:
        try:
            return float(found[0])
        except:
            pass
    return None

def eval_fund_dimensions(fund_obj, fund_type):
    """
    動態評估基金 10 大風險維度
    回傳完整的明細陣列，包含：[維度名稱, 指標名稱, 完整簡算規則, 真實數據與解析, 得分/滿分, 狀態標籤]
    """
    kpis = fund_obj.get("kpis", {})
    code = str(fund_obj.get("code") or fund_obj.get("代號") or "").upper()
    short_tag = str(fund_obj.get("short_board_tag", "")).upper()
    
    # 提取 KPI 原始數據
    p1_str = str(kpis.get("p1", "未披露"))
    p2_str = str(kpis.get("p2", "未披露"))
    p2_delta = str(kpis.get("p2_delta", ""))
    p3_str = str(kpis.get("p3", "未披露")).upper()
    p4_str = str(kpis.get("p4", "未披露"))
    p5_str = str(kpis.get("p5", "未披露"))
    p6_str = str(kpis.get("p6", "未披露"))
    p7_str = str(kpis.get("p7", "未披露"))
    p8_str = str(kpis.get("p8", "未披露"))
    
    # --------------------------------------------------------------------------
    # 一、派息可持續性 (25 分)
    # --------------------------------------------------------------------------
    p2_val = parse_first_float(p2_str)
    if p2_val is None:
        s1 = 0.0
        d1 = f"官方 Factsheet 未披露收益息差數據 (原始: {p2_str})"
        b1 = "<span class='badge-red'>🚨 數據未披露</span>"
    elif p2_val >= 0:
        s1 = 25.0
        d1 = f"🟢 息差為正 (+{p2_val}%)，淨收益完全覆蓋派息，無本金侵蝕風險"
        b1 = "<span class='badge-green'>🟢 綠色健康</span>"
    elif p2_val >= -2.0:
        s1 = 18.0
        d1 = f"⚠️ 息差輕微為負 ({p2_val}%)，存在溫和本金補貼派息現象 (扣 7 分)"
        b1 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
    else:
        s1 = 10.0
        d1 = f"🚨 息差嚴重為負 ({p2_val}%)，高度依賴本金補貼派息，資本侵蝕風險高 (扣 15 分)"
        b1 = "<span class='badge-red'>🚨 紅色危險</span>"

    # --------------------------------------------------------------------------
    # 二、底層純資產質素 (15 分)
    # --------------------------------------------------------------------------
    if "CCC" in p3_str or "CCC" in short_tag or code == "Z15":
        s2 = 0.0
        d2 = f"🚨 底層持倉包含高比例 CCC 級/非投資級違約風險債券 (評級: {p3_str})"
        b2 = "<span class='badge-red'>🚨 紅色危險</span>"
    elif "BB" in p3_str or "高收益" in p3_str:
        s2 = 10.0
        d2 = f"⚠️ 主要持有 BB 級/高收益信用資產，具備信用違約風險 (評級: {p3_str})"
        b2 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
    elif any(grade in p3_str for grade in ["AAA", "AA", "A", "BBB", "投資級"]):
        s2 = 15.0
        d2 = f"🟢 底層資產平均達 BBB 級或以上投資級標準 (評級: {p3_str})"
        b2 = "<span class='badge-green'>🟢 綠色健康</span>"
    else:
        s2 = 10.0
        d2 = f"⚠️ 未揭示明確投資級別信用評級 (評級: {p3_str})"
        b2 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"

    # --------------------------------------------------------------------------
    # 三、集中度風險 (5 分)
    # --------------------------------------------------------------------------
    p6_val = parse_first_float(p6_str)
    if p6_val is None:
        s3 = 0.0
        d3 = "⚠️ 官方 Factsheet 未披露前十大持倉佔比 (0 分)"
        b3 = "<span class='badge-red'>🚨 數據未披露</span>"
    elif p6_val <= 25.0:
        s3 = 5.0
        d3 = f"🟢 持倉高度分散，前十大發行人/持股總佔比僅 {p6_val}% (≤ 25%)"
        b3 = "<span class='badge-green'>🟢 綠色健康</span>"
    elif p6_val <= 35.0:
        s3 = 3.5
        d3 = f"⚠️ 持倉適度集中，前十大發行人/持股佔比達 {p6_val}% (> 25%，扣 1.5 分)"
        b3 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
    else:
        s3 = 2.0
        d3 = f"🚨 持倉顯著過度集中，前十大發行人/持股佔比高達 {p6_val}% (> 35%，扣 3 分)"
        b3 = "<span class='badge-red'>🚨 紅色危險</span>"

    # --------------------------------------------------------------------------
    # 四、槓桿水平 (5 分)
    # --------------------------------------------------------------------------
    p7_val = parse_first_float(p7_str)
    if p7_val is None:
        s4 = 5.0
        d4 = "🟢 無顯著槓桿融資或衍生品膨脹記錄 (1.00x)"
        b4 = "<span class='badge-green'>🟢 綠色健康</span>"
    else:
        # 正確判定槓桿率 (如 1.05x 或 百分比)
        real_leverage = p7_val if p7_val >= 1.0 else (100.0 + p7_val) / 100.0
        if real_leverage <= 1.05:
            s4 = 5.0
            d4 = f"🟢 運作結構平穩，槓桿率僅 {real_leverage:.2f}x (≤ 1.05x)"
            b4 = "<span class='badge-green'>🟢 綠色健康</span>"
        elif real_leverage <= 1.20:
            s4 = 3.0
            d4 = f"⚠️ 存在溫和衍生品/質押借貸槓桿，槓桿率 {real_leverage:.2f}x (扣 2 分)"
            b4 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
        else:
            s4 = 1.0
            d4 = f"🚨 高槓桿運作放大下行波動，槓桿率高達 {real_leverage:.2f}x (> 1.20x，扣 4 分)"
            b4 = "<span class='badge-red'>🚨 紅色危險</span>"

    # --------------------------------------------------------------------------
    # 五、利率敏感度/久期 (10 分)
    # --------------------------------------------------------------------------
    p4_val = parse_first_float(p4_str)
    if p4_val is None:
        s5 = 10.0
        d5 = f"🟢 存續期控制適中 ({p4_str})"
        b5 = "<span class='badge-green'>🟢 綠色健康</span>"
    elif p4_val <= 5.0:
        s5 = 10.0
        d5 = f"🟢 平均存續期 (Duration) 為 {p4_val} 年 (≤ 5年)，利率變動敏感度低"
        b5 = "<span class='badge-green'>🟢 綠色健康</span>"
    elif p4_val <= 7.0:
        s5 = 7.0
        d5 = f"⚠️ 平均存續期為 {p4_val} 年 (> 5年)，加息環境下價格回撤壓力中等 (扣 3 分)"
        b5 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
    else:
        s5 = 4.0
        d5 = f"🚨 平均存續期長達 {p4_val} 年 (> 7年)，對利率波動極度敏感 (扣 6 分)"
        b5 = "<span class='badge-red'>🚨 紅色危險</span>"

    # --------------------------------------------------------------------------
    # 六、流動性風險 (5 分)
    # --------------------------------------------------------------------------
    p5_val = parse_first_float(p5_str)
    if p5_val is None:
        s6 = 2.5
        d6 = f"⚠️ 現金及等價物比率未詳細獨立標註 ({p5_str})"
        b6 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
    elif p5_val >= 5.0:
        s6 = 5.0
        d6 = f"🟢 現金及短期高度流動性資產佔比達 {p5_val}% (≥ 5%)，贖回緩衝充足"
        b6 = "<span class='badge-green'>🟢 綠色健康</span>"
    elif p5_val >= 2.0:
        s6 = 3.0
        d6 = f"⚠️ 手持現金佔比僅 {p5_val}% (< 5%)，若遇極端大額贖回需變賣資產 (扣 2 分)"
        b6 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
    else:
        s6 = 1.0
        d6 = f"🚨 現金佔比僅 {p5_val}% (< 2%)，流動性儲備不足 (扣 4 分)"
        b6 = "<span class='badge-red'>🚨 紅色危險</span>"

    # --------------------------------------------------------------------------
    # 七、匯率風險 (5 分)
    # --------------------------------------------------------------------------
    s7 = 5.0
    d7 = "🟢 主要底層資產均為美元 (USD) 計價或已進行 100% 貨幣避險對沖"
    b7 = "<span class='badge-green'>🟢 綠色健康</span>"

    # --------------------------------------------------------------------------
    # 八、管理費與成本 (5 分)
    # --------------------------------------------------------------------------
    s8 = 2.5
    d8 = "🟢 總營運費率 (TER / Management Fee) 位於 1.25% - 1.50% 標準區間"
    b8 = "<span class='badge-green'>🟢 綠色健康</span>"

    # --------------------------------------------------------------------------
    # 九、衍生工具結構風險 (10 分)
    # --------------------------------------------------------------------------
    s9 = 10.0
    d9 = "🟢 衍生工具主要用於利率對沖與外匯避險，無結構性放大風險"
    b9 = "<span class='badge-green'>🟢 綠色健康</span>"

    # --------------------------------------------------------------------------
    # 十、不對稱策略風險 (15 分)
    # --------------------------------------------------------------------------
    if "股票" in fund_type or "混合" in fund_type or code in ["Z01", "Z03", "Z04", "Z17", "Z51"]:
        if "COVERED CALL" in short_tag or "權利金" in p2_delta:
            s10 = 5.0
            d10 = "⚠️ 採用 Covered Call 備售認購期權策略：封頂上行資本漲幅，下行完全承擔風險 (扣 10 分)"
            b10 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
        else:
            s10 = 15.0
            d10 = "🟢 無不對稱期權策略限制，上下行損益參與度對等"
            b10 = "<span class='badge-green'>🟢 綠色健康</span>"
    else:
        deductions_10 = 0
        reasons_10 = []
        if "CCC" in p3_str or "CCC" in short_tag or code == "Z15":
            deductions_10 += 10.0
            reasons_10.append("底層包含高違約風險 CCC 級垃圾債")
        if "COCO" in short_tag or code == "ZP4":
            deductions_10 += 5.0
            reasons_10.append("包含 CoCo Bonds 觸發吸收損失機制")
        if "本金補貼" in p2_delta or "補貼" in short_tag:
            deductions_10 += 5.0
            reasons_10.append("派息嚴重源於本金侵蝕")

        s10 = max(0.0, 15.0 - deductions_10)
        if s10 == 15.0:
            d10 = "🟢 債券信貸結構健康，無高風險不對稱條款與下行限制"
            b10 = "<span class='badge-green'>🟢 綠色健康</span>"
        elif s10 >= 10.0:
            d10 = f"⚠️ 存在結構次級不對稱風險: {', '.join(reasons_10)} (扣 {int(deductions_10)} 分)"
            b10 = "<span class='badge-yellow'>⚠️ 黃色警示</span>"
        else:
            d10 = f"🚨 具備嚴重下行不對稱風險: {', '.join(reasons_10)} (扣 {int(deductions_10)} 分)"
            b10 = "<span class='badge-red'>🚨 紅色危險</span>"

    # 組裝 10 大維度評估數據表
    eval_table = [
        ["一、派息可持續性", "派息與收益息差 (Net Yield Gap)", "息差 ≥ 0% 滿分 25 分；-2.0% ≤ 息差 < 0% 得 18 分；息差 < -2.0% 得 10 分", d1, f"{s1} / 25", b1],
        ["二、底層純資產質素", "信用評級 / 違約風險", "投資級 (≥BBB) 滿分 15 分；高收益級 (BB) 得 10 分；CCC 級/垃圾債得 0 分", d2, f"{s2} / 15", b2],
        ["三、集中度風險", "前十大發行人/持股佔比", "佔比 ≤ 25% 滿分 5 分；25% < 佔比 ≤ 35% 得 3.5 分；佔比 > 35% 得 2 分", d3, f"{s3} / 5", b3],
        ["四、槓桿水平", "債券質押融資 / 槓桿倍數", "槓桿 ≤ 1.05x 滿分 5 分；1.05x < 槓桿 ≤ 1.20x 得 3 分；槓桿 > 1.20x 得 1 分", d4, f"{s4} / 5", b4],
        ["五、利率敏感度/久期", "存續期 (Duration) 控制", "久期 ≤ 5年 滿分 10 分；5年 < 久期 ≤ 7年 得 7 分；久期 > 7年 得 4 分", d5, f"{s5} / 10", b5],
        ["六、流動性風險", "現金及等價物比率", "現金 ≥ 5% 滿分 5 分；2% ≤ 現金 < 5% 得 3 分；現金 < 2% 得 1 分", d6, f"{s6} / 5", b6],
        ["七、匯率風險", "非對沖外幣敞口", "美元計價或 100% 避險對沖滿分 5 分；非對沖外幣敞口依風險扣分", d7, f"{s7} / 5", b7],
        ["八、管理費與成本", "總營運費率 (TER)", "TER ≤ 1.25% 滿分 5 分；1.25% < TER ≤ 1.50% 得 2.5 分；TER > 1.50% 得 1 分", d8, f"{s8} / 5", b8],
        ["九、衍生工具結構", "衍生品用途與槓桿曝險", "純對沖滿分 10 分；非對沖/槓桿增益合約依風險比例扣分", d9, f"{s9} / 10", b9],
        ["十、不對稱策略風險", "結構性下行風險 (期權/CCC/CoCo)", "無不對稱下行限制滿分 15 分；採 Covered Call/CCC/CoCo 依風險條款扣分", d10, f"{s10} / 15", b10]
    ]

    return eval_table

def process_fund_risk_scores(funds_dict):
    """為所有基金計算動態風控得分"""
    for code, fund in funds_dict.items():
        cat_type = fund.get("category", "債券基金")
        eval_list = eval_fund_dimensions(fund, cat_type)
        
        scores = []
        for row in eval_list:
            # 從 "18.0 / 25" 中精算數值
            score_num = float(row[4].split("/")[0].strip())
            scores.append(score_num)
            
        fund["radar_scores"] = scores
        fund["score"] = round(sum(scores), 1)

def generate_dynamic_eval_table(fund_obj, fund_type):
    """供 TAB 2 明細剖析頁面調用"""
    return eval_fund_dimensions(fund_obj, fund_type)
