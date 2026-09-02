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

# 升級版防阻擋爬蟲函數
def fetch_aia_fund_data(fund_code):
    clean_code = extract_fund_code(fund_code)
    url = f"https://aia-fund-api.vercel.app/api/getFund?id={clean_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price_val = data.get("currentPrice") or data.get("nav") or data.get("price") or data.get("latestPrice")
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

def render_portfolio_builder_tab():
    st.markdown("## 💼 客戶基金組合建構與動態配置試算器")
    st.caption("連動官方 Factsheet 月報股債配置與 AIA 即時爬蟲現價，提供動態組合試算")

    # 名片圓角外框 CSS
    st.markdown("""
    <style>
        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 15px 12px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            margin-bottom: 10px;
        }
        .kpi-title { font-size: 13px; font-weight: 700; color: #64748B; margin-bottom: 6px; }
        .kpi-value { font-size: 22px; font-weight: 900; color: #1E3A8A; }
        .kpi-value-green { font-size: 22px; font-weight: 900; color: #059669; }
        .kpi-value-blue { font-size: 22px; font-weight: 900; color: #2563EB; }
    </style>
    """, unsafe_allow_html=True)

    # 1. 初始化 Session State 組合資料
    if "portfolio_funds" not in st.session_state:
        st.session_state.portfolio_funds = [
            {"code": "Z51", "amount": 100000.0, "bonus": 4.0, "buy_price": 10.40, "curr_price": 10.40, "high": 11.47, "low": 8.88, "stock_pct": 100, "bond_pct": 0, "yield_pct": 8.10},
            {"code": "Z15", "amount": 100000.0, "bonus": 0.0, "buy_price": 76.67, "curr_price": 76.67, "high": 78.23, "low": 73.05, "stock_pct": 0, "bond_pct": 100, "yield_pct": 9.40}
        ]

    # 工具列
    col_tb1, col_tb2, col_tb3 = st.columns([1.5, 1.5, 1.5])
    with col_tb1:
        plan_years = st.number_input("總投資年期 (Years):", min_value=1, max_value=30, value=10, step=1, key="plan_years_input")
    with col_tb2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ 新增一隻基金", use_container_width=True):
            st.session_state.portfolio_funds.append(
                {"code": "Z01", "amount": 100000.0, "bonus": 0.0, "buy_price": 10.0, "curr_price": 10.0, "high": 12.0, "low": 8.0, "stock_pct": 100, "bond_pct": 0, "yield_pct": 5.0}
            )
            st.rerun()
    with col_tb3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ 清空所有基金", use_container_width=True):
            st.session_state.portfolio_funds = []
            st.rerun()

    st.markdown("---")

    # 2. 實時精算頂部數據
    total_cost = 0.0          
    total_initial_val = 0.0   
    total_stock_amt = 0.0     
    total_bond_amt = 0.0      
    total_curr_monthly_div = 0.0 

    portfolio_geo_weighted = {}
    portfolio_sector_weighted = {}

    for fund_item in st.session_state.portfolio_funds:
        amt = fund_item["amount"]
        bonus_pct = fund_item["bonus"]
        init_val = amt * (1.0 + bonus_pct / 100.0)
        
        total_cost += amt
        total_initial_val += init_val
        
        s_pct = fund_item["stock_pct"]
        b_pct = fund_item["bond_pct"]
        total_stock_amt += init_val * (s_pct / 100.0)
        total_bond_amt += init_val * (b_pct / 100.0)
        
        monthly_div = init_val * (fund_item["yield_pct"] / 100.0) / 12.0
        total_curr_monthly_div += monthly_div

        code = fund_item["code"]
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

    total_asset_alloc = total_stock_amt + total_bond_amt
    if total_asset_alloc > 0:
        overall_stock_pct = int(round((total_stock_amt / total_asset_alloc) * 100))
        overall_bond_pct = 100 - overall_stock_pct
    else:
        overall_stock_pct, overall_bond_pct = 0, 0

    # 3. 渲染頂部獨立長方框名片
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">總投入成本 ($)</div><div class="kpi-value">${total_cost:,.0f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">組合股債比例 (股 : 債)</div><div class="kpi-value-blue">{overall_stock_pct}% : {overall_bond_pct}%</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">期末總市值預估 ($)</div><div class="kpi-value">${total_initial_val * 1.05:,.0f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">預計每月派息 ($)</div><div class="kpi-value-green">${total_curr_monthly_div:,.0f}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">本金差額 ($)</div><div class="kpi-value">${(total_initial_val * 1.05) - total_cost:,.0f}</div></div>', unsafe_allow_html=True)
        ann_yield = (total_curr_monthly_div * 12 / total_initial_val * 100) if total_initial_val > 0 else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">組合預估年化派息率</div><div class="kpi-value">{ann_yield:.2f}%</div></div>', unsafe_allow_html=True)
    with k4:
        tot_div_collected = total_curr_monthly_div * 12 * plan_years
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">累計總收取利息 ($)</div><div class="kpi-value-green">${tot_div_collected:,.0f}</div></div>', unsafe_allow_html=True)
        roi = (tot_div_collected / total_cost * 100) if total_cost > 0 else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">預估年均回報率 (ROI)</div><div class="kpi-value">{roi:.2f}%</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 4. 基金配置編輯區 (解決 AIA 爬蟲 Session State 動態連動)
    st.markdown("### 📁 組合內基金詳細配置")
    
    fund_options = {f"{f_data.get('code', '')} {f_data.get('zh', '')}": f_code for f_code, f_data in ALL_FUNDS.items()}
    fund_labels = list(fund_options.keys())

    num_funds = len(st.session_state.portfolio_funds)
    if num_funds > 0:
        cols = st.columns(num_funds)
        
        for idx, fund_item in enumerate(st.session_state.portfolio_funds):
            with cols[idx]:
                st.markdown(f"#### 基金 #{idx + 1}")
                
                current_code = fund_item["code"]
                default_index = 0
                for label_idx, label_str in enumerate(fund_labels):
                    if current_code in label_str:
                        default_index = label_idx
                        break

                selected_label = st.selectbox("選擇基金:", options=fund_labels, index=default_index, key=f"sel_f_{idx}")
                selected_code = fund_options[selected_label]
                target_fund = ALL_FUNDS.get(selected_code, {})

                # 動態元件 Key
                f_key = f"{idx}_{selected_code}"

                # 當切換基金時，強制更正並執行 AIA 防阻擋爬蟲
                if selected_code != fund_item["code"]:
                    fund_item["code"] = selected_code
                    
                    cat = target_fund.get("category", "")
                    if "債券" in cat:
                        fund_item["stock_pct"] = 0
                        fund_item["bond_pct"] = 100
                    elif "股票" in cat and "混合" not in cat:
                        fund_item["stock_pct"] = 100
                        fund_item["bond_pct"] = 0
                    else:  # 股債混合型 (如 Z18)
                        fund_item["stock_pct"] = 52
                        fund_item["bond_pct"] = 48
                    
                    fund_item["yield_pct"] = float(target_fund.get("last_yield", 8.0))

                    # ⚡ 精確提取短代號爬蟲 AIA API
                    clean_code = extract_fund_code(selected_code)
                    aia_data = fetch_aia_fund_data(clean_code)
                    if aia_data and aia_data["price"]:
                        fund_item["curr_price"] = aia_data["price"]
                        fund_item["buy_price"] = aia_data["price"]
                        if aia_data["high"]:
                            fund_item["high"] = aia_data["high"]
                        if aia_data["low"]:
                            fund_item["low"] = aia_data["low"]

                        # 強制同步至 Session State 輸入組件，確保 UI 100% 更新
                        st.session_state[f"curr_{f_key}"] = aia_data["price"]
                        st.session_state[f"buy_{f_key}"] = aia_data["price"]

                        st.toast(f"✅ 已為 {clean_code} 成功抓取 AIA 最新現價: ${aia_data['price']}", icon="📈")

                    st.rerun()

                # 輸入組件綁定
                amt_val = st.number_input("帳面本金 ($):", value=float(fund_item["amount"]), step=10000.0, key=f"amt_{f_key}")
                fund_item["amount"] = amt_val

                bonus_val = st.number_input("開戶獎賞 (%):", value=float(fund_item["bonus"]), step=0.5, key=f"bonus_{f_key}")
                fund_item["bonus"] = bonus_val

                col_s, col_b = st.columns(2)
                with col_s:
                    stk_val = st.number_input("股票 (%):", value=int(fund_item["stock_pct"]), min_value=0, max_value=100, key=f"stk_{f_key}")
                    fund_item["stock_pct"] = stk_val
                    fund_item["bond_pct"] = 100 - stk_val
                with col_b:
                    st.number_input("債券 (%):", value=int(fund_item["bond_pct"]), disabled=True, key=f"bnd_{f_key}")

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    buy_val = st.number_input("買入價 ($):", value=float(fund_item["buy_price"]), step=0.01, key=f"buy_{f_key}")
                    fund_item["buy_price"] = buy_val
                with col_p2:
                    curr_val = st.number_input("即時現價 ($):", value=float(fund_item["curr_price"]), step=0.01, key=f"curr_{f_key}")
                    fund_item["curr_price"] = curr_val

                if fund_item["buy_price"] > 0:
                    chg_pct = ((fund_item["curr_price"] - fund_item["buy_price"]) / fund_item["buy_price"]) * 100.0
                    st.caption(f"📈 帳面升跌: **{chg_pct:+.2f}%**")

                col_h, col_l = st.columns(2)
                with col_h:
                    st.text_input("歷史高位:", value=f"${fund_item['high']:.2f}", disabled=True, key=f"hi_{f_key}")
                with col_l:
                    st.text_input("歷史低位:", value=f"${fund_item['low']:.2f}", disabled=True, key=f"lo_{f_key}")

                yld_val = st.number_input("年派息率 (%):", value=float(fund_item["yield_pct"]), step=0.1, key=f"yld_{f_key}")
                fund_item["yield_pct"] = yld_val

                if st.button("🗑️ 移除此基金", key=f"del_{f_key}"):
                    st.session_state.portfolio_funds.pop(idx)
                    st.rerun()

    # 5. 地區與行業加權圓餅圖
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
