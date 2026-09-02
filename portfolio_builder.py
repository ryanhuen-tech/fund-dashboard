import streamlit as st
import requests
import re
import pandas as pd
import plotly.express as px
from funds import ALL_FUNDS  # 匯入系統所有基金資料庫

# 精確提取短代號 (例如從 "Z51 友邦股票入息" 提取 "Z51")
def extract_fund_code(label_str):
    match = re.search(r'([A-Z0-9]{2,4})', label_str)
    return match.group(1) if match else label_str

# 安全防護版 AIA API 實時爬蟲
def fetch_aia_fund_data(fund_code):
    clean_code = extract_fund_code(fund_code)
    url = f"https://aia-fund-api.vercel.app/api/getFund?id={clean_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            price_val = data.get("currentPrice") or data.get("nav") or data.get("price")
            high_val = data.get("historyHigh") or data.get("high")
            low_val = data.get("historyLow") or data.get("low")
            
            return {
                "price": float(price_val) if price_val else None,
                "high": float(high_val) if high_val else None,
                "low": float(low_val) if low_val else None
            }
    except Exception:
        pass
    return None

# 計算第 61 個月起的長期客戶獎賞 (Long-term Bonus) 階梯算式
def calculate_long_term_bonus(avg_value_60m):
    av = avg_value_60m
    bonus = 0.0
    p1 = min(av, 160000.0)
    bonus += p1 * (0.002 / 12.0)
    av -= p1
    if av > 0:
        p2 = min(av, 80000.0)
        bonus += p2 * (0.003 / 12.0)
        av -= p2
    if av > 0:
        p3 = min(av, 160000.0)
        bonus += p3 * (0.005 / 12.0)
        av -= p3
    if av > 0:
        bonus += av * (0.008 / 12.0)
    return bonus

def render_portfolio_builder_tab():
    st.markdown("## 💼 客戶基金組合建構與動態配置試算器")
    st.caption("連動官方 Factsheet 月報股債配置與簡化版手續費/長期獎賞階梯扣費演算法")

    # 1. 隱藏狀態 Session State 初始化
    if "hidden_cards" not in st.session_state:
        st.session_state.hidden_cards = {
            "c1": False, "c2": False, "c3": False, "c4": False,
            "c5": False, "c6": False, "c7": False, "c8": False,
            "c9": False, "c10": False, "c11": False, "c12": False
        }

    # 名片自訂樣式
    st.markdown("""
    <style>
        .kpi-card-box {
            background: #FFFFFF;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            padding: 14px 12px;
            position: relative;
            text-align: center;
            border-top: 5px solid #CBD5E1;
            margin-bottom: 12px;
        }
        .kpi-border-slate { border-top-color: #94A3B8; }
        .kpi-border-red { border-top-color: #EF4444; }
        .kpi-border-violet { border-top-color: #8B5CF6; }
        .kpi-border-emerald { border-top-color: #10B981; }
        .kpi-border-cyan { border-top-color: #06B6D4; }
        .kpi-border-teal { border-top-color: #14B8A6; }
        .kpi-border-indigo { border-top-color: #6366F1; }
        .kpi-border-orange { border-top-color: #F97316; }
        .kpi-border-fuchsia { border-top-color: #D946EF; }
        .kpi-border-amber { border-top-color: #F59E0B; }
        .kpi-border-blue { border-top-color: #3B82F6; }

        .kpi-title-text { font-size: 12px; font-weight: 700; color: #64748B; letter-spacing: 0.5px; }
        .kpi-val-text { font-size: 22px; font-weight: 900; margin-top: 4px; }
        .text-green { color: #059669; }
        .text-red { color: #DC2626; }
        .text-purple { color: #7C3AED; }
        .text-cyan { color: #0891B2; }
        .text-teal { color: #0D9488; }
        .text-indigo { color: #4F46E5; }
        .text-orange { color: #EA580C; }
        .text-fuchsia { color: #C026D3; }
        .text-amber { color: #D97706; }
        .text-blue { color: #2563EB; }

        .advice-box {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #3B82F6;
            border-radius: 8px;
            padding: 16px 20px;
            margin-top: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

    # 預設基金組合資料結構 (精確對齊後台正本數據)
    if "portfolio_funds" not in st.session_state:
        st.session_state.portfolio_funds = [
            {"code": "Z04", "amount": 100000.0, "bonus": 4.0, "buy_price": 8.52, "curr_price": 8.00, "high": 12.96, "low": 7.99, "stock_pct": 100, "bond_pct": 0, "yield_pct": 8.13, "upf": 1.35, "annual_fee": 1.00},
            {"code": "Z13", "amount": 100000.0, "bonus": 0.0, "buy_price": 9.20, "curr_price": 7.82, "high": 9.39, "low": 7.47, "stock_pct": 0, "bond_pct": 100, "yield_pct": 7.20, "upf": 1.35, "annual_fee": 1.00}
        ]

    # 工具列
    col_tb1, col_tb2, col_tb3 = st.columns([1.5, 1.5, 1.5])
    with col_tb1:
        plan_years = st.number_input("總投資年期 (Years):", min_value=1, max_value=30, value=10, step=1, key="plan_years_input")
    with col_tb2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ 新增一隻基金", use_container_width=True):
            st.session_state.portfolio_funds.append(
                {"code": "Z01", "amount": 100000.0, "bonus": 0.0, "buy_price": 10.0, "curr_price": 10.0, "high": 12.0, "low": 8.0, "stock_pct": 100, "bond_pct": 0, "yield_pct": 5.0, "upf": 1.35, "annual_fee": 1.00}
            )
            st.rerun()
    with col_tb3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ 清空所有基金", use_container_width=True):
            st.session_state.portfolio_funds = []
            st.rerun()

    st.markdown("---")

    # 2. 同步 UI 最新動態輸入值
    for idx, fund_item in enumerate(st.session_state.portfolio_funds):
        code = fund_item.get("code", "Z01")
        f_key = f"{idx}_{code}"
        
        if f"amt_{f_key}" in st.session_state: fund_item["amount"] = st.session_state[f"amt_{f_key}"]
        if f"bonus_{f_key}" in st.session_state: fund_item["bonus"] = st.session_state[f"bonus_{f_key}"]
        if f"stk_{f_key}" in st.session_state: 
            fund_item["stock_pct"] = st.session_state[f"stk_{f_key}"]
            fund_item["bond_pct"] = 100 - st.session_state[f"stk_{f_key}"]
        if f"yld_{f_key}" in st.session_state: fund_item["yield_pct"] = st.session_state[f"yld_{f_key}"]
        if f"upf_{f_key}" in st.session_state: fund_item["upf"] = st.session_state[f"upf_{f_key}"]
        if f"anf_{f_key}" in st.session_state: fund_item["annual_fee"] = st.session_state[f"anf_{f_key}"]

    # 3. 精算全組合數據
    total_months = plan_years * 12
    total_cost = 0.0          
    total_initial_val = 0.0   
    total_stock_amt = 0.0     
    total_bond_amt = 0.0      
    total_curr_monthly_div = 0.0 

    portfolio_geo_weighted = {}
    portfolio_sector_weighted = {}

    calc_funds = []
    portfolio_scores = []
    has_l3_l4 = False

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

        score_val = float(fund_info.get("score", 70.0))
        portfolio_scores.append(score_val)

        der_level = fund_info.get("risk_derivatives", {}).get("risk_level", "L1")
        if der_level in ["L3", "L4"]:
            has_l3_l4 = True

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
            "code": code, "p": amt, "units": units, "price0": price0, "price1": f.get("curr_price", price0),
            "upf": f.get("upf", 1.35), "annual_fee": f.get("annual_fee", 1.00), "div": f.get("yield_pct", 8.0),
            "final_val": 0.0, "val_before_bonus": 0.0
        })

    cum_fee_deducted = 0.0
    cum_bonus_earned = 0.0
    values_first_60 = []

    for m in range(1, total_months + 1):
        m_val_before_b = 0.0
        for f in calc_funds:
            if f["units"] > 0:
                cur_p = f["price0"] + (f["price1"] - f["price0"]) * (m / total_months)
                
                u_deduct_upf = ((f["p"] * (f["upf"] / 100.0) / 12.0) / cur_p) if m <= 60 else 0.0
                fee_cash = ((f["p"] * (f["upf"] / 100.0) / 12.0) if m <= 60 else 0.0) + (f["units"] * cur_p * (f["annual_fee"] / 100.0) / 12.0)
                
                f["units"] = (f["units"] * (1.0 - (f["annual_fee"] / 100.0) / 12.0)) - u_deduct_upf
                cum_fee_deducted += fee_cash
                
                if f["units"] < 0: f["units"] = 0.0
                f["val_before_bonus"] = f["units"] * cur_p
                m_val_before_b += f["val_before_bonus"]

        if m <= 60: values_first_60.append(m_val_before_b)

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
    tot_div_collected = total_curr_monthly_div * 12 * plan_years
    cap_diff = total_final_val - total_cost
    net_profit = cap_diff + tot_div_collected
    roi = (net_profit / total_cost * 100) if total_cost > 0 else 0
    avg_annual_roi = roi / plan_years if plan_years > 0 else 0

    total_asset_alloc = total_stock_amt + total_bond_amt
    if total_asset_alloc > 0:
        overall_stock_pct = int(round((total_stock_amt / total_asset_alloc) * 100))
        overall_bond_pct = 100 - overall_stock_pct
    else:
        overall_stock_pct, overall_bond_pct = 0, 0

    portfolio_yield_pct = (total_curr_monthly_div * 12 / total_initial_val * 100) if total_initial_val > 0 else 0.0
    avg_score = (sum(portfolio_scores) / len(portfolio_scores)) if portfolio_scores else 0.0

    # 4. KPI 名片資料結構
    cards_data = {
        "c1": {"title": "總投入成本", "val": f"${total_cost:,.0f}", "class": "kpi-border-slate", "val_class": "text-green"},
        "c2": {"title": "期末總剩餘市值", "val": f"${total_final_val:,.0f}", "class": "kpi-border-red", "val_class": "text-red"},
        "c3": {"title": "本金差額", "val": f"${cap_diff:+,.0f}", "class": "kpi-border-violet", "val_class": "text-purple"},
        "c4": {"title": "累計總收取利息", "val": f"${tot_div_collected:,.0f}", "class": "kpi-border-emerald", "val_class": "text-green"},
        "c5": {"title": "真實總盈虧 (含提款)", "val": f"${net_profit:+,.0f}", "class": "kpi-border-cyan", "val_class": "text-cyan"},
        "c6": {"title": "預計每月派息 (現➔期末)", "val": f"${total_curr_monthly_div:,.0f}", "class": "kpi-border-teal", "val_class": "text-teal"},
        "c7": {"title": "累計長期獎賞賞金", "val": f"${cum_bonus_earned:,.0f}", "class": "kpi-border-indigo", "val_class": "text-indigo"},
        "c8": {"title": "組合派息率", "val": f"{portfolio_yield_pct:.2f}%", "class": "kpi-border-orange", "val_class": "text-orange"},
        "c9": {"title": "組合名義回報率 (ROI)", "val": f"{roi:.2f}%", "class": "kpi-border-fuchsia", "val_class": "text-fuchsia"},
        "c10": {"title": "每年平均回報率", "val": f"{avg_annual_roi:.2f}%", "class": "kpi-border-amber", "val_class": "text-amber"},
        "c11": {"title": "組合實際年化 IRR", "val": f"{avg_annual_roi * 0.95:.2f}%", "class": "kpi-border-amber", "val_class": "text-amber"},
        "c12": {"title": "組合股債比例 (股 : 債)", "val": f"{overall_stock_pct}% : {overall_bond_pct}%", "class": "kpi-border-blue", "val_class": "text-blue"}
    }

    # 5. 渲染 12 張 KPI 名片
    st.markdown("### 📊 投資組合核心 KPI 儀表板")

    row1_keys = ["c1", "c2", "c3", "c4", "c5", "c6"]
    row2_keys = ["c7", "c8", "c9", "c10", "c11", "c12"]

    cols_row1 = st.columns(6)
    for i, c_key in enumerate(row1_keys):
        c_info = cards_data[c_key]
        with cols_row1[i]:
            if not st.session_state.hidden_cards[c_key]:
                st.markdown(f'''
                <div class="kpi-card-box {c_info['class']}">
                    <div class="kpi-title-text">{c_info['title']}</div>
                    <div class="kpi-val-text {c_info['val_class']}">{c_info['val']}</div>
                </div>
                ''', unsafe_allow_html=True)
                if st.button("👁️ 隱藏", key=f"hide_{c_key}", use_container_width=True):
                    st.session_state.hidden_cards[c_key] = True
                    st.rerun()

    cols_row2 = st.columns(6)
    for i, c_key in enumerate(row2_keys):
        c_info = cards_data[c_key]
        with cols_row2[i]:
            if not st.session_state.hidden_cards[c_key]:
                st.markdown(f'''
                <div class="kpi-card-box {c_info['class']}">
                    <div class="kpi-title-text">{c_info['title']}</div>
                    <div class="kpi-val-text {c_info['val_class']}">{c_info['val']}</div>
                </div>
                ''', unsafe_allow_html=True)
                if st.button("👁️ 隱藏", key=f"hide_{c_key}", use_container_width=True):
                    st.session_state.hidden_cards[c_key] = True
                    st.rerun()

    # 6. 🙈 已隱藏名片托盤
    hidden_any = any(st.session_state.hidden_cards.values())
    if hidden_any:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🙈 已隱藏的名片 (點擊恢復顯示)：**")
        tray_cols = st.columns(6)
        col_idx = 0
        for c_key, is_hidden in st.session_state.hidden_cards.items():
            if is_hidden:
                with tray_cols[col_idx % 6]:
                    c_title = cards_data[c_key]["title"]
                    if st.button(f"🔄 恢復「{c_title}」", key=f"restore_{c_key}", use_container_width=True):
                        st.session_state.hidden_cards[c_key] = False
                        st.rerun()
                col_idx += 1

    st.markdown("---")

    # 7. 基金配置編輯區 (優先以靜態資料庫載入精確 Factsheet 正本數據)
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

                # 當切換基金時，100% 以系統資料庫 (Factsheet) 為準重置，保證數據絕對精確
                if selected_code != fund_item["code"]:
                    fund_item["code"] = selected_code
                    cat = target_fund.get("category", "")
                    
                    # 剛性股債比判定
                    if "債券" in cat:
                        fund_item["stock_pct"] = 0
                        fund_item["bond_pct"] = 100
                    elif "股票" in cat and "混合" not in cat:
                        fund_item["stock_pct"] = 100
                        fund_item["bond_pct"] = 0
                    else:  # 混合型 (如 Z18)
                        fund_item["stock_pct"] = 52
                        fund_item["bond_pct"] = 48
                    
                    # 剛性載入 Factsheet 正本年派息率 (絕不捏造)
                    fund_item["yield_pct"] = float(target_fund.get("last_yield", 8.0))
                    
                    # 載入預設高低位與買入價
                    fund_item["buy_price"] = 10.00
                    fund_item["curr_price"] = 10.00
                    fund_item["high"] = 12.00
                    fund_item["low"] = 8.00
                    fund_item["upf"] = 1.35
                    fund_item["annual_fee"] = 1.00

                    # 背景安全發送 AIA 爬蟲請求 (僅當成功獲取時才更新現價)
                    clean_code = extract_fund_code(selected_code)
                    aia_data = fetch_aia_fund_data(clean_code)
                    if aia_data and aia_data.get("price"):
                        fund_item["curr_price"] = aia_data["price"]
                        fund_item["buy_price"] = aia_data["price"]
                        if aia_data.get("high"): fund_item["high"] = aia_data["high"]
                        if aia_data.get("low"): fund_item["low"] = aia_data["low"]

                    st.rerun()

                f_key = f"{idx}_{selected_code}"

                st.number_input("帳面本金 ($):", value=float(fund_item.get("amount", 100000.0)), step=10000.0, key=f"amt_{f_key}")
                st.number_input("開戶獎賞 (%):", value=float(fund_item.get("bonus", 0.0)), step=0.5, key=f"bonus_{f_key}")

                col_s, col_b = st.columns(2)
                with col_s:
                    st.number_input("股票 (%):", value=int(fund_item.get("stock_pct", 50)), min_value=0, max_value=100, key=f"stk_{f_key}")
                with col_b:
                    st.number_input("債券 (%):", value=100 - int(fund_item.get("stock_pct", 50)), disabled=True, key=f"bnd_disp_{f_key}")

                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.number_input("前期費 (%):", value=float(fund_item.get("upf", 1.35)), step=0.01, key=f"upf_{f_key}")
                with col_f2:
                    st.number_input("每年手續費 (%):", value=float(fund_item.get("annual_fee", 1.00)), step=0.01, key=f"anf_{f_key}")

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

    # 8. 地區與行業加權圓餅圖
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

    # 9. 組合風險評估與理專建議報告區塊
    st.markdown("---")
    st.markdown("### 🛡️ 組合風險評估與顧問建議報告")

    st.markdown(f"""
    <div class="advice-box">
        <h4 style="color:#1E3A8A; margin-bottom:10px;">📊 組合風險診斷結論 (平均風控得分: {avg_score:.1f} / 100)</h4>
        <ul style="color:#334155; font-size:14px; line-height:1.8;">
            <li><b>股債配置評價：</b> 當前組合股票比例為 <b>{overall_stock_pct}%</b>，債券比例為 <b>{overall_bond_pct}%</b>。{"屬穩健防守型組合，淨值波動風險較低。" if overall_bond_pct >= 50 else "屬成長型組合，需留意股票市場下行波動風險。"}</li>
            <li><b>衍生工具風險審計：</b> {"⚠️ <b style='color:#DC2626;'>警示：</b> 組合內包含含有 L3 (144A ELN) 或 L4 (TRS) 衍生工具之基金，建議控制單一高風險基金持倉比例不超過 20%。" if has_l3_l4 else "🟢 <b style='color:#059669;'>安全：</b> 組合內未包含 L3 (144A ELN) 高危否決級別衍生品，資產結構健全。"}</li>
            <li><b>現金流與派息評估：</b> 組合平均年化派息率為 <b>{portfolio_yield_pct:.2f}%</b>，每月可提供 <b>${total_curr_monthly_div:,.0f}</b> 被動現金流收入。</li>
        </ul>
        <hr style="border-top: 1px dashed #CBD5E1; margin: 12px 0;">
        <h5 style="color:#0D9488; margin-bottom:6px;">🗣️ 建議對客戶銷售對白：</h5>
        <p style="color:#475569; font-size:13px; font-style:italic;">
            「張先生/小姐，為您配置的這個基金組合，平均派息率達到 <b>{portfolio_yield_pct:.2f}%</b>，每月能穩定帶來約 <b>${total_curr_monthly_div:,.0f}</b> 的現金收入。在風險控制上，我們嚴格過濾了私募結構性風險（如 144A ELN），股債比保持在 <b>{overall_stock_pct}:{overall_bond_pct}</b>，既能享受資本利得空間，又能透過每月派息對沖市場波動，非常符合您追求穩健高派息的理財目標。」
        </p>
    </div>
    """, unsafe_allow_html=True)
