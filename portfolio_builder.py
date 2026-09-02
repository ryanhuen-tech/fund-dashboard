import streamlit as st
import pandas as pd
import plotly.express as px
from funds import ALL_FUNDS  # 匯入系統所有基金資料庫

# 計算第 61 個月起的長期客戶獎賞 (Long-term Bonus) 階梯算式
def calculate_long_term_bonus(avg_value_60m):
    av = avg_value_60m
    bonus = 0.0
    
    # 階梯一: 首 $160,000
    p1 = min(av, 160000.0)
    bonus += p1 * (0.002 / 12.0)
    av -= p1
    
    # 階梯二: $160,000 - $240,000
    if av > 0:
        p2 = min(av, 80000.0)
        bonus += p2 * (0.003 / 12.0)
        av -= p2
        
    # 階梯三: $240,000 - $400,000
    if av > 0:
        p3 = min(av, 160000.0)
        bonus += p3 * (0.005 / 12.0)
        av -= p3
        
    # 階梯四: $400,000 以上
    if av > 0:
        bonus += av * (0.008 / 12.0)
        
    return bonus

def render_portfolio_builder_tab():
    st.markdown("## 💼 客戶基金組合建構與動態配置試算器")
    st.caption("連動官方 Factsheet 月報股債配置與手續費/長期獎賞階梯扣費演算法")

    # 名片獨立長方框 CSS 樣式
    st.markdown("""
    <style>
        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 10px;
            padding: 12px 10px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
        .kpi-title { font-size: 12px; font-weight: 700; color: #64748B; margin-bottom: 4px; }
        .kpi-value { font-size: 20px; font-weight: 900; color: #1E3A8A; }
        .kpi-value-green { font-size: 20px; font-weight: 900; color: #059669; }
        .kpi-value-blue { font-size: 20px; font-weight: 900; color: #2563EB; }
        .kpi-value-red { font-size: 20px; font-weight: 900; color: #DC2626; }
    </style>
    """, unsafe_allow_html=True)

    # 1. Session State 組合資料初始化 (包含完整的預設費率)
    if "portfolio_funds" not in st.session_state:
        st.session_state.portfolio_funds = [
            {"code": "Z04", "amount": 100000.0, "bonus": 4.0, "buy_price": 8.52, "curr_price": 8.00, "high": 12.96, "low": 7.99, "stock_pct": 100, "bond_pct": 0, "yield_pct": 8.13, "upf": 1.35, "m1": 1.00, "m6": 1.00},
            {"code": "Z13", "amount": 100000.0, "bonus": 0.0, "buy_price": 9.20, "curr_price": 7.82, "high": 9.39, "low": 7.47, "stock_pct": 0, "bond_pct": 100, "yield_pct": 7.20, "upf": 1.35, "m1": 1.00, "m6": 1.50}
        ]

    # 工具列
    col_tb1, col_tb2, col_tb3 = st.columns([1.5, 1.5, 1.5])
    with col_tb1:
        plan_years = st.number_input("總投資年期 (Years):", min_value=1, max_value=30, value=10, step=1, key="plan_years_input")
    with col_tb2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ 新增一隻基金", use_container_width=True):
            st.session_state.portfolio_funds.append(
                {"code": "Z01", "amount": 100000.0, "bonus": 0.0, "buy_price": 10.0, "curr_price": 10.0, "high": 12.0, "low": 8.0, "stock_pct": 100, "bond_pct": 0, "yield_pct": 5.0, "upf": 1.35, "m1": 1.00, "m6": 1.50}
            )
            st.rerun()
    with col_tb3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ 清空所有基金", use_container_width=True):
            st.session_state.portfolio_funds = []
            st.rerun()

    st.markdown("---")

    # 2. 優先同步 UI 畫面的最新輸入參數 (.get 安全防護)
    for idx, fund_item in enumerate(st.session_state.portfolio_funds):
        code = fund_item["code"]
        f_key = f"{idx}_{code}"
        
        if f"amt_{f_key}" in st.session_state: fund_item["amount"] = st.session_state[f"amt_{f_key}"]
        if f"bonus_{f_key}" in st.session_state: fund_item["bonus"] = st.session_state[f"bonus_{f_key}"]
        if f"stk_{f_key}" in st.session_state: 
            fund_item["stock_pct"] = st.session_state[f"stk_{f_key}"]
            fund_item["bond_pct"] = 100 - st.session_state[f"stk_{f_key}"]
        if f"yld_{f_key}" in st.session_state: fund_item["yield_pct"] = st.session_state[f"yld_{f_key}"]
        if f"upf_{f_key}" in st.session_state: fund_item["upf"] = st.session_state[f"upf_{f_key}"]
        if f"m1_{f_key}" in st.session_state: fund_item["m1"] = st.session_state[f"m1_{f_key}"]
        if f"m6_{f_key}" in st.session_state: fund_item["m6"] = st.session_state[f"m6_{f_key}"]

    # 3. 逐月模擬演算 (安全使用 .get 防止 KeyError)
    total_months = plan_years * 12
    total_cost = 0.0          
    total_initial_val = 0.0   
    total_stock_amt = 0.0     
    total_bond_amt = 0.0      
    total_curr_monthly_div = 0.0 

    portfolio_geo_weighted = {}
    portfolio_sector_weighted = {}

    calc_funds = []
    for f in st.session_state.portfolio_funds:
        amt = f.get("amount", 100000.0)
        bonus_pct = f.get("bonus", 0.0)
        init_val = amt * (1.0 + bonus_pct / 100.0)
        price0 = f.get("buy_price", 10.0) if f.get("buy_price", 10.0) > 0 else 10.0
        units = init_val / price0
        
        total_cost += amt
        total_initial_val += init_val
        
        s_pct = f.get("stock_pct", 50)
        b_pct = f.get("bond_pct", 50)
        total_stock_amt += init_val * (s_pct / 100.0)
        total_bond_amt += init_val * (b_pct / 100.0)
        
        monthly_div = init_val * (f.get("yield_pct", 8.0) / 100.0) / 12.0
        total_curr_monthly_div += monthly_div

        code = f.get("code", "Z01")
        fund_info = ALL_FUNDS.get(code, {})

        # 地區加權
        if code == "Z04" or "中國" in fund_info.get("zh", ""):
            portfolio_geo_weighted["中國/大中華"] = portfolio_geo_weighted.get("中國/大中華", 0.0) + init_val
        elif "環球" in fund_info.get("zh", "") or "全球" in fund_info.get("zh", ""):
            portfolio_geo_weighted["美國/北美"] = portfolio_geo_weighted.get("美國/北美", 0.0) + (init_val * 0.65)
            portfolio_geo_weighted["環球其他"] = portfolio_geo_weighted.get("環球其他", 0.0) + (init_val * 0.35)
        else:
            portfolio_geo_weighted["美國/成熟市場"] = portfolio_geo_weighted.get("美國/成熟市場", 0.0) + init_val

        # 行業加權
        sector_dist = fund_info.get("sector_dist", [])
        for sector_name, pct_str in sector_dist:
            try:
                pct_val = float(str(pct_str).replace("%", ""))
                portfolio_sector_weighted[sector_name] = portfolio_sector_weighted.get(sector_name, 0.0) + (init_val * (pct_val / 100.0))
            except Exception:
                pass

        calc_funds.append({
            "code": code,
            "p": amt,
            "units": units,
            "price0": price0,
            "price1": f.get("curr_price", price0),
            "upf": f.get("upf", 1.35),   # 🟢 安全容錯讀取
            "m1": f.get("m1", 1.00),     # 🟢 安全容錯讀取
            "m6": f.get("m6", 1.50),     # 🟢 安全容錯讀取
            "div": f.get("yield_pct", 8.0),
            "final_val": 0.0,
            "val_before_bonus": 0.0
        })

    # 4. 逐月手續費扣除與長期客戶賞金滾存
    cum_fee_deducted = 0.0
    cum_bonus_earned = 0.0
    values_first_60 = []

    for m in range(1, total_months + 1):
        m_val_before_b = 0.0
        
        for f in calc_funds:
            if f["units"] > 0:
                cur_p = f["price0"] + (f["price1"] - f["price0"]) * (m / total_months)
                
                if m <= 60:
                    u_deduct_upf = (f["p"] * (f["upf"] / 100.0) / 12.0) / cur_p
                    fee_cash = (f["p"] * (f["upf"] / 100.0) / 12.0) + (f["units"] * cur_p * (f["m1"] / 100.0) / 12.0)
                    f["units"] = (f["units"] * (1.0 - (f["m1"] / 100.0) / 12.0)) - u_deduct_upf
                else:
                    fee_cash = f["units"] * cur_p * (f["m6"] / 100.0) / 12.0
                    f["units"] *= (1.0 - (f["m6"] / 100.0) / 12.0)
                
                cum_fee_deducted += fee_cash
                if f["units"] < 0: f["units"] = 0.0
                f["val_before_bonus"] = f["units"] * cur_p
                m_val_before_b += f["val_before_bonus"]

        if m <= 60:
            values_first_60.append(m_val_before_b)

        month_bonus = 0.0
        if m > 60 and len(values_first_60) == 60:
            avg_60m = sum(values_first_60) / 60.0
            month_bonus = calculate_long_term_bonus(avg_60m)
            cum_bonus_earned += month_bonus

            if m_val_before_b > 0:
                for f in calc_funds:
                    if f["units"] > 0:
                        cur_p = f["price0"] + (f["price1"] - f["price0"]) * (m / total_months)
                        f["units"] += (month_bonus * (f["val_before_bonus"] / m_val_before_b)) / cur_p

    total_final_val = sum(f["units"] * f["price1"] for f in calc_funds)

    total_asset_alloc = total_stock_amt + total_bond_amt
    if total_asset_alloc > 0:
        overall_stock_pct = int(round((total_stock_amt / total_asset_alloc) * 100))
        overall_bond_pct = 100 - overall_stock_pct
    else:
        overall_stock_pct, overall_bond_pct = 0, 0

    # 5. 頂部名片渲染
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">總投入成本 ($)</div><div class="kpi-value">${total_cost:,.0f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">組合股債比例 (股 : 債)</div><div class="kpi-value-blue">{overall_stock_pct}% : {overall_bond_pct}%</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">扣費後期末總市值 ($)</div><div class="kpi-value">${total_final_val:,.0f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">預計每月派息 ($)</div><div class="kpi-value-green">${total_curr_monthly_div:,.0f}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">預估累計總手續費 ($)</div><div class="kpi-value-red">${cum_fee_deducted:,.0f}</div></div>', unsafe_allow_html=True)
        ann_yield = (total_curr_monthly_div * 12 / total_initial_val * 100) if total_initial_val > 0 else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">組合預估年化派息率</div><div class="kpi-value">{ann_yield:.2f}%</div></div>', unsafe_allow_html=True)
    with k4:
        tot_div_collected = total_curr_monthly_div * 12 * plan_years
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">累計長期客戶獎賞 ($)</div><div class="kpi-value-green">${cum_bonus_earned:,.0f}</div></div>', unsafe_allow_html=True)
        roi = (tot_div_collected / total_cost * 100) if total_cost > 0 else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">預估年均回報率 (ROI)</div><div class="kpi-value">{roi:.2f}%</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 6. 基金配置編輯區 (.get 安全賦值)
    st.markdown("### 📁 組合內基金詳細配置與手續費設定")
    
    fund_options = {f"{f_data.get('code', '')} {f_data.get('zh', '')}": f_code for f_code, f_data in ALL_FUNDS.items()}
    fund_labels = list(fund_options.keys())

    num_funds = len(st.session_state.portfolio_funds)
    if num_funds > 0:
        cols = st.columns(num_funds)
        
        for idx, fund_item in enumerate(st.session_state.portfolio_funds):
            with cols[idx]:
                st.markdown(f"#### 基金 #{idx + 1}")
                
                current_code = fund_item.get("code", "Z01")
                default_index = 0
                for label_idx, label_str in enumerate(fund_labels):
                    if current_code in label_str:
                        default_index = label_idx
                        break

                selected_label = st.selectbox("選擇基金:", options=fund_labels, index=default_index, key=f"sel_f_{idx}")
                selected_code = fund_options[selected_label]
                target_fund = ALL_FUNDS.get(selected_code, {})

                if selected_code != fund_item["code"]:
                    fund_item["code"] = selected_code
                    cat = target_fund.get("category", "")
                    if "債券" in cat:
                        fund_item["stock_pct"] = 0
                        fund_item["bond_pct"] = 100
                    elif "股票" in cat and "混合" not in cat:
                        fund_item["stock_pct"] = 100
                        fund_item["bond_pct"] = 0
                    else:
                        fund_item["stock_pct"] = 52
                        fund_item["bond_pct"] = 48
                    
                    fund_item["yield_pct"] = float(target_fund.get("last_yield", 8.0))
                    fund_item["upf"] = 1.35
                    fund_item["m1"] = 1.00
                    fund_item["m6"] = 1.50
                    st.rerun()

                f_key = f"{idx}_{selected_code}"

                st.number_input("帳面本金 ($):", value=float(fund_item.get("amount", 100000.0)), step=10000.0, key=f"amt_{f_key}")
                st.number_input("開戶獎賞 (%):", value=float(fund_item.get("bonus", 0.0)), step=0.5, key=f"bonus_{f_key}")

                col_s, col_b = st.columns(2)
                with col_s:
                    st.number_input("股票 (%):", value=int(fund_item.get("stock_pct", 50)), min_value=0, max_value=100, key=f"stk_{f_key}")
                with col_b:
                    st.number_input("債券 (%):", value=100 - int(fund_item.get("stock_pct", 50)), disabled=True, key=f"bnd_disp_{f_key}")

                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    st.number_input("前期費(%):", value=float(fund_item.get("upf", 1.35)), step=0.01, key=f"upf_{f_key}")
                with col_f2:
                    st.number_input("首5年費(%):", value=float(fund_item.get("m1", 1.00)), step=0.01, key=f"m1_{f_key}")
                with col_f3:
                    st.number_input("6年後費(%):", value=float(fund_item.get("m6", 1.50)), step=0.01, key=f"m6_{f_key}")

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.number_input("買入價 ($):", value=float(fund_item.get("buy_price", 10.0)), step=0.01, key=f"buy_{f_key}")
                with col_p2:
                    st.number_input("即時現價 ($):", value=float(fund_item.get("curr_price", 10.0)), step=0.01, key=f"curr_{f_key}")

                buy_p = fund_item.get("buy_price", 10.0)
                curr_p = fund_item.get("curr_price", 10.0)
                if buy_p > 0:
                    chg_pct = ((curr_p - buy_p) / buy_p) * 100.0
                    st.caption(f"📈 帳面升跌: **{chg_pct:+.2f}%**")

                col_h, col_l = st.columns(2)
                with col_h:
                    st.text_input("歷史高位:", value=f"${fund_item.get('high', 12.0):.2f}", disabled=True, key=f"hi_{f_key}")
                with col_l:
                    st.text_input("歷史低位:", value=f"${fund_item.get('low', 8.0):.2f}", disabled=True, key=f"lo_{f_key}")

                st.number_input("年派息率 (%):", value=float(fund_item.get("yield_pct", 8.0)), step=0.1, key=f"yld_{f_key}")

                if st.button("🗑️ 移除此基金", key=f"del_{f_key}"):
                    st.session_state.portfolio_funds.pop(idx)
                    st.rerun()

    # 7. 地區與行業加權圓餅圖
    st.markdown("---")
    st.markdown("### 📊 組合總體風險分散度分析 (地區與行業加權分佈)")

    col_chart_geo, col_chart_sec = st.columns(2)

    with col_chart_geo:
        st.markdown("#### 🌍 組合地區分佈佔比 (%)")
        if portfolio_geo_weighted and total_initial_val > 0:
            df_geo = pd.DataFrame([
                {"地區": k, "金額": v, "佔比 (%)": round((v / total_initial_val) * 100, 2)}
                for k, v in portfolio_geo_weighted.items()
            ])
            fig_geo = px.pie(df_geo, names="地區", values="金額", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_geo.update_traces(textinfo="label+percent")
            fig_geo.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=320)
            st.plotly_chart(fig_geo, use_container_width=True)
        else:
            st.info("尚無數據繪製地區分佈圖。")

    with col_chart_sec:
        st.markdown("#### 🏢 組合行業分佈佔比 (%)")
        if portfolio_sector_weighted and total_initial_val > 0:
            df_sec = pd.DataFrame([
                {"行業": k, "金額": v, "佔比 (%)": round((v / total_initial_val) * 100, 2)}
                for k, v in portfolio_sector_weighted.items()
            ])
            fig_sec = px.pie(df_sec, names="行業", values="金額", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig_sec.update_traces(textinfo="label+percent")
            fig_sec.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=320)
            st.plotly_chart(fig_sec, use_container_width=True)
        else:
            st.info("尚無數據繪製行業分佈圖。")
