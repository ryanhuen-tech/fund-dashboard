import streamlit as st
import re
import uuid
import pandas as pd
import plotly.express as px
from funds import ALL_FUNDS  # 匯入系統所有基金資料庫

# 精確提取短代號
def extract_fund_code(label_str):
    match = re.search(r'([A-Z0-9]{2,4})', label_str)
    return match.group(1) if match else label_str

# 1. 從資料庫正本提取真實派息率
def get_exact_yield_from_fund(target_fund):
    history_div = target_fund.get("history_div", [])
    if history_div and len(history_div) > 0:
        latest_record = history_div[0]
        if len(latest_record) >= 6:
            yield_str = str(latest_record[5]).replace("%", "").strip()
            try:
                return float(yield_str)
            except ValueError:
                pass
    
    last_y = target_fund.get("last_yield")
    if last_y is not None:
        try:
            return float(str(last_y).replace("%", "").strip())
        except ValueError:
            pass
            
    return 7.50

# 2. 從資料庫正本提取真實股債配置
def get_exact_asset_alloc(target_fund):
    cat = target_fund.get("category", "")
    if "債券" in cat:
        return 0, 100
    elif "股票" in cat and "混合" not in cat:
        return 100, 0
    elif "混合" in cat:
        return 52, 48
    return 50, 50

# 3. 初始化內建與自訂模版字典 (所有賞金預設設定為 0.0%)
def init_custom_templates():
    if "saved_templates" not in st.session_state:
        st.session_state.saved_templates = {
            "低風險組合 (保守型 - 高收益債券)": [
                {"code": "Z13", "amt": 100000.0, "bonus": 0.0, "stk": 0, "bnd": 100},
                {"code": "Z15", "amt": 100000.0, "bonus": 0.0, "stk": 0, "bnd": 100}
            ],
            "中風險組合 (平衡型 - 股債對半)": [
                {"code": "Z04", "amt": 100000.0, "bonus": 0.0, "stk": 100, "bnd": 0},
                {"code": "Z13", "amt": 100000.0, "bonus": 0.0, "stk": 0, "bnd": 100}
            ],
            "高風險組合 (積極型 - 股票入息)": [
                {"code": "Z04", "amt": 100000.0, "bonus": 0.0, "stk": 100, "bnd": 0},
                {"code": "Z51", "amt": 100000.0, "bonus": 0.0, "stk": 100, "bnd": 0}
            ]
        }

# 4. 根據名稱建立組合物件 (預設賞金為 0.0%)
def create_portfolio_from_template(template_name):
    selected_items = st.session_state.saved_templates.get(template_name, [])
    new_funds = []
    
    for item in selected_items:
        code = item["code"]
        target_fund = ALL_FUNDS.get(code, {})
        stk = item.get("stk", 50)
        bnd = item.get("bnd", 50)
        yld = item.get("yld", get_exact_yield_from_fund(target_fund))
        
        new_funds.append({
            "id": str(uuid.uuid4()),
            "code": code,
            "amount": item.get("amt", 100000.0),
            "bonus": 0.0,  # 🟢 預設開戶賞金設定為 0.0
            "buy_price": item.get("buy_price", 10.00),
            "curr_price": item.get("curr_price", 10.00),
            "stock_pct": stk,
            "bond_pct": bnd,
            "yield_pct": yld,
            "upf": item.get("upf", 1.35),
            "annual_fee": item.get("annual_fee", 1.00)
        })
        
    return new_funds

# 5. 下拉選單切換時強制更新 UI 狀態
def on_fund_select_change(f_id, fund_item):
    sel_label = st.session_state.get(f"sel_{f_id}")
    if not sel_label:
        return
    fund_options = {f"{f_data.get('code', '')} {f_data.get('zh', '')}": f_code for f_code, f_data in ALL_FUNDS.items()}
    selected_code = fund_options.get(sel_label)
    if not selected_code:
        return
        
    target_fund = ALL_FUNDS.get(selected_code, {})
    fund_item["code"] = selected_code
    
    stk, bnd = get_exact_asset_alloc(target_fund)
    st.session_state[f"stk_{f_id}"] = stk
    st.session_state[f"bnd_{f_id}"] = bnd
    fund_item["stock_pct"] = stk
    fund_item["bond_pct"] = bnd
        
    exact_yield = get_exact_yield_from_fund(target_fund)
    st.session_state[f"yld_{f_id}"] = exact_yield
    fund_item["yield_pct"] = exact_yield

def on_stock_change(f_id, fund_item):
    new_stk = st.session_state.get(f"stk_{f_id}", 50)
    new_bnd = 100 - new_stk
    st.session_state[f"bnd_{f_id}"] = new_bnd
    fund_item["stock_pct"] = new_stk
    fund_item["bond_pct"] = new_bnd

def on_bond_change(f_id, fund_item):
    new_bnd = st.session_state.get(f"bnd_{f_id}", 50)
    new_stk = 100 - new_bnd
    st.session_state[f"stk_{f_id}"] = new_stk
    fund_item["stock_pct"] = new_stk
    fund_item["bond_pct"] = new_bnd

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

    init_custom_templates()

    # 1. 隱藏狀態與卡片順序 Session State 初始化
    if "hidden_cards" not in st.session_state:
        st.session_state.hidden_cards = {
            "c1": False, "c2": False, "c3": False, "c4": False,
            "c5": False, "c6": False, "c7": False, "c8": False,
            "c9": False, "c10": False, "c11": False, "c12": False
        }

    # 名片預設順序初始化
    if "card_order" not in st.session_state:
        st.session_state.card_order = [
            "c1", "c2", "c3", "c4", "c5", "c6",
            "c7", "c8", "c9", "c10", "c11", "c12"
        ]

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

    # 頂部模版管理區塊
    st.markdown("#### ⚡ 投資組合策略模版管理")
    
    template_list = list(st.session_state.saved_templates.keys())
    
    col_tpl_sel, col_tpl_act1, col_tpl_act2 = st.columns([2.5, 1, 1])
    with col_tpl_sel:
        selected_template = st.selectbox("選擇預設或自訂模版:", options=template_list, key="tpl_select")
    with col_tpl_act1:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 載入此組合", use_container_width=True):
            st.session_state.portfolio_funds = create_portfolio_from_template(selected_template)
            st.toast(f"已載入模版：「{selected_template}」", icon="✅")
            st.rerun()
    with col_tpl_act2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ 刪除此模版", use_container_width=True):
            if selected_template in st.session_state.saved_templates:
                del st.session_state.saved_templates[selected_template]
                st.toast(f"已刪除模版：「{selected_template}」", icon="🗑️")
                st.rerun()

    # 自訂名稱並儲存當前畫面的組合
    col_save_name, col_save_btn = st.columns([3, 1])
    with col_save_name:
        new_template_name = st.text_input("輸入自訂組合名稱 (例：張先生 - 20萬美金高派息方案):", placeholder="請輸入組合名稱...", key="new_tpl_name_input")
    with col_save_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("💾 儲存當前組合", use_container_width=True):
            if new_template_name.strip():
                saved_data = []
                for f in st.session_state.portfolio_funds:
                    saved_data.append({
                        "code": f.get("code", "Z01"),
                        "amt": f.get("amount", 100000.0),
                        "bonus": 0.0,  # 🟢 儲存時開戶獎賞預設為 0.0
                        "stk": f.get("stock_pct", 50),
                        "bnd": f.get("bond_pct", 50),
                        "yld": f.get("yield_pct", 7.5),
                        "buy_price": f.get("buy_price", 10.0),
                        "curr_price": f.get("curr_price", 10.0),
                        "upf": f.get("upf", 1.35),
                        "annual_fee": f.get("annual_fee", 1.00)
                    })
                st.session_state.saved_templates[new_template_name.strip()] = saved_data
                st.toast(f"🎉 成功儲存組合：「{new_template_name.strip()}」", icon="💾")
                st.rerun()
            else:
                st.warning("請先輸入組合名稱再儲存！")

    st.markdown("---")

    # 初始化預設基金
    if "portfolio_funds" not in st.session_state:
        st.session_state.portfolio_funds = create_portfolio_from_template("中風險組合 (平衡型 - 股債對半)")

    for fund_item in st.session_state.portfolio_funds:
        if "id" not in fund_item:
            fund_item["id"] = str(uuid.uuid4())

    # 工具列第二排：基礎設定與增刪
    col_tb1, col_tb2, col_tb3 = st.columns([1.5, 1.5, 1.5])
    with col_tb1:
        plan_years = st.number_input("總投資年期 (Years):", min_value=1, max_value=30, value=10, step=1, key="plan_years_input")
    with col_tb2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ 新增一隻基金", use_container_width=True):
            f_default = ALL_FUNDS.get("Z01", {})
            stk, bnd = get_exact_asset_alloc(f_default)
            st.session_state.portfolio_funds.append(
                {
                    "id": str(uuid.uuid4()),
                    "code": "Z01", "amount": 100000.0, "bonus": 0.0, "buy_price": 10.0, "curr_price": 10.0,  # 🟢 賞金設為 0.0
                    "stock_pct": stk, "bond_pct": bnd,
                    "yield_pct": get_exact_yield_from_fund(f_default),
                    "upf": 1.35, "annual_fee": 1.00
                }
            )
            st.rerun()
    with col_tb3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ 清空所有基金", use_container_width=True):
            st.session_state.portfolio_funds = []
            st.rerun()

    st.markdown("---")

    # 2. 同步 UI 最新動態輸入值
    for fund_item in st.session_state.portfolio_funds:
        f_id = fund_item.get("id")
        code = fund_item.get("code", "Z01")
        target_fund = ALL_FUNDS.get(code, {})

        if f"stk_{f_id}" not in st.session_state or f"bnd_{f_id}" not in st.session_state:
            stk_init, bnd_init = get_exact_asset_alloc(target_fund)
            st.session_state[f"stk_{f_id}"] = stk_init
            st.session_state[f"bnd_{f_id}"] = bnd_init
            fund_item["stock_pct"] = stk_init
            fund_item["bond_pct"] = bnd_init
        else:
            fund_item["stock_pct"] = st.session_state[f"stk_{f_id}"]
            fund_item["bond_pct"] = st.session_state[f"bnd_{f_id}"]

        if f"amt_{f_id}" in st.session_state: fund_item["amount"] = st.session_state[f"amt_{f_id}"]
        if f"bonus_{f_id}" in st.session_state: fund_item["bonus"] = st.session_state[f"bonus_{f_id}"]
        if f"yld_{f_id}" in st.session_state: fund_item["yield_pct"] = st.session_state[f"yld_{f_id}"]
        if f"upf_{f_id}" in st.session_state: fund_item["upf"] = st.session_state[f"upf_{f_id}"]
        if f"anf_{f_id}" in st.session_state: fund_item["annual_fee"] = st.session_state[f"anf_{f_id}"]
        if f"buy_{f_id}" in st.session_state: fund_item["buy_price"] = st.session_state[f"buy_{f_id}"]
        if f"curr_{f_id}" in st.session_state: fund_item["curr_price"] = st.session_state[f"curr_{f_id}"]

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
    weighted_score_sum = 0.0
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
        
        yield_val = f.get("yield_pct", 8.0)
        monthly_div = init_val * (yield_val / 100.0) / 12.0
        total_curr_monthly_div += monthly_div

        code = f.get("code", "Z01")
        fund_info = ALL_FUNDS.get(code, {})

        score_val = float(fund_info.get("score", 85.0))
        weighted_score_sum += score_val * init_val

        der_level = fund_info.get("risk_derivatives", {}).get("risk_level", "L1")
        if der_level in ["L3", "L4"] or code in ["Z18", "Z17"]:
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
            "upf": f.get("upf", 1.35), "annual_fee": f.get("annual_fee", 1.00), "div": yield_val,
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
    avg_score = (weighted_score_sum / total_initial_val) if total_initial_val > 0 else 0.0

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

    # 🟢 5. 渲染 12 張 KPI 名片 (支援名片位置上下移動與順序調整)
    st.markdown("### 📊 投資組合核心 KPI 儀表板")

    # 折疊選單：提供名片順序調整功能
    with st.expander("↕️ 點擊展開：調整名片顯示順序", expanded=False):
        st.caption("您可以透過點擊「⬆️ 向上」或「⬇️ 向下」自由搬移調整名片的顯示優先順序：")
        for pos, c_key in enumerate(st.session_state.card_order):
            c_title = cards_data[c_key]["title"]
            col_pos_title, col_up, col_dn = st.columns([3, 1, 1])
            with col_pos_title:
                st.write(f"**第 {pos + 1} 位:** {c_title}")
            with col_up:
                if pos > 0:
                    if st.button("⬆️ 向上", key=f"move_up_{c_key}"):
                        st.session_state.card_order[pos], st.session_state.card_order[pos - 1] = st.session_state.card_order[pos - 1], st.session_state.card_order[pos]
                        st.rerun()
            with col_dn:
                if pos < len(st.session_state.card_order) - 1:
                    if st.button("⬇️ 向下", key=f"move_dn_{c_key}"):
                        st.session_state.card_order[pos], st.session_state.card_order[pos + 1] = st.session_state.card_order[pos + 1], st.session_state.card_order[pos]
                        st.rerun()

    # 依動態順序分兩排渲染 (每排 6 張)
    ordered_keys = [k for k in st.session_state.card_order if k in cards_data]
    row1_keys = ordered_keys[:6]
    row2_keys = ordered_keys[6:12]

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

    # 7. 基金配置編輯區 (開戶賞金預設為 0.0)
    st.markdown("### 📁 組合內基金詳細配置與手續費設定")
    
    fund_options = {f"{f_data.get('code', '')} {f_data.get('zh', '')}": f_code for f_code, f_data in ALL_FUNDS.items()}
    fund_labels = list(fund_options.keys())

    num_funds = len(st.session_state.portfolio_funds)
    if num_funds > 0:
        cols = st.columns(num_funds)
        
        for idx, fund_item in enumerate(st.session_state.portfolio_funds):
            with cols[idx]:
                st.markdown(f"#### 基金 #{idx + 1}")
                
                f_id = fund_item.get("id", str(uuid.uuid4()))
                current_code = fund_item.get("code", "Z01")
                default_index = 0
                for label_idx, label_str in enumerate(fund_labels):
                    if current_code in label_str:
                        default_index = label_idx
                        break

                selected_label = st.selectbox(
                    "選擇基金:", 
                    options=fund_labels, 
                    index=default_index, 
                    key=f"sel_{f_id}",
                    on_change=on_fund_select_change,
                    args=(f_id, fund_item)
                )

                st.number_input("帳面本金 ($):", value=float(fund_item.get("amount", 100000.0)), step=10000.0, key=f"amt_{f_id}")
                st.number_input("開戶獎賞 (%):", value=float(fund_item.get("bonus", 0.0)), step=0.5, key=f"bonus_{f_id}")  # 🟢 預設顯示 0.0

                col_s, col_b = st.columns(2)
                with col_s:
                    st.number_input(
                        "股票 (%):", 
                        value=int(st.session_state.get(f"stk_{f_id}", fund_item.get("stock_pct", 50))), 
                        min_value=0, max_value=100, 
                        key=f"stk_{f_id}",
                        on_change=on_stock_change,
                        args=(f_id, fund_item)
                    )
                with col_b:
                    st.number_input(
                        "債券 (%):", 
                        value=int(st.session_state.get(f"bnd_{f_id}", fund_item.get("bond_pct", 50))), 
                        min_value=0, max_value=100, 
                        key=f"bnd_{f_id}",
                        on_change=on_bond_change,
                        args=(f_id, fund_item)
                    )

                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.number_input("前期費 (%):", value=float(fund_item.get("upf", 1.35)), step=0.01, key=f"upf_{f_id}")
                with col_f2:
                    st.number_input("每年手續費 (%):", value=float(fund_item.get("annual_fee", 1.00)), step=0.01, key=f"anf_{f_id}")

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.number_input("買入價 ($):", value=float(fund_item.get("buy_price", 10.0)), step=0.01, key=f"buy_{f_id}")
                with col_p2:
                    st.number_input("現價 ($):", value=float(fund_item.get("curr_price", 10.0)), step=0.01, key=f"curr_{f_id}")

                buy_p = fund_item.get("buy_price", 10.0)
                curr_p = fund_item.get("curr_price", 10.0)
                if buy_p > 0:
                    chg_pct = ((curr_p - buy_p) / buy_p) * 100.0
                    st.caption(f"📈 帳面升跌: **{chg_pct:+.2f}%**")

                # 年派息率
                st.number_input("年派息率 (%):", value=float(fund_item.get("yield_pct", 7.5)), step=0.1, key=f"yld_{f_id}")

                if st.button("🗑️ 移除此基金", key=f"del_{f_id}"):
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

    alloc_comment = "屬防守型組合，淨值波動風險較低。" if overall_bond_pct >= 50 else "屬成長型組合，需留意股票市場下行波動風險。"
    deriv_comment = "⚠️ <b style='color:#DC2626;'>警示：</b> 組合內含有 L3 (144A ELN) 或 L4 (TRS) 高風險衍生工具基金（如 Z18/Z17），建議控制該類基金持倉比例不超過 20%。" if has_l3_l4 else "🟢 <b style='color:#059669;'>安全：</b> 組合內全數基金皆未包含 L3 (144A ELN) 高危否決級別衍生品，資產結構極度健康。"

    st.markdown(f"""
    <div class="advice-box">
        <h4 style="color:#1E3A8A; margin-bottom:10px;">📊 組合風險診斷結論 (加權平均風控得分: {avg_score:.1f} / 100)</h4>
        <ul style="color:#334155; font-size:14px; line-height:1.8;">
            <li><b>股債配置評價：</b> 當前組合股票比例為 <b>{overall_stock_pct}%</b>，債券比例為 <b>{overall_bond_pct}%</b>。{alloc_comment}</li>
            <li><b>衍生工具風險審計：</b> {deriv_comment}</li>
            <li><b>現金流與派息評估：</b> 組合加權平均年化派息率為 <b>{portfolio_yield_pct:.2f}%</b>，每月可提供 <b>${total_curr_monthly_div:,.0f}</b> 被動現金流收入。</li>
        </ul>
        <hr style="border-top: 1px dashed #CBD5E1; margin: 12px 0;">
        <h5 style="color:#0D9488; margin-bottom:6px;">🗣️ 建議對客戶銷售對白：</h5>
        <p style="color:#475569; font-size:13px; font-style:italic;">
            「張先生/小姐，為您量身配置的這個基金組合，加權平均派息率達到 <b>{portfolio_yield_pct:.2f}%</b>，每月能穩定帶來約 <b>${total_curr_monthly_div:,.0f}</b> 的現金流。在風險控制上，綜合風控得分高達 <b>{avg_score:.1f} 分</b>，股債比保持在 <b>{overall_stock_pct}:{overall_bond_pct}</b>，既能享有資本利得空間，又能透過每月現金派息對沖市場波動，非常符合您追求穩健高派息的理財目標。」
        </p>
    </div>
    """, unsafe_allow_html=True)
