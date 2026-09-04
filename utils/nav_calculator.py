# utils/nav_calculator.py - 100% 精確 NAV-to-NAV 計算引擎

def calculate_realtime_nav_to_nav(history_div_list):
    if not history_div_list or len(history_div_list) < 12:
        return {"status": "error", "message": "歷史派息紀錄不足 12 個月"}

    try:
        recent_12 = history_div_list[:12]
        
        # 提取最新與期初 NAV
        latest_nav = float(str(recent_12[0][4]).replace("$", "").strip())
        initial_nav = float(str(recent_12[-1][4]).replace("$", "").strip())
        
        # 提取 12 個月派息總和
        total_payout = sum([float(str(row[3]).replace("$", "").strip()) for row in recent_12])
        
        # 資本漲跌與純現金收益
        nav_capital_change_pct = round(((latest_nav - initial_nav) / initial_nav) * 100, 2)
        simple_cash_yield_pct = round((total_payout / initial_nav) * 100, 2)
        cash_payout_return_pct = round(simple_cash_yield_pct + nav_capital_change_pct, 2)
        
        # 股息再投資動態滾算
        current_units = 1000.0
        for row in reversed(recent_12):
            payout_per_share = float(str(row[3]).replace("$", "").strip())
            nav_at_ex = float(str(row[4]).replace("$", "").strip())
            
            monthly_dividend_cash = current_units * payout_per_share
            units_bought = monthly_dividend_cash / nav_at_ex
            current_units += units_bought

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
