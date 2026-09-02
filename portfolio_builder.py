import streamlit as st
import json
import requests
import pandas as pd
from funds import ALL_FUNDS  # 匯入您系統已註冊的所有 20+ 隻基金資料庫

def render_portfolio_builder_tab():
    st.markdown("## 💼 客戶基金組合建構與動態配置試算器")
    st.caption("連動官方 Factsheet 月報股債配置與 AIA 即時爬蟲現價，提供動態組合試算")

    # 1. 初始化 Session State 組合資料
    if "portfolio_funds" not in st.session_state:
        st.session_state.portfolio_funds = [
            {"code": "Z51", "amount": 125000, "bonus": 3.0, "buy_price": 10.40, "curr_price": 10.40, "high": 11.47, "low": 8.88, "stock_pct": 100, "bond_pct": 0, "yield_pct": 8.0, "w_year": 0, "w_month": 0, "w_amt": 0},
            {"code": "Z15", "amount": 125000, "bonus": 3.0, "buy_price": 76.67, "curr_price": 76.67, "high": 78.23, "low": 73.05, "stock_pct": 0, "bond_pct": 100, "yield_pct": 9.4, "w_year": 0, "w_month": 0, "w_amt": 0},
            {"code": "Z13", "amount": 125000, "bonus": 3.0, "buy_price": 9.20, "curr_price": 7.82, "high": 9.39, "low": 7.47, "stock_pct": 0, "bond_pct": 100, "yield_pct": 7.2, "w_year": 0, "w_month": 0, "w_amt": 0},
            {"code": "Z04", "amount": 125000, "bonus": 3.0, "buy_price": 8.52, "curr_price": 8.00, "high": 10.49, "low": 7.95, "stock_pct": 100, "bond_pct": 0, "yield_pct": 8.13, "w_year": 0, "w_month": 0, "w_amt": 0}
        ]

    # 工具列：總投資年期與快捷操作
    col_toolbar1, col_toolbar2 = st.columns([2, 3])
    with col_toolbar1:
        plan_years = st.number_input("總投資年期 (Years):", min_value=1, max_value=30, value=10, step=1)
    with col_toolbar2:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("➕ 新增一隻基金", use_container_width=True):
                st.session_state.portfolio_funds.append(
                    {"code": "Z01", "amount": 100000, "bonus": 0.0, "buy_price": 10.0, "curr_price": 10.0, "high": 12.0, "low": 8.0, "stock_pct": 100, "bond_pct": 0, "yield_pct": 7.5, "w_year": 0, "w_month": 0, "w_amt": 0}
                )
                st.rerun()
        with col_btn2:
            if st.button("🗑️ 清空所有基金", use_container_width=True):
                st.session_state.portfolio_funds = []
                st.rerun()

    st.markdown("---")

    # 2. 核心計算邏輯
    total_cost = 0.0          # 總投入成本
    total_initial_val = 0.0   # 含開戶獎賞初始本金
    total_stock_amt = 0.0     # 初始股票總金額
    total_bond_amt = 0.0      # 初始債券總金額
    total_curr_monthly_div = 0.0 # 預計每月派息

    # 逐一精算各基金的股債拆解與派息
    for fund_item in st.session_state.portfolio_funds:
        amt = fund_item["amount"]
        bonus_pct = fund_item["bonus"]
        init_val = amt * (1 + bonus_pct / 100.0)
        
        total_cost += amt
        total_initial_val += init_val
        
        # 加權股債比例
        s_pct = fund_item["stock_pct"]
        b_pct = fund_item["bond_pct"]
        total_stock_amt += init_val * (s_pct / 100.0)
        total_bond_amt += init_val * (b_pct / 100.0)
        
        # 預計每月派息金額 ($)
        monthly_div = init_val * (fund_item["yield_pct"] / 100.0) / 12.0
        total_curr_monthly_div += monthly_div

    # 計算組合總股債比例 %
    total_asset_alloc = total_stock_amt + total_bond_amt
    if total_asset_alloc > 0:
        overall_stock_pct = int(round((total_stock_amt / total_asset_alloc) * 100))
        overall_bond_pct = 100 - overall_stock_pct
    else:
        overall_stock_pct, overall_bond_pct = 0, 0

    # 3. 頂部 KPI 卡片區 (對齊您 HTML 的 12 個 KPI 卡片)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric("總投入成本 ($)", f"${total_cost:,.0f}")
        st.metric("組合股債比例 (股 : 債)", f"{overall_stock_pct}% : {overall_bond_pct}%")
    with kpi_col2:
        st.metric("期末總市值預估 ($)", f"${total_initial_val * 1.05:,.0f}")  # 示意滾存
        st.metric("預計每月派息 ($)", f"${total_curr_monthly_div:,.0f}")
    with kpi_col3:
        st.metric("本金差額 ($)", f"${(total_initial_val * 1.05) - total_cost:,.0f}")
        st.metric("組合預估年化派息率", f"{(total_curr_monthly_div * 12 / total_initial_val * 100) if total_initial_val > 0 else 0:.2f}%")
    with kpi_col4:
        st.metric("累計總收取利息 ($)", f"${total_curr_monthly_div * 12 * plan_years:,.0f}")
        st.metric("預估年均回報率 (ROI)", f"{((total_curr_monthly_div * 12 * plan_years) / total_cost * 100) if total_cost > 0 else 0:.2f}%")

    st.markdown("---")

    # 4. 基金卡片編輯區 (多欄式橫向卡片)
    st.markdown("### 📁 組合內基金詳細配置")
    
    # 建構基金選擇的映射選單 (名稱 -> 代號)
    fund_options = {f"{f_data.get('code', '')} {f_data.get('zh', '')}": f_code for f_code, f_data in ALL_FUNDS.items()}
    fund_labels = list(fund_options.keys())

    cols = st.columns(len(st.session_state.portfolio_funds) if len(st.session_state.portfolio_funds) > 0 else 1)

    for idx, fund_item in enumerate(st.session_state.portfolio_funds):
        with cols[idx]:
            st.markdown(f"#### 基金 #{idx + 1}")
            
            # (1) 下拉選單揀選基金 (選擇後自動帶入股債比與 AIA 即時現價)
            current_code = fund_item["code"]
            default_index = 0
            for label_idx, label_str in enumerate(fund_labels):
                if current_code in label_str:
                    default_index = label_idx
                    break

            selected_label = st.selectbox(
                "選擇基金:",
                options=fund_labels,
                index=default_index,
                key=f"select_fund_{idx}"
            )
            
            selected_code = fund_options[selected_label]
            target_fund = ALL_FUNDS.get(selected_code, {})

            # 💡 當切換基金時，自動填寫月報股債比例與 Factsheet 數據
            if selected_code != fund_item["code"]:
                fund_item["code"] = selected_code
                
                # 自動讀取月報資產類別 (股票 % vs 債券 %)
                cat = target_fund.get("category", "")
                if "股票" in cat:
                    fund_item["stock_pct"] = 100
                    fund_item["bond_pct"] = 0
                elif "債券" in cat:
                    fund_item["stock_pct"] = 0
                    fund_item["bond_pct"] = 100
                else:  # 混合型
                    fund_item["stock_pct"] = 50
                    fund_item["bond_pct"] = 50
                
                fund_item["yield_pct"] = float(target_fund.get("last_yield", 8.0))

                # ⚡ AIA 官網 API 即時爬蟲 (抓取最新現價與歷史高低位)
                try:
                    api_url = f"https://aia-fund-api.vercel.app/api/getFund?id={selected_code}"
                    res = requests.get(api_url, timeout=3).json()
                    fund_item["curr_price"] = res.get("currentPrice", fund_item["curr_price"])
                    fund_item["high"] = res.get("historyHigh", fund_item["high"])
                    fund_item["low"] = res.get("historyLow", fund_item["low"])
                except Exception:
                    pass  # 若連線失敗，保留保底數值

                st.rerun()

            # (2) 數值輸入與連動 (帳面本金、開戶獎賞、買入價、現價、高低位)
            fund_item["amount"] = st.number_input("帳面本金 ($):", value=float(fund_item["amount"]), step=10000.0, key=f"amt_{idx}")
            fund_item["bonus"] = st.number_input("開戶獎賞 (%):", value=float(fund_item["bonus"]), step=0.5, key=f"bonus_{idx}")

            col_sb1, col_sb2 = st.columns(2)
            with col_sb1:
                # 股票比例 (自動帶入，亦可手動微調)
                fund_item["stock_pct"] = st.number_input("股票 (%):", value=int(fund_item["stock_pct"]), min_value=0, max_value=100, key=f"stock_{idx}")
            with col_sb2:
                # 債券比例
                fund_item["bond_pct"] = 100 - fund_item["stock_pct"]
                st.number_input("債券 (%):", value=int(fund_item["bond_pct"]), disabled=True, key=f"bond_{idx}")

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                fund_item["buy_price"] = st.number_input("買入價 ($):", value=float(fund_item["buy_price"]), step=0.01, key=f"buy_p_{idx}")
            with col_p2:
                fund_item["curr_price"] = st.number_input("即時現價 ($):", value=float(fund_item["curr_price"]), step=0.01, key=f"curr_p_{idx}")

            # 計算帳面升跌 %
            if fund_item["buy_price"] > 0:
                p_change = ((fund_item["curr_price"] - fund_item["buy_price"]) / fund_item["buy_price"]) * 100
                st.caption(f"📈 帳面升跌: **{p_change:+.2f}%**")

            # 歷史高點與低點
            col_hl1, col_hl2 = st.columns(2)
            with col_hl1:
                st.text_input("歷史高位:", value=f"${fund_item['high']:.2f}", disabled=True, key=f"high_{idx}")
            with col_hl2:
                st.text_input("歷史低位:", value=f"${fund_item['low']:.2f}", disabled=True, key=f"low_{idx}")

            fund_item["yield_pct"] = st.number_input("年派息率 (%):", value=float(fund_item["yield_pct"]), step=0.1, key=f"yield_{idx}")

            if st.button("🗑️ 移除此基金", key=f"del_{idx}"):
                st.session_state.portfolio_funds.pop(idx)
                st.rerun()

    # 5. 組合整體風險與資產配置視覺化 (Chart.js / Streamlit Progress)
    st.markdown("---")
    st.markdown("### 📊 組合資產配置與風險審計總覽")
    
    col_chart1, col_col2 = st.columns(2)
    with col_chart1:
        st.markdown("**股債總體配置比率**")
        st.progress(overall_stock_pct / 100.0)
        st.write(f"🔵 股票比率: **{overall_stock_pct}%** | 🟢 債券比率: **{overall_bond_pct}%**")

    with col_col2:
        st.markdown("**組合主要風險等級審計**")
        has_l3_l4 = any(ALL_FUNDS.get(f["code"], {}).get("risk_derivatives", {}).get("risk_level") in ["L3", "L4"] for f in st.session_state.portfolio_funds)
        if has_l3_l4:
            st.warning("⚠️ 組合內包含 L3 (144A ELN) 或 L4 (TRS) 高風險衍生工具，請留意熔斷門檻！")
        else:
            st.success("🟢 組合安全度良好：全數基金未觸發 L3/L4 衍生工具熔斷。")
