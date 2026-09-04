# utils/nav_calculator.py - 100% 動態 12 個月派息與 NAV 精算模組

def calculate_realtime_nav_to_nav(history_div_list):
    """
    依據過去 12 個月真實派息紀錄與 NAV 滾動計算實時總回報
    """
    if not history_div_list or len(history_div_list) < 12:
        return {"status": "error", "message": "歷史派息紀錄不足 12 個月"}

    try:
        # 嚴格取最新的 12 個月紀錄 (從最新到最舊)
        recent_12 = history_div_list[:12]
        
        # 提取期末 (最新) 與期初 (12個月前) NAV
        latest_nav = float(str(recent_12[0][4]).replace("$", "").replace("美元", "").strip())
        initial_nav = float(str(recent_12[-1][4]).replace("$", "").replace("美元", "").strip())
        
        # 12 個月累計現金派息總和
        total_payout = sum([float(str(row[3]).replace("$", "").strip()) for row in recent_12])
        
        # 1. 資本淨值 (NAV) 漲跌幅度 %
        nav_capital_change_pct = round(((latest_nav - initial_nav) / initial_nav) * 100, 2)
        
        # 2. 純領現金收益率 % & 淨收益率 %
        simple_cash_yield_pct = round((total_payout / initial_nav) * 100, 2)
        cash_payout_return_pct = round(simple_cash_yield_pct + nav_capital_change_pct, 2)
        
        # 3. 股息再投資 (Dividend Reinvestment) 月度滾算
        current_units = 1000.0  # 期初假設 1,000 單位
        for row in reversed(recent_12):  # 按時間由舊至新滾算
            payout_per_share = float(str(row[3]).replace("$", "").strip())
            nav_at_ex = float(str(row[4]).replace("$", "").replace("美元", "").strip())
            
            monthly_dividend_cash = current_units * payout_per_share
            units_bought = monthly_dividend_cash / nav_at_ex
            current_units += units_bought

        # 期末總資產價值與 NAV-to-NAV 回報率
        initial_investment_val = 1000.0 * initial_nav
        final_portfolio_val = current_units * latest_nav
        nav_to_nav_return_pct = round(((final_portfolio_val - initial_investment_val) / initial_investment_val) * 100, 2)

        return {
            "status": "success",
            "initial_nav": initial_nav,
            "latest_nav": latest_nav,
            "total_payout": round(total_payout, 4),
            "nav_capital_change_pct": nav_capital_change_pct,     # -2.23%
            "simple_cash_yield_pct": simple_cash_yield_pct,       # +7.81%
            "cash_payout_return_pct": cash_payout_return_pct,     # +5.58%
            "nav_to_nav_return_pct": nav_to_nav_return_pct,       # +5.78%
            "units_grown": round(current_units, 3),
            "units_added": round(current_units - 1000.0, 3)
        }

    except Exception as e:
        return {"status": "error", "message": f"計算過程異常: {str(e)}"}
