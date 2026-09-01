# app.py
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from funds_loader import load_all_funds  # 從加載器動態加載
from utils.nav_calculator import calculate_realtime_nav_to_nav

# 0. 強制清除 Streamlit 快取，確保永遠抓取 GitHub 上最新的基金數據
st.cache_data.clear()
PRESET_FUNDS = load_all_funds()

# 1. 網頁頁面配置
st.set_page_config(
    page_title="智能基金風險評估系統", 
    page_icon="🛡️", 
    layout="wide"
)

# ==============================================================================
# 🔐 帳號與密碼認證系統
# ==============================================================================

USER_CREDENTIALS = {
    "admin": "888888",
    "user": "123456"
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def check_login(username, password):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.success("🎉 登入成功！正在載入系統...")
        st.rerun()
    else:
        st.error("❌ 帳號或密碼錯誤，請重新輸入！")

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.rerun()

if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; background-color: #1E222D; padding: 25px; border-radius: 12px; border-top: 5px solid #00E676;">
                <h2 style="color: #FFFFFF; margin-bottom: 5px;">🛡️ 智能基金風險評估系統</h2>
                <p style="color: #94A3B8; font-size: 14px;">請輸入授權帳號與密碼以進行存取</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            user_input = st.text_input("👤 帳號 (Username)：", placeholder="請輸入帳號")
            pass_input = st.text_input("🔑 密碼 (Password)：", type="password", placeholder="請輸入密碼")
            submit_button = st.form_submit_button("🚀 安全登入 (Login)", use_container_width=True)

            if submit_button:
                check_login(user_input, pass_input)

    st.stop()

# ==============================================================================
# 🎯 登入後的系統主要內容
# ==============================================================================

# 2. 注入自訂 CSS 樣式 (加寬 padding-top 解決頁首遮擋)
st.markdown("""
    <style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 2rem !important; }
    .main-title { font-size: 26px; font-weight: 800; color: #1E3A8A; margin-bottom: 15px; margin-top: 10px; }
    .fund-header { background-color: #1E222D; padding: 16px 22px; border-radius: 8px; border-left: 5px solid #00E676; margin-bottom: 15px; }
    .source-tag { background-color: #00E676; color: #000; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .type-tag { background-color: #E0E7FF; color: #3730A3; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-left: 8px; }
    .ms-star-tag { background-color: #FEF08A; color: #854D0E; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-left: 8px; }
    .yield-tag { background-color: #E0F2FE; color: #0369A1; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-left: 8px; }
    .metric-group-title { font-size: 15px; font-weight: 700; color: #1E3A8A; margin: 0; }
    .company-profile-list { font-size: 12px; color: #334155; margin: 0; padding-left: 18px; line-height: 1.6; }
    .data-disclaimer-note { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #059669; padding: 8px 14px; border-radius: 6px; font-size: 12px; color: #475569; margin-bottom: 20px; }
    .custom-table { width: 100%; border-collapse: collapse; background-color: #FFFFFF; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin-top: 10px; font-size: 13px; }
    .custom-table th { background-color: #1E3A8A; color: #FFFFFF; font-weight: 700; text-align: left; padding: 12px 14px; border-bottom: 2px solid #1E293B; white-space: nowrap; }
    .custom-table td { padding: 12px 14px; border-bottom: 1px solid #E2E8F0; vertical-align: middle; color: #334155; line-height: 1.6; text-align: left; }
    .custom-table tr:hover { background-color: #F8FAFC; }
    .quality-badge-green { background-color: #D1FAE5; color: #065F46; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; display: inline-block; text-align: center; }
    .quality-badge-yellow { background-color: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; display: inline-block; text-align: center; }
    .quality-badge-red { background-color: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; display: inline-block; text-align: center; }
    .badge-green { background-color: #D1FAE5; color: #065F46; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 12px; }
    .badge-yellow { background-color: #FEF3C7; color: #92400E; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 12px; }
    .badge-red { background-color: #FEE2E2; color: #991B1B; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 12px; }
    .summary-footer { background-color: #F1F5F9; padding: 14px 24px; border-radius: 0 0 8px 8px; display: flex; justify-content: flex-end; align-items: center; gap: 15px; border: 1px solid #E2E8F0; border-top: none; margin-top: -1px; margin-bottom: 25px; }
    .summary-title { font-size: 14px; font-weight: 700; color: #334155; }
    .summary-score { font-size: 18px; font-weight: 800; color: #1E3A8A; }
    
    /* 工具指引卡片專用 CSS */
    .deriv-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px; margin-bottom: 15px; border-left: 5px solid #1E3A8A; }
    .deriv-title { font-size: 16px; font-weight: 800; color: #1E3A8A; margin-bottom: 8px; }
    .deriv-tag-l1 { background-color: #D1FAE5; color: #065F46; font-size: 11px; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
    .deriv-tag-l2 { background-color: #FEF3C7; color: #92400E; font-size: 11px; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
    .deriv-tag-l3 { background-color: #FEE2E2; color: #991B1B; font-size: 11px; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
    .script-box { background-color: #F8FAFC; border: 1px dashed #CBD5E1; padding: 12px 15px; border-radius: 6px; font-size: 13px; color: #334155; margin-top: 10px; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# 頁首標題與登出按鈕
title_col, user_col = st.columns([3.5, 1])
with title_col:
    st.markdown('<div class="main-title">🛡️ 智能基金風險評估系統</div>', unsafe_allow_html=True)
with user_col:
    st.write(f"👤 已登入：**{st.session_state['username']}**")
    if st.button("🚪 安全登出", use_container_width=True):
        logout()

top_tab1, top_tab2, top_tab3 = st.tabs([
    "📊 跨基金總體風險比較表 (全基金縱覽)", 
    "🔍 單一基金深度風險剖析", 
    "📚 衍生工具解密與客戶對白指南"
])

# ==============================================================================
# TAB 1: 📊 全基金縱覽比較表
# ==============================================================================
with top_tab1:
    st.markdown("### 📊 跨基金 10 大風險維度得分與回報總覽表")

    filter_col1, filter_col2, filter_col3 = st.columns([1.5, 1.5, 1])
    with filter_col1:
        selected_category = st.selectbox("📌 請選擇風險評估類別：", ["全部類別", "債券基金", "股債混合基金", "股票基金"], index=0)

    matrix_data = []
    for key, f in PRESET_FUNDS.items():
        cat = f.get("category", "未分類")
        if selected_category != "全部類別" and cat != selected_category:
            continue
        
        score_val = float(f.get("score", 0))
        risk_deduction = 100.0 - score_val
        
        return_1y_val = float(f.get("return_1y", 0))
        if "history_div" in f and f["history_div"]:
            nav_calc = calculate_realtime_nav_to_nav(f["history_div"])
            if nav_calc.get("status") == "success":
                return_1y_val = nav_calc["nav_to_nav_return_pct"]

        eff_score = round((return_1y_val / (risk_deduction + 10.0)) * 100, 2)
        radar_scores = f.get("radar_scores", [0]*10)
        radar_dims = f.get("radar_dimensions", ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"])

        risk_deriv_info = f.get("risk_derivatives", {
            "display_html": "<span class='badge-green'>🟢 無 L3/L4 高風險產品 (0%)</span>"
        })

        matrix_data.append({
            "代號": f.get("code") or f.get("代號") or "N/A", 
            "基金簡稱": f.get("zh") or f.get("基金簡稱") or key, 
            "基金類別": cat,
            "高風險衍生品曝險": risk_deriv_info.get("display_html", "<span class='badge-green'>🟢 無 L3/L4 高風險產品 (0%)</span>"),
            "晨星評級": f.get("star", "未評級"), 
            "star_num": f.get("star_num", 0), 
            "上月年化派息率 (%)": f.get("last_yield", 0),
            "近1年總回報 (%)": return_1y_val, 
            "近3年年化總回報 (%)": f.get("return_3y", 0),
            "綜合風險總分": score_val, 
            "風險與回報對比指數": eff_score,
            "一、派息可持續性 (25)": radar_scores[0] if len(radar_scores) > 0 else 0, 
            "二、底層純資產質素 (15)": radar_scores[1] if len(radar_scores) > 1 else 0,
            "三、衍生工具與槓桿 (20)": radar_scores[2] if len(radar_scores) > 2 else 0, 
            "四、集中度風險 (5)": radar_scores[3] if len(radar_scores) > 3 else 0,
            "五、風險調整後回報 (10)": radar_scores[4] if len(radar_scores) > 4 else 0, 
            "六、大盤敏感度 (5)": radar_scores[5] if len(radar_scores) > 5 else 0,
            "七、流動性與規模 (5)": radar_scores[6] if len(radar_scores) > 6 else 0, 
            "八、匯率風險 (5)": radar_scores[7] if len(radar_scores) > 7 else 0,
            "九、區域集中度 (5)": radar_scores[8] if len(radar_scores) > 8 else 0, 
            "十、歷史相對波動 (5)": radar_scores[9] if len(radar_scores) > 9 else 0
        })
    
    df_matrix = pd.DataFrame(matrix_data)

    if len(df_matrix) == 0:
        st.warning(f"目前無屬於『{selected_category}』類別的預設基金。")
    else:
        with filter_col2:
            sort_by_col = st.selectbox("🔀 排序依據：", ["風險與回報對比指數", "近1年總回報 (%)", "近3年年化總回報 (%)", "上月年化派息率 (%)", "綜合風險總分"], index=0)
        with filter_col3:
            sort_order = st.radio("排序方向：", ["由高至低 (降序)", "由低至高 (升序)"], horizontal=True)

        ascending_flag = True if sort_order == "由低至高 (升序)" else False
        df_matrix_sorted = df_matrix.sort_values(sort_by_col, ascending=ascending_flag)

        rows_list = []
        for _, r in df_matrix_sorted.iterrows():
            b1 = "quality-badge-green" if r.get('一、派息可持續性 (25)', 0)>=12.5 else "quality-badge-red"
            b2 = "quality-badge-green" if r.get('二、底層純資產質素 (15)', 0)>=12.0 else "quality-badge-yellow"
            b3 = "quality-badge-green" if r.get('三、衍生工具與槓桿 (20)', 0)>=12.0 else "quality-badge-red"
            b4 = "quality-badge-green" if r.get('四、集中度風險 (5)', 0)>=5.0 else "quality-badge-yellow"
            b5 = "quality-badge-green" if r.get('五、風險調整後回報 (10)', 0)>=8.0 else "quality-badge-yellow"
            b6 = "quality-badge-green" if r.get('六、大盤敏感度 (5)', 0)>=4.0 else "quality-badge-yellow"
            b7 = "quality-badge-green" if r.get('七、流動性與規模 (5)', 0)>=5.0 else "quality-badge-yellow"
            b8 = "quality-badge-green" if r.get('八、匯率風險 (5)', 0)>=5.0 else "quality-badge-yellow"
            b9 = "quality-badge-green" if r.get('九、區域集中度 (5)', 0)>=5.0 else "quality-badge-yellow"
            b10 = "quality-badge-green" if r.get('十、歷史相對波動 (5)', 0)>=3.0 else "quality-badge-yellow"

            code_str = r.get('代號', '-')
            zh_str = r.get('基金簡稱', '-')
            cat_str = r.get('基金類別', '-')
            deriv_html = r.get('高風險衍生品曝險', '<span class="badge-green">🟢 無 L3/L4 高風險產品 (0%)</span>')
            yield_str = r.get('上月年化派息率 (%)', 0)
            r1_str = r.get('近1年總回報 (%)', 0)
            r3_str = r.get('近3年年化總回報 (%)', 0)
            star_str = r.get('晨星評級', '-')
            score_str = r.get('綜合風險總分', 0)
            eff_str = r.get('風險與回報對比指數', 0)

            rows_list.append(f"<tr><td><b>{code_str}</b></td><td><b>{zh_str}</b></td><td><span class='type-tag'>{cat_str}</span></td><td style='text-align:center;'>{deriv_html}</td><td><span class='yield-tag'>📈 {yield_str}%</span></td><td style='font-weight:bold; color:#059669;'>+{r1_str}%</td><td style='font-weight:bold; color:#0284C7;'>+{r3_str}%</td><td><span class='ms-star-tag'>{star_str}</span></td><td style='font-size:15px; font-weight:800; color:#1E3A8A;'>{score_str} / 100</td><td style='font-size:15px; font-weight:800; color:#059669;'><b>{eff_str}</b></td><td><span class='{b1}'>{r.get('一、派息可持續性 (25)', 0)} 分</span></td><td><span class='{b2}'>{r.get('二、底層純資產質素 (15)', 0)} 分</span></td><td><span class='{b3}'>{r.get('三、衍生工具與槓桿 (20)', 0)} 分</span></td><td><span class='{b4}'>{r.get('四、集中度風險 (5)', 0)} 分</span></td><td><span class='{b5}'>{r.get('五、風險調整後回報 (10)', 0)} 分</span></td><td><span class='{b6}'>{r.get('六、大盤敏感度 (5)', 0)} 分</span></td><td><span class='{b7}'>{r.get('七、流動性與規模 (5)', 0)} 分</span></td><td><span class='{b8}'>{r.get('八、匯率風險 (5)', 0)} 分</span></td><td><span class='{b9}'>{r.get('九、區域集中度 (5)', 0)} 分</span></td><td><span class='{b10}'>{r.get('十、歷史相對波動 (5)', 0)} 分</span></td></tr>")

        component_html = f"""
        <!DOCTYPE html><html><head><style>
        body {{ font-family: sans-serif; margin:0; background: transparent; }}
        .custom-table {{ width:100%; border-collapse:collapse; background:#FFF; border:1px solid #E2E8F0; font-size:13px; }}
        .custom-table th {{ background:#1E3A8A; color:#FFF; padding:12px 14px; text-align:left; white-space:nowrap; }}
        .custom-table td {{ padding:12px 14px; border-bottom:1px solid #E2E8F0; white-space:nowrap; }}
        .type-tag {{ background:#E0E7FF; color:#3730A3; padding:3px 8px; border-radius:4px; font-weight:bold; }}
        .badge-green {{ background:#D1FAE5; color:#065F46; padding:4px 10px; border-radius:4px; font-weight:700; font-size:12px; }}
        .badge-yellow {{ background:#FEF3C7; color:#92400E; padding:4px 10px; border-radius:4px; font-weight:700; font-size:12px; }}
        .badge-red {{ background:#FEE2E2; color:#991B1B; padding:4px 10px; border-radius:4px; font-weight:700; font-size:12px; }}
        .quality-badge-green {{ background:#D1FAE5; color:#065F46; padding:4px 10px; border-radius:4px; font-weight:700; }}
        .quality-badge-yellow {{ background:#FEF3C7; color:#92400E; padding:4px 10px; border-radius:4px; font-weight:700; }}
        .quality-badge-red {{ background:#FEE2E2; color:#991B1B; padding:4px 10px; border-radius:4px; font-weight:700; }}
        .ms-star-tag {{ background:#FEF08A; color:#854D0E; padding:3px 8px; border-radius:4px; font-weight:bold; }}
        .yield-tag {{ background:#E0F2FE; color:#0369A1; padding:3px 8px; border-radius:4px; font-weight:bold; }}
        </style></head><body><div style="overflow-x:auto;">
        <table class="custom-table" style="min-width:1850px;"><thead><tr><th>代號</th><th>基金名稱</th><th>類別</th><th style="background-color:#991B1B; color:#FFF; text-align:center;">高風險衍生品曝險 ⚠️</th><th>上月派息率</th><th>近1年回報 (NAV-to-NAV)</th><th>近3年年化</th><th>晨星</th><th>風險總分</th><th>風險與回報對比指數 🏆</th><th>一、派息可持續性 (25)</th><th>二、底層純資產質素 (15)</th><th>三、衍生工具與槓桿 (20)</th><th>四、集中度 (5)</th><th>五、風控與夏普 (10)</th><th>六、敏感度/Beta (5)</th><th>七、流動性 (5)</th><th>八、匯率風險 (5)</th><th>九、區域風險 (5)</th><th>十、淨值波動 (5)</th></tr></thead>
        <tbody>{"".join(rows_list)}</tbody></table></div></body></html>
        """
        components.html(component_html, height=380, scrolling=True)

        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_l, col_r = st.columns([1.3, 1])
        with col_l:
            st.markdown("#### 🕸️ 雷達圖多基金重疊對比")
            selected_compare = st.multiselect("請選擇要對比的基金：", list(PRESET_FUNDS.keys()), default=list(PRESET_FUNDS.keys())[:2])
            if selected_compare:
                radar_data = []
                for f_name in selected_compare:
                    f_obj = PRESET_FUNDS[f_name]
                    radar_scores = f_obj.get("radar_scores", [0]*10)
                    radar_dims = f_obj.get("radar_dimensions", ["維度"]*10)
                    code_val = f_obj.get("code") or f_obj.get("代號") or ""
                    zh_val = f_obj.get("zh") or f_obj.get("基金簡稱") or f_name
                    code_name = f"{code_val} {zh_val}"
                    for dim, score, m_score in zip(radar_dims, radar_scores, [25, 15, 20, 5, 10, 5, 5, 5, 5, 5]):
                        radar_data.append({"基金": code_name, "維度": dim, "得分率 (%)": (score / m_score) * 100})
                fig_radar = px.line_polar(pd.DataFrame(radar_data), r='得分率 (%)', theta='維度', color='基金', line_close=True, markers=True, range_r=[0, 100], template="plotly_dark")
                fig_radar.update_layout(height=450, paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_radar, use_container_width=True)

        with col_r:
            st.markdown("#### 🏆 風險與回報對比指數排行榜")
            fig_rank = px.bar(df_matrix.sort_values("風險與回報對比指數", ascending=True), x='風險與回報對比指數', y='代號', text='風險與回報對比指數', orientation='h', color='風險與回報對比指數', color_continuous_scale='Greens', template="plotly_white")
            fig_rank.update_layout(height=450)
            st.plotly_chart(fig_rank, use_container_width=True)

# ==============================================================================
# TAB 2: 🔍 單一基金深度風險剖析 (含空值容錯機制)
# ==============================================================================
with top_tab2:
    ctrl_col1, ctrl_col2 = st.columns([1.8, 1.2])
    with ctrl_col1: selected_preset = st.selectbox("📌 選擇基金名稱：", list(PRESET_FUNDS.keys()))
    curr_fund = PRESET_FUNDS[selected_preset]
    
    category_val = curr_fund.get("category", "債券基金")
    default_index = 1 if category_val == "股票基金" else 2 if category_val == "股債混合基金" else 0
    with ctrl_col2: fund_type = st.selectbox("📌 風險評估類別：", ["債券基金", "股票基金", "股債混合基金"], index=default_index)

    zh_name = curr_fund.get("zh") or curr_fund.get("基金簡稱") or selected_preset
    en_name = curr_fund.get("en", "")
    last_yield_val = curr_fund.get("last_yield", 0)
    star_val = curr_fund.get("star", "未評級")
    company_name = curr_fund.get("company_name", "未知機構")
    company_profile = curr_fund.get("company_profile", [])

    st.markdown(f'<div class="fund-header"><span class="source-tag">📍 {zh_name}</span> <span class="yield-tag">📈 派息率: {last_yield_val}%</span> <span class="ms-star-tag">⭐ {star_val}</span><br><span style="font-size:20px; font-weight:bold; color:#FFF;">{zh_name}</span> <span style="font-size:14px; color:#AAA;">({en_name})</span></div>', unsafe_allow_html=True)

    with st.expander(f"🏢 基金公司簡介 — {company_name}", expanded=False):
        st.markdown(f'<ul class="company-profile-list">{"".join([f"<li>{item}</li>" for item in company_profile])}</ul>', unsafe_allow_html=True)

    st.markdown('<div class="data-disclaimer-note"><b>📑 數據來源聲明備註：</b> 本 Dashboard 內所有財務數據、持倉比率、派息成分與營運損益，均完全依據<b>基金官方發布之基金月報 (Factsheet)、派息分派紀錄及年度財務報告</b> 客觀建檔分析。</div>', unsafe_allow_html=True)

    if "history_div" in curr_fund and curr_fund["history_div"]:
        nav_res = calculate_realtime_nav_to_nav(curr_fund["history_div"])
        if nav_res.get("status") == "success":
            st.markdown("### 🧮 最新 12 個月實時含息總回報精算 (NAV-to-NAV)")
            st.caption("💡 本區塊根據該基金最新發放的 12 個月派息與動態 NAV 自動精算，非半年前之舊歷史數據。")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(
                    label="🟢 最新 NAV-to-NAV 總回報 (股息再投資)",
                    value=f"{'+' if nav_res['nav_to_nav_return_pct'] > 0 else ''}{nav_res['nav_to_nav_return_pct']}%",
                    delta=f"持股單位滾存: 1,000 ➔ {nav_res['units_grown']} 單位"
                )
            with c2:
                st.metric(
                    label="🟡 最新實時純領現金總回報 (無再投資)",
                    value=f"{'+' if nav_res['cash_payout_return_pct'] > 0 else ''}{nav_res['cash_payout_return_pct']}%",
                    delta=f"現金利息收益: +{nav_res['simple_cash_yield_pct']}%"
                )
            with c3:
                st.metric(
                    label="📉 資本淨值 (NAV) 漲跌",
                    value=f"{nav_res['nav_capital_change_pct']}%",
                    delta=f"${nav_res['initial_nav']} ➔ ${nav_res['latest_nav']} 美元",
                    delta_color="inverse" if nav_res['nav_capital_change_pct'] < 0 else "normal"
                )
            
            st.info(f"""
            **🗣️ 理專白話解說對白：**
            * **每月領現金**：過去 12 個月落袋利息為 **+{nav_res['simple_cash_yield_pct']}%**，扣除淨值微幅波動後，純領現金實質總收益為 **+{nav_res['cash_payout_return_pct']}%**。
            * **股息再投資**：若選擇利息滾存，單位數自動增加了 **+{nav_res['units_added']} 單位**，最新實時總資產增長率高達 **+{nav_res['nav_to_nav_return_pct']}%**！
            """)
            st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    kpis = curr_fund.get('kpis', {})
    p2_delta = kpis.get('p2_delta', '⚠️ 存在本金補貼風險')
    p2_color = kpis.get('p2_color', 'inverse')
    p3_delta = kpis.get('p3_delta', '⚠️ 非投資級/風險持倉')
    p3_color = kpis.get('p3_color', 'inverse')
    p5_delta = kpis.get('p5_delta', '流動資產')
    p5_color = kpis.get('p5_color', 'normal')
    p9_delta = kpis.get('p9_delta', '🟢 總收入-總支出')
    p9_color = kpis.get('p9_color', 'normal')
    p10_delta = kpis.get('p10_delta', '🟢 淨收益覆蓋佳')
    p10_color = kpis.get('p10_color', 'normal')
    p11_delta = kpis.get('p11_delta', '⚠️ 申購 - 贖回差距')
    p11_color = kpis.get('p11_color', 'inverse')

    header_col1, eye_col1 = st.columns([4, 1])
    with header_col1: st.markdown('<div class="metric-group-title">📈 收益與回報指標 (Income & Total Return Metrics)</div>', unsafe_allow_html=True)
    with eye_col1: show_g1 = st.toggle("👁️ 顯示名片", value=True, key="eye_g1")
    
    display_1y_return = curr_fund.get('return_1y', 0)
    if "history_div" in curr_fund and curr_fund["history_div"]:
        nav_calc = calculate_realtime_nav_to_nav(curr_fund["history_div"])
        if nav_calc.get("status") == "success":
            display_1y_return = nav_calc["nav_to_nav_return_pct"]

    if show_g1:
        g1_c1, g1_c2, g1_c3, g1_c4, g1_c5, g1_c6 = st.columns(6)
        with g1_c1: st.metric(label="現時派息率", value=kpis.get('p1', '-'), delta="年化分派", delta_color="normal")
        with g1_c2: st.metric(label="派息與收益息差", value=kpis.get('p2', '-'), delta=p2_delta, delta_color=p2_color)
        with g1_c3: st.metric(label="過往 1 年總回報率", value=f"+{display_1y_return}%", delta="含股息再投資 (NAV-to-NAV)", delta_color="normal")
        with g1_c4: st.metric(label="過往 3 年年化總回報", value=f"+{curr_fund.get('return_3y', 0)}%", delta="晨星年化複合回報", delta_color="normal")
        with g1_c5: st.metric(label="過往一年總派息金額", value=kpis.get('p10', '-'), delta=p10_delta, delta_color=p10_color)
        with g1_c6: st.metric(label="過往一年淨收益/權利金", value=kpis.get('p9', '-'), delta=p9_delta, delta_color=p9_color)

    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    header_col2, eye_col2 = st.columns([4, 1])
    with header_col2: st.markdown('<div class="metric-group-title">🛡️ 風險與信用結構 (Risk & Credit Structure)</div>', unsafe_allow_html=True)
    with eye_col2: show_g2 = st.toggle("👁️ 顯示名片", value=True, key="eye_g2")

    if show_g2:
        g2_c1, g2_c2, g2_c3, g2_c4, g2_c5, g2_c6 = st.columns(6)
        with g2_c1: st.metric(label="平均持有評級/屬性", value=kpis.get('p3', '-'), delta=p3_delta, delta_color=p3_color)
        with g2_c2: st.metric(label="存續期/Beta敏感度", value=kpis.get('p4', '-'), delta="風險敏感指標", delta_color="normal")
        with g2_c3: st.metric(label="手持現金/衍生品比率", value=kpis.get('p5', '-'), delta=p5_delta, delta_color=p5_color)
        with g2_c4: st.metric(label="總持有資產數量", value=curr_fund.get('holdings_count', '-'), delta="底層持倉分散度", delta_color="normal")
        with g2_c5: st.metric(label="前十大發行人/持股佔比", value=kpis.get('p6', '-'), delta="集中度管控", delta_color="normal")
        with g2_c6: st.metric(label="槓桿比率", value=kpis.get('p7', '-'), delta="借貸/衍生品膨脹率", delta_color="normal")

    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    header_col3, eye_col3 = st.columns([4, 1])
    with header_col3: st.markdown('<div class="metric-group-title">💵 規模與資金流向 (Capital & AUM Flow)</div>', unsafe_allow_html=True)
    with eye_col3: show_g3 = st.toggle("👁️ 顯示名片", value=True, key="eye_g3")

    if show_g3:
        g3_c1, g3_c2 = st.columns(2)
        with g3_c1: st.metric(label="總基金資產值 (AUM)", value=kpis.get('p8', '-'), delta="百萬計價 (Million)", delta_color="normal")
        with g3_c2: st.metric(label="申購與贖回差距 (淨資金流向)", value=kpis.get('p11', '-'), delta=p11_delta, delta_color=p11_color)

    st.markdown("<br>", unsafe_allow_html=True)

    main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6, main_tab7 = st.tabs([
        "🕸️ 風險維度雷達圖", 
        "📋 底層資產清單 (Top 10)", 
        "📅 歷史派息紀錄", 
        "💰 派息組成 (收益 vs 資本)", 
        "🏭 十大行業分佈 (%)", 
        "🛡️ 評級/市值分佈 (%)", 
        "🌍 地區分佈歷年走勢 (%)"
    ])

    with main_tab1:
        radar_scores = curr_fund.get("radar_scores", [0]*10)
        radar_dims = curr_fund.get("radar_dimensions", ["維度"]*10)
        max_scores = [25, 15, 20, 5, 10, 5, 5, 5, 5, 5]
        
        df_chart = pd.DataFrame(dict(
            Score=[(s/m)*100 for s,m in zip(radar_scores, max_scores)], 
            RawScore=radar_scores,
            MaxScore=max_scores,
            Dimension=radar_dims
        ))
        fig = px.line_polar(df_chart, r='Score', theta='Dimension', line_close=True, markers=True, range_r=[0, 100], color_discrete_sequence=['#00E676'])
        fig.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.35)', line=dict(color='#00E676', width=2.5))
        fig.update_layout(height=480, margin=dict(l=60, r=60, t=30, b=30), paper_bgcolor="rgba(0,0,0,0)", polar=dict(bgcolor="#1E222D"))
        st.plotly_chart(fig, use_container_width=True)

    with main_tab2:
        top10_list = curr_fund.get("top10", [])
        if top10_list:
            top10_rows_html = "".join([f"<tr><td><b>{r.get('排名', '-')}</b></td><td><b>{r.get('持倉名稱', '-')}</b></td><td style='color:#475569;'>{r.get('bg','')}</td><td>{r.get('資產類別', '-')}</td><td style='font-weight:bold;'>{r.get('佔比 (%)', '-')}</td><td style='text-align:center;'>{r.get('badge', '-')}</td></tr>" for r in top10_list])
            st.markdown(f'<table class="custom-table"><thead><tr><th>排名</th><th>底層資產名稱</th><th>資產背景簡介</th><th>資產類別</th><th>佔比 (%)</th><th style="text-align:center;">品質評級</th></tr></thead><tbody>{top10_rows_html}</tbody></table>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ 官方 Factsheet 暫未提供此基金之 Top 10 詳細持倉清單。")

    # 🟢 修正 3：歷史派息紀錄 (加入空值檢查防不顯示)
    with main_tab3:
        h_div = curr_fund.get("history_div", [])
        if h_div:
            h_rows = "".join([f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td><b>{r[3]}</b></td><td>{r[4]}</td><td style='font-weight:bold; color:#059669;'>{r[5]}</td></tr>" for r in h_div])
            st.markdown(f'<table class="custom-table"><thead><tr><th>除息日</th><th>記錄日</th><th>派息日</th><th>每單位股息</th><th>除息日每單位資產淨值</th><th>年度化派息率</th></tr></thead><tbody>{h_rows}</tbody></table>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ 該基金非分派/派息類別，或官方分派正本暫無提供歷史派息紀錄數據。")

    # 🟢 修正 4：派息組成 (加入空值檢查防不顯示)
    with main_tab4:
        c_div = curr_fund.get("composition_div", [])
        if c_div:
            c_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td style='font-weight:bold; color:#D97706;'>{r[3]}</td></tr>" for r in c_div])
            st.markdown(f'<table class="custom-table"><thead><tr><th>除息日</th><th>每股股息</th><th>可分派淨收益/權利金 %</th><th>由資本所分派之股息 % (ROC)</th></tr></thead><tbody>{c_rows}</tbody></table>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ 官方派息成份報告 (Dividend Composition) 暫無提供此股份類別之分派來源拆解數據。")

    # 🟢 修正 5：十大行業分佈 (加入空值檢查防不顯示)
    with main_tab5:
        s_dist = curr_fund.get("sector_dist", [])
        if s_dist:
            s_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td style='font-weight:bold; color:#1E3A8A;'>{r[1]}</td></tr>" for r in s_dist])
            st.markdown(f'<table class="custom-table" style="width:50%;"><thead><tr><th>行業類別</th><th>佔市值 %</th></tr></thead><tbody>{s_rows}</tbody></table>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ 官方月報暫無提供此基金之行業分佈占比數據。")

    # 🟢 修正 6：評級/市值分佈 (加入空值檢查防不顯示)
    with main_tab6:
        r_dist = curr_fund.get("rating_dist", [])
        if r_dist:
            r_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td style='font-weight:bold; color:#1E3A8A;'>{r[1]}</td></tr>" for r in r_dist])
            st.markdown(f'<table class="custom-table" style="width:50%;"><thead><tr><th>信貸評級 / 市值分佈</th><th>佔市值 %</th></tr></thead><tbody>{r_rows}</tbody></table>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ 官方月報暫無提供此基金之評級/市值分佈占比數據。")

    # 🟢 修正 7：地區分佈歷年走勢 (加入空值檢查防不顯示)
    with main_tab7:
        geo_hist = curr_fund.get("geo_dist_history", [])
        if geo_hist:
            col_chart_geo, col_table_geo = st.columns([1.2, 1])
            df_geo = pd.DataFrame(geo_hist)
            with col_chart_geo:
                geo_y_cols = [c for c in df_geo.columns if c != '月份']
                fig_geo = px.bar(df_geo, x='月份', y=geo_y_cols, title="地區分佈歷史走勢 (%)", template="plotly_white")
                fig_geo.update_layout(height=380, barmode='stack', yaxis_title="佔比 (%)")
                st.plotly_chart(fig_geo, use_container_width=True)
            with col_table_geo:
                geo_cols = df_geo.columns.tolist()
                geo_header_html = "".join([f"<th>{c} %</th>" if c != '月份' else "<th>月份</th>" for c in geo_cols])
                geo_rows = "".join(["<tr>" + "".join([f"<td><b>{r[c]}</b></td>" if c == '月份' else f"<td>{r[c]}%</td>" for c in geo_cols]) + "</tr>" for _, r in df_geo.iterrows()])
                st.markdown(f'<table class="custom-table"><thead><tr>{geo_header_html}</tr></thead><tbody>{geo_rows}</tbody></table>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ 官方月報暫無提供此基金之地區歷史分佈走勢數據。")

    st.markdown("---")

    with st.expander("📋 點擊展開 / 折疊：基金深度風險評估明細表", expanded=True):
        eval_list = curr_fund.get("eval_table", [])
        
        eval_rows_html = ""
        for r in eval_list:
            dim_name = r[0] if len(r) > 0 else "-"
            metric_name = r[1] if len(r) > 1 else "-"
            rule_text = r[2] if len(r) > 2 else "-"
            fund_data_text = r[3] if len(r) > 3 else "-"
            score_text = r[4] if len(r) > 4 else "-"
            status_badge = r[5] if len(r) > 5 else "-"
            
            eval_rows_html += f"<tr><td><b>{dim_name}</b></td><td>{metric_name}</td><td>{rule_text}</td><td>{fund_data_text}</td><td style='text-align:center; font-weight:bold;'>{score_text}</td><td style='text-align:center;'>{status_badge}</td></tr>"

        score_val = curr_fund.get("score", "0")
        st.markdown(f'''
        <table class="custom-table">
            <thead>
                <tr>
                    <th style="width: 15%;">評估維度</th>
                    <th style="width: 18%;">具體檢查指標</th>
                    <th style="width: 24%;">專屬評分簡算規則</th>
                    <th style="width: 27%;">基金真實數據與解析</th>
                    <th style="width: 8%; text-align: center;">得分/滿分</th>
                    <th style="width: 8%; text-align: center;">風險狀態</th>
                </tr>
            </thead>
            <tbody>{eval_rows_html}</tbody>
        </table>
        <div class="summary-footer">
            <span class="summary-title">總得分 / 得分率：</span>
            <span class="summary-score">{score_val} / 100</span>
            <span class="quality-badge-green" style="font-size: 13px; padding: 5px 12px;">{score_val}% (健康度評估)</span>
        </div>
        ''', unsafe_allow_html=True)

# ==============================================================================
# TAB 3: 📚 衍生工具解密與客戶對白指南 (新增 TRS 詳細解說)
# ==============================================================================
with top_tab3:
    st.markdown("### 📚 基金衍生工具速查與理專話術寶典")
    st.caption("💡 本頁面將 Dashboard 中涉及的所有衍生工具進行白話解構，幫助您在面對客戶質疑或詢問時，能以最專業且易懂的方式應對。")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown("""
        <div style="background:#D1FAE5; padding:15px; border-radius:8px; border-left:5px solid #059669;">
            <b style="color:#065F46; font-size:15px;">🟢 L1 / L2 級：風險安全 / 可控工具</b><br>
            <span style="font-size:12px; color:#047857;">包含：交易所掛牌 Covered Call、外匯遠期對沖 (Forward FX)、公債期貨 (Futures)。<br><b>特徵：</b>無對手方違約風險，主要用於避險或鎖定權利金。</span>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown("""
        <div style="background:#FEF3C7; padding:15px; border-radius:8px; border-left:5px solid #D97706;">
            <b style="color:#92400E; font-size:15px;">🟡 L2 / L4 級：槓桿/資產調控工具</b><br>
            <span style="font-size:12px; color:#B45309;">包含：總回報掉期 (TRS)、信用違約掉期 (CDS)。<br><b>特徵：</b>具雙向對等性，受 Daily Margin 追繳機制保護，無爆倉毒藥。</span>
        </div>
        """, unsafe_allow_html=True)
    with col_t3:
        st.markdown("""
        <div style="background:#FEE2E2; padding:15px; border-radius:8px; border-left:5px solid #DC2626;">
            <b style="color:#991B1B; font-size:15px;">⚠️ L3 級：不對稱高風險毒藥 (剛性否決)</b><br>
            <span style="font-size:12px; color:#B91C1C;">包含：144A 私募股票掛鈎票據 (ELN)。<br><b>特徵：</b>收益封頂但下行承擔 100% 暴跌接股損失，且帶有投行倒閉風險！</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. Covered Call
    st.markdown("""
    <div class="deriv-card">
        <div class="deriv-title">1. Covered Call（覆蓋式看漲期權） <span class="deriv-tag-l2">L2 級：收益封頂型</span></div>
        <b>📍 代表基金：</b> Z03/Z07 (安聯收益成長)、Z04 (安聯環球高息)、Z51 (友邦股票入息)、Z17 (貝萊德高息)<br>
        <b>⚙️ 工具運作原理：</b> 基金經理人「手上有 100% 實體股票正股」，同時向市場賣出該股票的看漲期權 (Call Option)，向買家收取高額的「權利金 (Premium)」，並將權利金拿來補足基金派息。<br>
        <b>⚠️ 實質影響：</b> 股票下跌時，下行風險與普通股票 100% 相同；但當股票暴漲時，超過履約價的利潤會被買家拿走（資本利得封頂）。<br>
        <div class="script-box">
            <b>🗣️ 客戶詢問對白（理專話術）：</b><br>
            <i>「張先生/小姐，這檔基金能給到 8% 派息，是因為經理人採用了『租金增強策略 (Covered Call)』。就好比您買了一套豪宅（持有正股），平時收租金（股息），同時您跟租客簽合約，允許他未來以某個高價買走房子，並先收一筆大額訂金（權利金）。這種做法完全是在手上有房子的情況下進行，沒有借錢放大的槓桿，非常安全！」</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 144A ELN
    st.markdown("""
    <div class="deriv-card" style="border-left-color: #DC2626;">
        <div class="deriv-title" style="color: #991B1B;">2. 144A ELN（144A 私募股票掛鈎票據） <span class="deriv-tag-l3">L3 級：不對稱高危毒藥 (一票否決)</span></div>
        <b>📍 代表基金：</b> Z18 (富蘭克林入息)、Z77 (東方匯理收益機遇)<br>
        <b>⚙️ 工具運作原理：</b> 經理人向投行（如高盛、摩根大通）購買私規發行的結構性債券。實質上是把資金借給投行，同時向投行「賣出股票看跌期權 (Sell Put)」，靠承擔暴跌風險來換取高額利息。<br>
        <b>⚠️ 實質影響：</b> 上漲時只能領固定利息；但當連結的個股暴跌時，基金必須以高價「強行接手跌爆的股票」，承擔 100% 巨額虧損！且 144A 屬私募性質，資訊極度不透明，若投行倒閉則票據變廢紙。<br>
        <div class="script-box">
            <b>🗣️ 客戶詢問對白（理專話術）：</b><br>
            <i>「李太太，我們風控系統對這檔基金亮紅燈，是因為它持有超過 20% 的『144A ELN 結構商品』。這類產品就像是『賣保險給投行』，平時賺小利息，但萬一底層股票暴跌，基金就要承擔全部虧損。我們建議選擇像安聯 (Z03) 或惠理 (Z01) 這種資產純度更高、沒有這種私規爆點的基金。」</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. TRS (全新加入之總回報掉期專解)
    st.markdown("""
    <div class="deriv-card" style="border-left-color: #D97706;">
        <div class="deriv-title" style="color: #B45309;">3. TRS（Total Return Swap，總回報掉期） <span class="deriv-tag-l2">L4 級：合成資產與對沖調控</span></div>
        <b>📍 代表基金：</b> Z17 (貝萊德高息)、Z20 (施羅德動力收息)<br>
        <b>⚙️ 工具運作原理：</b> 基金不直接買賣實體股票/債券，而是與華爾街投行簽訂掉期合約。基金支付固定利息（如 SOFR 基準利率），換取投行手上某個資產組合（如美股指數或高息債）的「全部資本利得與股息總回報」。<br>
        <b>⚠️ 實質影響：</b> 屬「雙向對等工具」（漲 5% 賺 5%、跌 5% 虧 5%），絕非像 ELN 那樣不對稱爆價；且每天受國際 ISDA/CSA 協議監管，投行與基金每日清算補足現金保證金（Daily Margin Call），對手方違約風險極低。<br>
        <div class="script-box">
            <b>🗣️ 客戶詢問對白（理專話術）：</b><br>
            <i>「黃先生，這檔基金使用的 TRS（總回報掉期）是一種非常成熟的『合成配置工具』。就好比經理人想獲取某個指數的報酬，但他不需要大費周章在市場上買入幾百隻股票，而是直接跟投行做報酬交換。這屬於雙向對等的交易，漲跌跟實體股票一模一樣，而且每天都有現金保證金結算，沒有像 ELN 那種暴跌強行接股的毒藥條款，您可以完全放心。」</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Swaps & Futures
    st.markdown("""
    <div class="deriv-card" style="border-left-color: #D97706;">
        <div class="deriv-title" style="color: #B45309;">4. Futures & Forwards（國債/指數期貨與外匯遠期） <span class="deriv-tag-l1">L1 級：流動性與避險工具</span></div>
        <b>📍 代表基金：</b> Z06 (柏瑞動態配置)、Z05 (路博邁新興債)、Z33 (駿利亨德森平衡)<br>
        <b>⚙️ 工具運作原理：</b> 透過在公開交易所買賣國債或股票指數期貨（Futures），或與銀行鎖定遠期匯率（Forward FX），達到調整組合存續期（久期）或外匯避險之目的。<br>
        <b>⚠️ 實質影響：</b> 公開市場交易所擔保，無對手方違約風險，且用於降低匯率與利率波動，屬最健康的風控工具。<br>
        <div class="script-box">
            <b>🗣️ 客戶詢問對白（理專話術）：</b><br>
            <i>「陳先生，這檔混合型基金使用期貨與遠期外匯，主要是為了『幫您的資產保險』。比如當聯準會打算升息或市場波動時，經理人透過期貨快速鎖定收益，並對沖掉台幣或歐元對美元的匯率風險，讓您的投資不會被匯率波動吃掉。」</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. CoCos & Subordinated Debt
    st.markdown("""
    <div class="deriv-card" style="border-left-color: #059669;">
        <div class="deriv-title" style="color: #065F46;">5. CoCos & Subordinated Debt（應急可轉債 / 優先股 / 次級債） <span class="deriv-tag-l1">L1 / L2 級：金融次級資本</span></div>
        <b>📍 代表基金：</b> ZP4 (信安優先證券)、Z03/Z07 (安聯可轉債端)<br>
        <b>⚙️ 工具運作原理：</b> 由大型銀行或保險公司發行的次級資本工具（如 Additional Tier 1 債券）。清償順序低於普通國債，但高於普通股，因此能提供 6%~8% 的高到期收益率。<br>
        <b>⚠️ 實質影響：</b> 只有在銀行發生極端系統性危機（資本適足率低於法定門檻）時才會被強行轉股或減記；發行人皆為全球巨無霸金融機構。<br>
        <div class="script-box">
            <b>🗣️ 客戶詢問對白（理專話術）：</b><br>
            <i>「王總，這檔優先證券基金主要買的是像摩根大通、滙豐銀行發行的『優先資本債 (CoCos)』。簡單來說，銀行為了滿足政府的監管資本要求，願意支付比普通債券高出 2%~3% 的利息給我們。底層全是全球頂級銀行，安全性遠高於一般的企業高收益債！」</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 💡 理專快速銷售對照矩陣")
    
    matrix_guide = [
        {"客戶類型": "🛡️ 極度保守 / 討厭衍生品", "推薦基金": "Z01 惠理高息股票 / Z33 駿利亨德森平衡", "核心銷售話術": "100% 實體正股與美債，完全不碰期權或 ELN 結構商品，資產純度最高。"},
        {"客戶類型": "📈 追求高派息 (8%+) / 接受適度封頂", "推薦基金": "Z03 安聯收益成長 / Z04 安聯環球高息", "核心銷售話術": "採用交易所掛牌 Covered Call 租金增強，無私規投行違約風險，派息極度穩定。"},
        {"客戶類型": "💵 偏好純穩健債息 / 低波幅", "推薦基金": "Z05 路博邁新興債 / ZP4 信安優先證券", "核心銷售話術": "巨無霸級母基金規模，重倉主權債與歐美頂級銀行優先債，波幅極低。"},
        {"客戶類型": "⚠️ 需避開的風險產品", "警戒基金": "Z18 富蘭克林入息 / Z77 東方匯理收益機遇", "警示話術": "持有超過 20% 私募 144A ELN，下行承擔個股暴跌接股風險，已被風控系統熔斷。"}
    ]
    
    st.table(pd.DataFrame(matrix_guide))
