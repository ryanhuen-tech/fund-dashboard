# utils/nav_calculator.py - 徹底修復分母錯誤與公式倒置之 NAV-to-NAV 精算模組

def calculate_realtime_nav_to_nav(history_div_list):
    """
    根據官方 12 個月派息與 NAV 紀錄，進行 100% 精確的 NAV-to-NAV 總回報計算
    """
    if not history_div_list or len(history_div_list) < 12:
        return {"status": "error", "message": "歷史派息紀錄不足 12 個月"}

    try:
        # 取最近 12 個月紀錄 (從最新到最舊)
        recent_12 = history_div_list[:12]
        
        # 1. 抓取期初 (12個月前) 與最新 NAV
        # 歷史陣列格式：[除息日, 記錄日, 派息日, 每單位股息, 每單位資產淨值 NAV, 年化率]
        latest_nav = float(str(recent_12[0][4]).replace("$", "").replace("美元", "").strip())
        initial_nav = float(str(recent_12[-1][4]).replace("$", "").replace("美元", "").strip())
        
        # 2. 計算 12 個月累計現金派息總和
        total_payout = sum([float(str(row[3]).replace("$", "").strip()) for row in recent_12])
        
        # 3. 資本淨值 (NAV) 本金漲跌幅度 %
        nav_capital_change_pct = round(((latest_nav - initial_nav) / initial_nav) * 100, 2)
        
        # 4. 純現金總收益率 (無再投資) % = 派息率 + 淨值漲跌
        simple_cash_yield_pct = round((total_payout / initial_nav) * 100, 2)
        cash_payout_return_pct = round(simple_cash_yield_pct + nav_capital_change_pct, 2)
        
        # 5. 股息再投資 (Dividend Reinvestment) 單位數動態滾算
        current_units = 1000.0  # 假設期初持有 1,000 單位
        for row in reversed(recent_12):  # 從 12 個月前按時間順序滾算
            payout_per_share = float(str(row[3]).replace("$", "").strip())
            nav_at_ex = float(str(row[4]).replace("$", "").replace("美元", "").strip())
            
            # 每月領到的利息再買入新單位
            monthly_dividend_cash = current_units * payout_per_share
            units_bought = monthly_dividend_cash / nav_at_ex
            current_units += units_bought

        # 6. 期末股息再投資後的總資產價值與總回報率 %
        initial_investment_val = 1000.0 * initial_nav
        final_portfolio_val = current_units * latest_nav
        nav_to_nav_return_pct = round(((final_portfolio_val - initial_investment_val) / initial_investment_val) * 100, 2)

        return {
            "status": "success",
            "initial_nav": initial_nav,
            "latest_nav": latest_nav,
            "total_payout": round(total_payout, 4),
            "nav_capital_change_pct": nav_capital_change_pct,
            "simple_cash_yield_pct": simple_cash_yield_pct,
            "cash_payout_return_pct": cash_payout_return_pct,
            "nav_to_nav_return_pct": nav_to_nav_return_pct,
            "units_grown": round(current_units, 3),
            "units_added": round(current_units - 1000.0, 3)
        }

    except Exception as e:
        return {"status": "error", "message": f"計算異常: {str(e)}"}
