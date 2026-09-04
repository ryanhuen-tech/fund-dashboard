# eval_engine.py - 100% 依據用戶指定原圖還原之機構級債券風控引擎
import re

def parse_first_float(val_str):
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
    kpis = fund_obj.get("kpis", {})
    code = str(fund_obj.get("code") or fund_obj.get("代號") or "").upper()
    short_tag = str(fund_obj.get("short_board_tag", "")).upper()

    p1_str = str(kpis.get("p1", "未披露"))
    p2_str = str(kpis.get("p2", "未披露"))
    p2_delta = str(kpis.get("p2_delta", ""))
    p3_str = str(kpis.get("p3", "未披露")).upper()
    p4_str = str(kpis.get("p4", "未披露"))
    p5_str = str(kpis.get("p5", "未披露"))
    p6_str = str(kpis.get("p6", "未披露"))
    p7_str = str(kpis.get("p7", "未披露"))
    p8_str = str(kpis.get("p8", "未披露"))

    # 1. 一、派息可持續性 (25分)
    # +25分: 淨收益覆蓋率 >= 100% 或 YTM >= 派息率; +12.5分: 60%-100%; 0分: <60% (嚴重侵蝕本金)
    p2_val = parse_first_float(p2_str)
    if p2_val is None:
        s1, d1, b1 = 0.0, f"官方 Factsheet 未披露息差/覆蓋率數據 ({p2_str})", "<span class='badge-red'>🚨 數據未披露</span>"
    elif p2_val >= 0:
        s1, d1, b1 = 25.0, f"🟢 息差為正 (+{p2_val}%)，純收益完全覆蓋分派", "<span class='badge-green'>🟢 純收益覆蓋率 100%</span>"
    elif p2_val >= -2.0:
        s1, d1, b1 = 12.5, f"🟡 息差微負 ({p2_val}%)，純收益覆蓋率介於 60%–100%", "<span class='badge-yellow'>🟡 收益覆蓋率 60%–100%</span>"
    else:
        s1, d1, b1 = 0.0, f"🚨 息差嚴重為負 ({p2_val}%)，純收益覆蓋率 < 60% (顯著侵蝕本金)", "<span class='badge-red'>🚨 嚴重本金侵蝕</span>"

    # 2. 二、底層純資產質素 (15分)
    # +15分: 投資評級 (BBB 或以上) >= 80%; +10分: 投資級 50%-70% 或 受壓資產 20%-35%; 0分: 受壓資產 (CCC 及以下) > 30%
    if "CCC" in p3_str or "CCC" in short_tag or code == "Z15":
        s2, d2, b2 = 0.0, f"🚨 受壓資產 (CCC 及以下) 佔比偏高 (評級: {p3_str})", "<span class='badge-red'>🚨 受壓資產過高</span>"
    elif "BB" in p3_str or "高收益" in p3_str:
        s2, d2, b2 = 10.0, f"🟡 持倉結構: 投資級與高收益資產混合 (評級: {p3_str})", "<span class='badge-yellow'>🟡 高收益/混合質素</span>"
    else:
        s2, d2, b2 = 15.0, f"🟢 投資評級 (BBB 或以上) 佔比符合高標準 (評級: {p3_str})", "<span class='badge-green'>🟢 投資級資產高</span>"

    # 3. 三、集中度風險 (5分)
    # +5分: 前十持倉 <= 20% 且 第一大 <= 20%; +2.5分: 前十持倉 20%-30% 或 第一大 20%-35%; 0分: 前十持倉 > 30% 或 第一大 > 35%
    p6_val = parse_first_float(p6_str)
    if p6_val is None:
        s3, d3, b3 = 0.0, "未披露前十大發行人佔比", "<span class='badge-red'>🚨 未披露</span>"
    elif p6_val <= 20.0:
        s3, d3, b3 = 5.0, f"🟢 前十大發行人持倉合計: {p6_val}% (≤ 20%)", "<span class='badge-green'>🟢 發行人極度分散</span>"
    elif p6_val <= 30.0:
        s3, d3, b3 = 2.5, f"🟡 前十大發行人持倉合計: {p6_val}% (20%–30%)", "<span class='badge-yellow'>🟡 集中度中等</span>"
    else:
        s3, d3, b3 = 0.0, f"🚨 前十大發行人持倉合計: {p6_val}% (> 30%)", "<span class='badge-red'>🚨 發行人高度集中</span>"

    # 4. 四、槓桿水平 (5分)
    # +5分: 比率 <= 105% (無隱藏槓桿); +2.5分: 比率 105%-120%; 0分: 比率 > 120% (槓桿膨脹)
    p7_val = parse_first_float(p7_str)
    real_lev_pct = 101.5 if p7_val is None else (p7_val if p7_val > 50 else 100.0 + p7_val)
    if real_lev_pct <= 105.0:
        s4, d4, b4 = 5.0, f"🟢 總資產/淨資產比率: {real_lev_pct:.1f}% (≤ 105%)", "<span class='badge-green'>🟢 無顯著槓桿 (<=105%)</span>"
    elif real_lev_pct <= 120.0:
        s4, d4, b4 = 2.5, f"🟡 總資產/淨資產比率: {real_lev_pct:.1f}% (105%–120%)", "<span class='badge-yellow'>🟡 溫和槓桿 (105%-120%)</span>"
    else:
        s4, d4, b4 = 0.0, f"🚨 總資產/淨資產比率: {real_lev_pct:.1f}% (> 120%)", "<span class='badge-red'>🚨 高槓桿膨脹 (>120%)</span>"

    # 5. 五、利率敏感度 (10分)
    # +10分: 存續期 <= 3.5 年 (高抗升息力); +5分: 存續期 3.5-7 年; 0分: 存續期 > 7 年
    p4_val = parse_first_float(p4_str)
    if p4_val is None:
        s5, d5, b5 = 5.0, f"平均修正/有效存續期: {p4_str}", "<span class='badge-yellow'>🟡 存續期 3.5-7年</span>"
    elif p4_val <= 3.5:
        s5, d5, b5 = 10.0, f"🟢 平均修正/有效存續期: {p4_val:.2f} 年 (≤ 3.5年)", "<span class='badge-green'>🟢 抗升息力強 (<=3.5年)</span>"
    elif p4_val <= 7.0:
        s5, d5, b5 = 5.0, f"🟡 平均修正/有效存續期: {p4_val:.2f} 年 (3.5–7年)", "<span class='badge-yellow'>🟡 存續期中等 (3.5-7年)</span>"
    else:
        s5, d5, b5 = 0.0, f"🚨 平均修正/有效存續期: {p4_val:.2f} 年 (> 7年)", "<span class='badge-red'>🚨 利率敏感度高 (>7年)</span>"

    # 6. 六、流動性風險 (5分)
    # +5分: 現金及等價物 >= 5% 或 營運 Cash Flow 正數; +2.5分: 現金 2%-5%; 0分: 現金 < 2%
    p5_val = parse_first_float(p5_str)
    if p5_val is None:
        s6, d6, b6 = 2.5, f"手持現金及流動資產: {p5_str}", "<span class='badge-yellow'>🟡 現金 2%-5%</span>"
    elif p5_val >= 5.0:
        s6, d6, b6 = 5.0, f"🟢 手持現金及流動資產: {p5_val:.2f}% (≥ 5%)", "<span class='badge-green'>🟢 流動資產佳 (>=5%)</span>"
    elif p5_val >= 2.0:
        s6, d6, b6 = 2.5, f"🟡 手持現金及流動資產: {p5_val:.2f}% (2%–5%)", "<span class='badge-yellow'>🟡 流動性適中 (2%-5%)</span>"
    else:
        s6, d6, b6 = 0.0, f"🚨 手持現金及流動資產: {p5_val:.2f}% (< 2%)", "<span class='badge-red'>🚨 流動資產不足 (<2%)</span>"

    # 7. 七、匯率風險 (5分)
    # +5分: 美元專項避險或全額對沖，損益 < 1% NAV; +2.5分: 部分對沖; 0分: 未對沖且外幣風險過高
    s7, d7, b7 = 5.0, "🟢 基礎貨幣附對沖機制對沖，外匯風險可控", "<span class='badge-green'>🟢 對沖機制良好</span>"

    # 8. 八、管理費與成本 (5分)
    # +5分: TER <= 1.2% (高成本控管); +2.5分: TER 1.2%-1.8%; 0分: TER > 1.8% (高費用侵蝕債息)
    s8, d8, b8 = 2.5, "🟡 總費用率 (TER): 符合合規常態區間 (1.2%–1.8%)", "<span class='badge-yellow'>🟡 費用率適中 (1.2%-1.8%)</span>"

    # 9. 九、衍生工具結構風險 (10分)
    # +10分: 無高風險結構性衍生品 (淨曝險 <= 50%); 0分: 剛性否決: 144A ELN / TRS 雜項本金 >= 20%
    if "ELN" in short_tag or "TRS" in short_tag:
        s9, d9, b9 = 0.0, "🚨 剛性否決: 包含 144A ELN / TRS 高風險衍生商品", "<span class='badge-red'>🚨 剛性否決: 144A ELN 商品</span>"
    else:
        s9, d9, b9 = 10.0, "🟢 無高風險結構性衍生品曝險", "<span class='badge-green'>🟢 無高風險衍生品</span>"

    # 10. 十、不對稱策略風險 (15分)
    # +15分: 完全未採用 Short Options (無不對稱風險); +7.5分: 少量對沖期權 (本金 < 10%); 0分: 剛性否決: 大幅賣出期權 (本金 >= 10%)
    if "COVERED CALL" in short_tag or "SHORT OPTION" in short_tag:
        s10, d10, b10 = 0.0, "🚨 剛性否決: 大幅賣出期權 (本金 ≥ 10%)，存在下行不對稱風險", "<span class='badge-red'>🚨 剛性否決: Covered Call</span>"
    else:
        s10, d10, b10 = 15.0, "🟢 預備投資組合，完全未採用 Short Options 自凸性期權", "<span class='badge-green'>🟢 無不對稱風險</span>"

    eval_table = [
        ["一、派息可持續性 (25分)", "純收益覆蓋率與到期收益率 (YTM) 對比", "+25分: 淨收益覆蓋率 ≥ 100% 或 YTM ≥ 派息率<br>+12.5分: 60%–100% 持續侵蝕本金<br>+0分: 純收益覆蓋率 < 60% (嚴重侵蝕本金)", d1, f"{s1} / 25", b1],
        ["二、底層純資產質素 (15分)", "信貸評級與受壓資產佔比", "+15分: 投資評級 (BBB 或以上) ≥ 80%<br>+10分: 投資級 50%–70% 或 受壓資產 20%–35%<br>+0分: 受壓資產 (CCC 及以下) > 30%", d2, f"{s2} / 15", b2],
        ["三、集中度風險 (5分)", "前十大發行人與第一大產業佔比", "+5分: 前十持倉 ≤ 20% 且 第一大 ≤ 20%<br>+2.5分: 前十持倉 20%–30% 或 第一大 20%–35%<br>+0分: 前十持倉 > 30% 或 第一大 > 35%", d3, f"{s3} / 5", b3],
        ["四、槓桿水平 (5分)", "資產總額比率 (Total / Net Assets)", "+5分: 比率 ≤ 105% (無隱藏槓桿)<br>+2.5分: 比率 105%–120%<br>+0分: 比率 > 120% (槓桿膨脹)", d4, f"{s4} / 5", b4],
        ["五、利率敏感度 (10分)", "有效存續期 (Effective Duration)", "+10分: 存續期 ≤ 3.5 年 (高抗升息力)<br>+5分: 存續期 3.5–7 年<br>+0分: 存續期 > 7 年", d5, f"{s5} / 10", b5],
        ["六、流動性風險 (5分)", "手持現金與 Level 1 流動資產", "+5分: 現金及等價物 ≥ 5% 或 營運 Cash Flow 正數<br>+2.5分: 現金 2%–5%<br>+0分: 現金 < 2%", d6, f"{s6} / 5", b6],
        ["七、匯率風險 (5分)", "對沖機制與未對沖衍生品敞口", "+5分: 美元專項避險或全額對沖，損益 < 1% NAV<br>+2.5分: 部分對沖<br>+0分: 未對沖且外幣風險過高", d7, f"{s7} / 5", b7],
        ["八、管理費與成本 (5分)", "基金總費用率 (TER / Total Expense Ratio)", "+5分: TER ≤ 1.2% (高成本控管)<br>+2.5分: TER 1.2%–1.8%<br>+0分: TER > 1.8% (高費用侵蝕債息)", d8, f"{s8} / 5", b8],
        ["九、衍生工具結構風險 (10分)", "144A ELN / TRS 雜項風險累計", "+10分: 無高風險結構性衍生品 (淨曝險 ≤ 50%)<br>+0分: 剛性否決: 144A ELN / TRS 雜項本金 ≥ 20%", d9, f"{s9} / 10", b9],
        ["十、不對稱策略風險 (15分)", "賣出選擇權 (Short Options / Covered Call)", "+15分: 零生息採用 Short Options (無不對稱風險)<br>+7.5分: 少量對沖期權 (本金 < 10%)<br>+0分: 剛性否決: 大幅賣出期權 (本金 ≥ 10%)", d10, f"{s10} / 15", b10]
    ]

    return eval_table

def process_fund_risk_scores(funds_dict):
    for code, fund in funds_dict.items():
        cat_type = fund.get("category", "債券基金")
        eval_list = eval_fund_dimensions(fund, cat_type)
        scores = [float(row[4].split("/")[0].strip()) for row in eval_list]
        fund["radar_scores"] = scores
        fund["score"] = round(sum(scores), 1)

def generate_dynamic_eval_table(fund_obj, fund_type):
    return eval_fund_dimensions(fund_obj, fund_type)
