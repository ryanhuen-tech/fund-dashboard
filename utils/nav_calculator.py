# utils/nav_calculator.py
# ==============================================================================
# 全系統通用：NAV-to-NAV 動態含息總回報率精算模組
# 適用於所有具備歷史派息紀錄 (history_div) 的股票、債券與混合型基金
# ==============================================================================


def calculate_realtime_nav_to_nav(history_div_data, target_months=12):
    """通用 NAV-to-NAV 股息再投資算式。

    參數:
        history_div_data (list): 基金的歷史派息紀錄列表，格式為：
            [除息日, 紀錄日, 派息日, 每單位股息, 除息日每單位NAV, 年化派息率]
        target_months (int): 要計算的月數，預設為 12 個月 (近 1 年)

    傳回:
        dict: 包含各種角度計算結果的完整數據字典
    """
    # 數據安全性檢核
    if not history_div_data or len(history_div_data) == 0:
        return {
            "status": "error",
            "message": "無歷史派息紀錄數據",
            "nav_to_nav_return_pct": 0.0,
            "cash_payout_return_pct": 0.0,
            "simple_cash_yield_pct": 0.0,
            "nav_capital_change_pct": 0.0,
        }

    # 確保資料足夠，若少於 target_months，則取全部現有月份
    actual_months = min(len(history_div_data), target_months)
    recent_data = history_div_data[:actual_months]

    # 將數據時間轉換為「由舊到新」（即時間順序 1 -> 12）
    chronological_data = list(reversed(recent_data))

    try:
        # 設定初始基準：假設 1 年前第一個除息日購入 1,000 單位
        initial_units = 1000.0
        initial_nav = float(chronological_data[0][4])  # 1年前除息日 NAV
        initial_investment = initial_units * initial_nav

        current_units = initial_units
        total_cash_dividends = 0.0  # 紀錄若純領現金的累積利息

        # 逐月進行「股息再投資」單位數滾存
        for month_row in chronological_data:
            dividend_per_unit = float(month_row[3])
            ex_nav = float(month_row[4])

            # 當月收到的派息總額
            monthly_payout = current_units * dividend_per_unit
            total_cash_dividends += monthly_payout

            # 用當天除息日 NAV 再投資買入新單位
            reinvested_units = monthly_payout / ex_nav
            current_units += reinvested_units

        # 最新一個月 (當前) 的除息日 NAV
        latest_nav = float(history_div_data[0][4])

        # 1. 股息再投資 (NAV-to-NAV) 總價值與總回報率
        final_reinvested_value = current_units * latest_nav
        nav_to_nav_return_pct = (
            (final_reinvested_value - initial_investment) / initial_investment
        ) * 100

        # 2. 純領現金 (不滾存) 總價值與總回報率
        final_cash_value = (initial_units * latest_nav) + total_cash_dividends
        cash_payout_return_pct = (
            (final_cash_value - initial_investment) / initial_investment
        ) * 100

        # 3. 資本淨值 (NAV) 純漲跌幅
        nav_capital_change_pct = (
            (latest_nav - initial_nav) / initial_nav
        ) * 100

        # 4. 簡單現金利息收益率
        simple_cash_yield_pct = (
            total_cash_dividends / initial_investment
        ) * 100

        return {
            "status": "success",
            "months_calculated": actual_months,
            "initial_nav": initial_nav,
            "latest_nav": latest_nav,
            "initial_investment": round(initial_investment, 2),
            "final_reinvested_value": round(final_reinvested_value, 2),
            "final_cash_value": round(final_cash_value, 2),
            "units_grown": round(current_units, 4),
            "units_added": round(current_units - initial_units, 4),
            "nav_to_nav_return_pct": round(nav_to_nav_return_pct, 2),
            "cash_payout_return_pct": round(cash_payout_return_pct, 2),
            "nav_capital_change_pct": round(nav_capital_change_pct, 2),
            "simple_cash_yield_pct": round(simple_cash_yield_pct, 2),
        }

    except (ValueError, ZeroDivisionError, IndexError) as e:
        return {
            "status": "error",
            "message": f"數據格式轉換錯誤: {str(e)}",
            "nav_to_nav_return_pct": 0.0,
            "cash_payout_return_pct": 0.0,
            "simple_cash_yield_pct": 0.0,
            "nav_capital_change_pct": 0.0,
        }
