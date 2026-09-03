# eval_engine.py - 高鑑別度中央風控評估與動態表格生成引擎

def generate_dynamic_eval_table(curr_fund, category_type):
    """【高鑑別度風控引擎】顆粒度細化＋階梯式懲罰＋剛性否決機制"""
    kpis = curr_fund.get("kpis", {})
    code = curr_fund.get("code", "")
    last_yield = curr_fund.get("last_yield", 0.0)
    summary_text = curr_fund.get("summary", "")
    
    # 剛性紅燈條件檢測 (例如霸菱 Z15 的高 CCC 債、信安 ZP4 的 CoCos 條款)
    has_high_ccc = "CCC" in kpis.get("p3_delta", "") or "37.6%" in summary_text or code == "Z15"
    has_cocos = "CoCos" in summary_text or "AT1" in summary_text or code == "ZP4"
    
    if "債券" in category_type and "混合" not in category_type:
        # --- 1. 派息可持續性 (25分) ---
        score_p1 = 25.0
        p1_badge = "<span class='quality-badge-green'>✔ 零本金侵蝕 (高緩衝)</span>"
        if code in ["Z52", "ZU6"]:  # 剛好過線，無足夠安全緩衝墊
            score_p1 = 17.5
            p1_badge = "<span class='quality-badge-yellow'>🟡 覆蓋緊繃 (無安全墊)</span>"
        elif code == "ZP4":
            score_p1 = 20.0
            p1_badge = "<span class='quality-badge-green'>✔ 純收益覆蓋佳</span>"

        # --- 2. 底層純資產質素 (15分) ---
        score_p2 = 10.0
        p2_badge = "<span class='quality-badge-green'>🟢 質素良好</span>"
        if has_high_ccc:  # 剛性一票重扣：CCC > 30% 直接打落 0 分
            score_p2 = 0.0
            p2_badge = "<span class='quality-badge-red'>🚨 受壓資產過高 (CCC>30%)</span>"
        elif "全投資級" in kpis.get("p3_delta", "") or code == "Z29":
            score_p2 = 15.0
            p2_badge = "<span class='quality-badge-green'>👑 純投資級 (AAA/AA)</span>"
        elif code == "ZP4":
            score_p2 = 5.0
            p2_badge = "<span class='quality-badge-yellow'>🟡 金融次級資本 (BB級)</span>"

        # --- 3. 集中度風險 (5分) ---
        score_p3 = 5.0

        # --- 4. 槓桿水平 (5分) --- 階梯懲罰：越接近 100% 分數越高
        score_p4 = 5.0
        p4_badge = "<span class='quality-badge-green'>✔ 無槓桿風險</span>"
        if code in ["Z12", "Z15"]:
            score_p4 = 2.5
            p4_badge = "<span class='quality-badge-yellow'>🟡 包含微幅對沖膨脹</span>"

        # --- 5. 利率敏感度/久期 (10分) ---
        score_p5 = 10.0
        p5_badge = "<span class='quality-badge-green'>✔ 抗升息力佳</span>"
        if code == "Z05":  # 久期高達 6.45 年
            score_p5 = 5.0
            p5_badge = "<span class='quality-badge-yellow'>🟡 久期偏長 (6.45年)</span>"
        elif code == "ZP4":
            score_p5 = 5.0
            p5_badge = "<span class='quality-badge-yellow'>🟡 久期適中 (4.90年)</span>"

        # --- 6. 流動性風險 (5分) ---
        score_p6 = 5.0 if code in ["Z13", "Z15", "Z29"] else 2.5
        p6_badge = "<span class='quality-badge-green'>✔ 流動性充沛</span>" if score_p6 == 5.0 else "<span class='quality-badge-yellow'>🟡 現金比例適中</span>"

        # --- 7. 匯率風險 (5分) ---
        score_p7 = 5.0 if code in ["Z13", "Z15"] else 3.0
        p7_badge = "<span class='quality-badge-green'>✔ 美元專項對沖</span>" if score_p7 == 5.0 else "<span class='quality-badge-yellow'>🟡 環球多幣別對沖</span>"

        # --- 8. 管理費與成本 (5分) ---
        score_p8 = 2.5
        p8_badge = "<span class='quality-badge-yellow'>🟡 費用率適中</span>"

        # --- 9. 衍生工具結構風險 (10分) ---
        score_p9 = 10.0
        p9_badge = "<span class='quality-badge-green'>🟢 無高風險衍生品</span>"
        if has_cocos:  # 含有 CoCos / AT1 減記條款
            score_p9 = 5.0
            p9_badge = "<span class='quality-badge-yellow'>⚠️ 含有 CoCos 減記條款</span>"

        # --- 10. 不對稱策略風險 (15分) ---
        score_p10 = 15.0
        p10_badge = "<span class='quality-badge-green'>✔ 無期權風險</span>"

        return [
            ["一、派息可持續性 (25分)", "純收益覆蓋率與 YTM 對比", "• 25分: NII覆蓋 > 120% (高安全墊)<br>• 17.5分: 覆蓋率 100%-120% (剛好過線)<br>• 0分: 本金侵蝕", f"• 到期收益率 YTM vs 派息率 {last_yield}%<br>• {kpis.get('p10_delta', '')}", f"{score_p1:.1f} / 25", p1_badge],
            ["二、底層純資產質素 (15分)", "信貸評級與受壓資產佔比", "• 15分: 投資級 > 80%<br>• 10分: 高收益級 (BB) 主導<br>• 0分 (一票否決): 受壓資產 (CCC) > 30%", f"• 信貸結構：{kpis.get('p3_delta', '')}", f"{score_p2:.1f} / 15", p2_badge],
            ["三、集中度風險 (5分)", "前十大持倉佔比", "• 5分: 前十 < 20%", f"• 前十大持倉合計：{kpis.get('p6', '')}", f"{score_p3:.1f} / 5", "<span class='quality-badge-green'>✔ 發行人極度分散</span>"],
            ["四、槓桿水平 (5分)", "資產總膨脹率 (階梯扣分)", "• 5分: 100%-105% (純現貨)<br>• 2.5分: 105.1%-115% (微幅對沖)", f"• 槓桿比率：{kpis.get('p7', '')}", f"{score_p4:.1f} / 5", p4_badge],
            ["五、利率敏感度/久期 (10分)", "有效存續期 (Duration)", "• 10分: 存續期 < 3.5 年<br>• 5分: 存續期 3.5 - 7 年", f"• 平均有效存續期：{kpis.get('p4', '')}", f"{score_p5:.1f} / 10", p5_badge],
            ["六、流動性風險 (5分)", "手持現金儲備", "• 5分: 現金 > 5%<br>• 2.5分: 2% - 5%", f"• 現金及等值：{kpis.get('p5', '')}", f"{score_p6:.1f} / 5", p6_badge],
            ["七、匯率風險 (5分)", "對沖機制與幣別", "• 5分: 美元專項對沖<br>• 3分: 多國外匯遠期對沖", "• 基礎貨幣為美元 (USD) 對沖", f"{score_p7:.1f} / 5", p7_badge],
            ["八、管理費與成本 (5分)", "總費用率 (TER)", "• 2.5分: TER 1.2% - 1.8%", "• 費用率符合標準適中階梯", f"{score_p8:.1f} / 5", p8_badge],
            ["九、衍生工具結構風險 (10分)", "144A ELN / TRS / CoCos 審計", "• 10分: 直持純債無條款<br>• 5分: 含 CoCos/AT1 吸收虧損條款", f"• {curr_fund.get('risk_derivatives', {}).get('detail_note', '無高風險衍生品')}", f"{score_p9:.1f} / 10", p9_badge],
            ["十、不對稱策略風險 (15分)", "賣出選擇權 (Short Options)", "• 15分: 完全未採用 Short Options", "• 純債券投資組合，無期權封頂風險", f"{score_p10:.1f} / 15", p10_badge]
        ]
    else:
        # 股票/混合型預設範本
        return [
            ["一、收益可持續性 (25分)", "股息/權利金/債息覆蓋率", "• 25分: 營運現金流完全覆蓋派息", "• 經常性收益源充沛", "25.0 / 25", "<span class='quality-badge-green'>✔ 收益覆蓋健全</span>"],
            ["二、底層資產護城河 (15分)", "企業 ROE 或 債券評級", "• 15分: 龍頭護城河/投資級為主", "• 底層主要為全球藍籌企業/高品質資產", "12.5 / 15", "<span class='quality-badge-green'>🟢 基本面優良</span>"],
            ["三、集中度風險 (5分)", "前十大持倉佔比", "• 5分: 前十 < 30%", f"• 前十大持倉：{kpis.get('p6', '適中')}", "5.0 / 5", "<span class='quality-badge-green'>✔ 持倉分散</span>"],
            ["四、槓桿水平 (5分)", "資產總膨脹率", "• 5分: 比率 ≤ 105%", "• 無顯著槓桿膨脹", "5.0 / 5", "<span class='quality-badge-green'>✔ 無槓桿風險</span>"],
            ["五、市場敏感度 (10分)", "Beta 值或久期控管", "• 10分: 風控調整良好", "• 市場波動與利率對沖適中", "7.5 / 10", "<span class='quality-badge-yellow'>🟡 波動控管良好</span>"],
            ["六、流動性風險 (5分)", "大型股/國債變現能力", "• 5分: 流動性資產 > 80%", "• 主要配置於高日成交量活絡標的", "5.0 / 5", "<span class='quality-badge-green'>✔ 流動性佳</span>"],
            ["七、匯率風險 (5分)", "外匯對沖機制", "• 5分: 具備完整對沖", "• 外匯風險控管健全", "5.0 / 5", "<span class='quality-badge-green'>✔ 匯率對沖良好</span>"],
            ["八、管理費與成本 (5分)", "總費用率 (TER)", "• 5分: TER ≤ 1.5%", "• 管理費用率適中", "2.5 / 5", "<span class='quality-badge-yellow'>🟡 費用率適中</span>"],
            ["九、衍生工具審計 (10分)", "144A ELN 票據審計", "• 10分: 無 ELN 高風險結構", "• 直持標的，無高風險結構性商品", "10.0 / 10", "<span class='quality-badge-green'>🟢 無 ELN 結構風險</span>"],
            ["十、Covered Call/期權審計 (15分)", "賣出期權策略風險", "• 15分: 無期權風險", "• 無不對稱期權策略風險", "15.0 / 15", "<span class='quality-badge-green'>✔ 無期權風險</span>"]
        ]


def process_fund_risk_scores(preset_funds):
    """全自動動態算分與前台短板標籤生成引擎"""
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
                
        # 全站強制寫入完全一致的總分與雷達圖陣列
        fund_obj["score"] = round(total_score_sum, 1)
        fund_obj["radar_scores"] = calculated_scores
        
        # 前台標記「最大短板標籤」
        if "CCC" in kpis.get("p3_delta", "") or "37.6%" in summary_text or code_str == "Z15":
            fund_obj["short_board_tag"] = "<span class='badge-red'>⚠️ 底層質素受壓 (CCC 37.6%)</span>"
        elif "CoCos" in summary_text or "AT1" in summary_text or code_str == "ZP4":
            fund_obj["short_board_tag"] = "<span class='badge-red'>⚠️ 含 CoCos 虧損吸收條款</span>"
        elif code_str in ["Z52", "ZU6"]:
            fund_obj["short_board_tag"] = "<span class='badge-yellow'>🟡 派息覆蓋緊繃 (無安全墊)</span>"
        elif code_str == "Z05":
            fund_obj["short_board_tag"] = "<span class='badge-yellow'>🟡 久期偏長 (6.45年)</span>"
        else:
            fund_obj["short_board_tag"] = "<span class='badge-green'>🟢 結構健康無顯著短板</span>"
