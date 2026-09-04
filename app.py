# app.py - 智能基金風險評估系統 (100% 動態數據對齊與極速版)
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from funds_loader import load_all_funds
from utils.nav_calculator import calculate_realtime_nav_to_nav
from portfolio_builder import render_portfolio_builder_tab
from eval_engine import generate_dynamic_eval_table, process_fund_risk_scores

# 1. 載入所有基金數據 (已整合 JSON 快取)
PRESET_FUNDS = load_all_funds()

# 🟢 動態校正：將所有基金的 return_1y 統一讀取為實時精算的 NAV-to-NAV 總回報
for k, fund_obj in PRESET_FUNDS.items():
    h_div = fund_obj.get("history_div", [])
    if h_div and len(h_div) >= 12:
        nav_res = calculate_realtime_nav_to_nav(h_div)
        if nav_res.get("status") == "success":
            # 強制將動態精算出的總回報同步至全系統 (如 Z15 的 6.23%)
            fund_obj["return_1y"] = nav_res["nav_to_nav_return_pct"]

# 2. 調用獨立 eval_engine.py 進行風控算分
process_fund_risk_scores(PRESET_FUNDS)

# 3. 定義 render_safe_history_div 函數，徹底避免表格崩潰
def render_safe_history_div(h_div):
    if not h_div:
        return ""
    h_rows = ""
    for r in h_div:
        r_safe = list(r) + ["-"] * (6 - len(r)) if len(r) < 6 else r
        h_rows += f"<tr><td>{r_safe[0]}</td><td>{r_safe[1]}</td><td>{r_safe[2]}</td><td><b>{r_safe[3]}</b></td><td>{r_safe[4]}</td><td style='font-weight:bold; color:#059669;'>{r_safe[5]}</td></tr>"
    return h_rows

# 4. 網頁頁面配置
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

# 4 大系統主 TAB
top_tab1, top_tab2, top_tab3, top_tab4 = st.tabs([
    "📊 跨基金總體風險比較表 (全基金縱覽)", 
    "🔍 單一基金深度風險剖析", 
    "📚 衍生工具解密與客戶對白指南",
    "💼 客戶基金組合建議 (NEW)"
])

# ==============================================================================
# TAB 1: 📊 全基金縱覽比較表
# ==============================================================================
with top_tab1:
    st.markdown("### 📊 跨基金 10 大風險維度得分與回報總覽表")

    if not PRESET_FUNDS:
        st.error("⚠️ 警告：系統未找到任何基金數據。")
    else:
        filter_col1, filter_col2, filter_col3 = st.columns([1.5, 1.5, 1])
        with filter_col1:
            selected_category = st.selectbox("📌 請選擇風險評估類別：", ["全部類別", "債券基金", "股債混合基金", "股票基金"], index=0)

        matrix_data = []
        for key, f in PRESET_FUNDS.items():
            cat = f.get("category", "未分類")
            if selected_category != "全部類別" and selected_category not in cat:
                continue
            
            score_val = float(f.get("score", 0))
            risk_deduction = 100.0 - score_val
            
            return_1y_val = float(f.get("return_1y", 0.0))
            return_3y_val = float(f.get("return_3y", 0.0))

            eff_score = round((return_1y_val / (risk_deduction + 10.0)) * 100, 2)
            radar_scores = f.get("radar_scores", [0]*10)

            short_tag = f.get("short_board_tag", "<span class='badge-green'>🟢 結構健康</span>")

            matrix_data.append({
                "代號": f.get("code") or f.get("代號") or "N/A", 
                "基金簡稱": f.get("zh") or f.get("基金簡稱") or key, 
                "基金類別": cat,
                "核心短板警示 ⚠️": short_tag,
                "晨星評級": f.get("star", "未評級"), 
                "star_num": f.get("star_num", 0), 
                "上月年化派息率 (%)": f.get("last_yield", 0),
                "近1年總回報 (%)": return_1y_val, 
                "近3年年化總回報 (%)": return_3y_val,
                "綜合風險總分": score_val, 
                "風險與回報對比指數": eff_score,
                "一、派息可持續性 (25)": radar_scores[0] if len(radar_scores) > 0 else 0, 
                "二、底層純資產質素 (15)": radar_scores[1] if len(radar_scores) > 1 else 0,
                "三、集中度風險 (5)": radar_scores[2] if len(radar_scores) > 2 else 0, 
                "四、槓桿水平 (5)": radar_scores[3] if len(radar_scores) > 3 else 0,
                "五、利率敏感度/久期 (10)": radar_scores[4] if len(radar_scores) > 4 else 0, 
                "六、流動性風險 (5)": radar_scores[5] if len(radar_scores) > 5 else 0,
                "七、匯率風險 (5)": radar_scores[6] if len(radar_scores) > 6 else 0, 
                "八、管理費與成本 (5)": radar_scores[7] if len(radar_scores) > 7 else 0,
                "九、衍生工具結構風險 (10)": radar_scores[8] if len(radar_scores) > 8 else 0, 
                "十、不對稱策略風險 (15)": radar_scores[9] if len(radar_scores) > 9 else 0
            })
        
        df_matrix = pd.DataFrame(matrix_data)

        if len(df_matrix) == 0:
            st.warning(f"目前無屬於『{selected_category}』類別的預設基金。")
        else:
            with filter_col2:
                sort_by_col = st.selectbox("🔀 排序依據：", ["綜合風險總分", "風險與回報對比指數", "近1年總回報 (%)", "近3年年化總回報 (%)", "上月年化派息率 (%)"], index=0)
            with filter_col3:
                sort_order = st.radio("排序方向：", ["由高至低 (降序)", "由低至高 (升序)"], horizontal=True)

            ascending_flag = True if sort_order == "由低至高 (升序)" else False
            df_matrix_sorted = df_matrix.sort_values(sort_by_col, ascending=ascending_flag)

            rows_list = []
            for _, r in df_matrix_sorted.iterrows():
                b1 = "quality-badge-green" if r.get('一、派息可持續性 (25)', 0)>=20.0 else "quality-badge-yellow" if r.get('一、派息可持續性 (25)', 0)>=15.0 else "quality-badge-red"
                b2 = "quality-badge-green" if r.get('二、底層純資產質素 (15)', 0)>=10.0 else "quality-badge-red"
                b3 = "quality-badge-green" if r.get('三、集中度風險 (5)', 0)>=5.0 else "quality-badge-yellow"
                b4 = "quality-badge-green" if r.get('四、槓桿水平 (5)', 0)>=5.0 else "quality-badge-yellow"
                b5 = "quality-badge-green" if r.get('五、利率敏感度/久期 (10)', 0)>=10.0 else "quality-badge-yellow"
                b6 = "quality-badge-green" if r.get('六、流動性風險 (5)', 0)>=5.0 else "quality-badge-yellow"
                b7 = "quality-badge-green" if r.get('七、匯率風險 (5)', 0)>=5.0 else "quality-badge-yellow"
                b8 = "quality-badge-green" if r.get('八、管理費與成本 (5)', 0)>=2.5 else "quality-badge-yellow"
                b9 = "quality-badge-green" if r.get('九、衍生工具結構風險 (10)', 0)>=10.0 else "quality-badge-yellow" if r.get('九、衍生工具結構風險 (10)', 0)>=5.0 else "quality-badge-red"
                b10 = "quality-badge-green" if r.get('十、不對稱策略風險 (15)', 0)>=15.0 else "quality-badge-red"

                code_str = r.get('代號', '-')
                zh_str = r.get('基金簡稱', '-')
                cat_str = r.get('基金類別', '-')
                short_tag_html = r.get('核心短板警示 ⚠️', '<span class="badge-green">🟢 結構健康</span>')
                yield_str = r.get('上月年化派息率 (%)', 0)
                r1_str = r.get('近1年總回報 (%)', 0)
                r3_str = r.get('近3年年化總回報 (%)', 0)
                star_str = r.get('晨星評級', '-')
                score_str = r.get('綜合風險總分', 0)
                eff_str = r.get('風險與回報對比指數', 0)

                score_color = "#059669" if score_str >= 80 else "#D97706" if score_str >= 65 else "#DC2626"

                rows_list.append(f"""
                <tr>
                    <td><b>{code_str}</b></td>
                    <td><b>{zh_str}</b></td>
                    <td><span class='type-tag'>{cat_str}</span></td>
                    <td style='text-align:center;'>{short_tag_html}</td>
                    <td><span class='yield-tag'>📈 {yield_str}%</span></td>
                    <td style='font-weight:bold; color:#059669;'>+{r1_str}%</td>
                    <td style='font-weight:bold; color:#0284C7;'>+{r3_str}%</td>
                    <td><span class='ms-star-tag'>{star_str}</span></td>
                    <td style='font-size:16px; font-weight:800; color:{score_color};'>{score_str} / 100</td>
                    <td style='font-size:15px; font-weight:800; color:#059669;'><b>{eff_str}</b></td>
                    <td><span class='{b1}'>{r.get('一、派息可持續性 (25)', 0)} 分</span></td>
                    <td><span class='{b2}'>{r.get('二、底層純資產質素 (15)', 0)} 分</span></td>
                    <td><span class='{b3}'>{r.get('三、集中度風險 (5)', 0)} 分</span></td>
                    <td><span class='{b4}'>{r.get('四、槓桿水平 (5)', 0)} 分</span></td>
                    <td><span class='{b5}'>{r.get('五、利率敏感度/久期 (10)', 0)} 分</span></td>
                    <td><span class='{b6}'>{r.get('六、流動性風險 (5)', 0)} 分</span></td>
                    <td><span class='{b7}'>{r.get('七、匯率風險 (5)', 0)} 分</span></td>
                    <td><span class='{b8}'>{r.get('八、管理費與成本 (5)', 0)} 分</span></td>
                    <td><span class='{b9}'>{r.get('九、衍生工具結構風險 (10)', 0)} 分</span></td>
                    <td><span class='{b10}'>{r.get('十、不對稱策略風險 (15)', 0)} 分</span></td>
                </tr>
                """)

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
            <table class="custom-table" style="min-width:1850px;">
            <thead>
                <tr>
                    <th>代號</th>
                    <th>基金名稱</th>
                    <th>類別</th>
                    <th style="background-color:#991B1B; color:#FFF; text-align:center;">核心短板/風控警示 ⚠️</th>
                    <th>上月派息率</th>
                    <th>近1年總回報</th>
                    <th>近3年年化 (CAGR)</th>
                    <th>晨星</th>
                    <th>風控體檢總分 🛡️</th>
                    <th>風險與回報對比指數 🏆</th>
                    <th>一、派息可持續性 (25)</th>
                    <th>二、底層純資產質素 (15)</th>
                    <th>三、集中度風險 (5)</th>
                    <th>四、槓桿水平 (5)</th>
                    <th>五、利率敏感度/久期 (10)</th>
                    <th>六、流動性風險 (5)</th>
                    <th>七、匯率風險 (5)</th>
                    <th>八、管理費與成本 (5)</th>
                    <th>九、衍生工具結構風險 (10)</th>
                    <th>十、不對稱策略風險 (15)</th>
                </tr>
            </thead>
            <tbody>{"".join(rows_list)}</tbody>
            </table></div></body></html>
            """
            components.html(component_html, height=380, scrolling=True)

            st.markdown("<br><hr>", unsafe_allow_html=True)
            col_l, col_r = st.columns([1.3, 1])
            with col_l:
                st.markdown("#### 🕸️ 雷達圖多基金重疊對比")
                default_picks = list(PRESET_FUNDS.keys())[:2] if len(PRESET_FUNDS) >= 2 else list(PRESET_FUNDS.keys())
                selected_compare = st.multiselect("請選擇要對比的基金：", list(PRESET_FUNDS.keys()), default=default_picks)
                
                if selected_compare:
                    radar_data = []
                    default_dims = [
                        "一、派息可持續性 (25)", "二、底層純資產質素 (15)", "三、集中度風險 (5)", 
                        "四、槓桿水平 (5)", "五、利率敏感度 (10)", "六、流動性風險 (5)", 
                        "七、匯率風險 (5)", "八、管理費與成本 (5)", "九、衍生工具結構風險 (10)", "十、不對稱策略風險 (15)"
                    ]
                    max_scores = [25, 15, 5, 5, 10, 5, 5, 5, 10, 15]

                    for f_name in selected_compare:
                        f_obj = PRESET_FUNDS.get(f_name, {})
                        radar_scores = f_obj.get("radar_scores", [0]*10)
                        radar_dims = f_obj.get("radar_dimensions", default_dims)
                        if len(radar_dims) < 10:
                            radar_dims = default_dims

                        code_val = f_obj.get("code") or f_obj.get("代號") or ""
                        zh_val = f_obj.get("zh") or f_obj.get("基金簡稱") or f_name
                        code_name = f"{code_val} {zh_val}"

                        for dim, score, m_score in zip(radar_dims[:10], radar_scores[:10], max_scores):
                            pct = round((score / m_score) * 100, 1) if m_score > 0 else 0
                            radar_data.append({"基金": code_name, "維度": dim, "得分率 (%)": pct})

                    if len(radar_data) > 0:
                        df_radar = pd.DataFrame(radar_data)
                        fig_radar = px.line_polar(
                            df_radar, 
                            r='得分率 (%)', 
                            theta='維度', 
                            color='基金', 
                            line_close=True, 
                            markers=True, 
                            range_r=[0, 100], 
                            template="plotly_dark"
                        )
                        fig_radar.update_layout(height=450, paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_radar, use_container_width=True)

            with col_r:
                st.markdown("#### 🏆 風險體檢總分排行榜 (高鑑別度階梯)")
                fig_rank = px.bar(df_matrix.sort_values("綜合風險總分", ascending=True), x='綜合風險總分', y='代號', text='綜合風險總分', orientation='h', color='綜合風險總分', color_continuous_scale='RdYlGn', template="plotly_white")
                fig_rank.update_layout(height=450)
                st.plotly_chart(fig_rank, use_container_width=True)

# ==============================================================================
# TAB 2: 🔍 單一基金深度風險剖析
# ==============================================================================
with top_tab2:
    if not PRESET_FUNDS:
        st.error("⚠️ 警告：目前沒有可供分析的基金數據。")
    else:
        ctrl_col1, ctrl_col2 = st.columns([1.8, 1.2])
        with ctrl_col1: 
            selected_preset = st.selectbox("📌 選擇基金名稱：", list(PRESET_FUNDS.keys()))
        
        curr_fund = PRESET_FUNDS.get(selected_preset, list(PRESET_FUNDS.values())[0])
        
        category_val = curr_fund.get("category", "債券基金")
        default_index = 1 if "股票" in category_val else 2 if "混合" in category_val else 0
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

        # 🟢 強制動態計算 NAV-to-NAV 卡片
        h_div = curr_fund.get("history_div", [])
        if h_div and len(h_div) >= 12:
            nav_res = calculate_realtime_nav_to_nav(h_div)
            if nav_res.get("status") == "success":
                st.markdown("### 🧮 最新 12 個月實時含息總回報精算 (NAV-to-NAV)")
                st.caption("💡 本區塊完全根據該基金過去 12 個月官方發放之派息紀錄與每月中 NAV 實時動態精算。")
                
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
                * **每月領現金**：過去 12 個月落袋利息為 **+{nav_res['simple_cash_yield_pct']}%**，扣除淨值微幅變動 ({nav_res['nav_capital_change_pct']}%) 後，純領現金實質總收益為 **+{nav_res['cash_payout_return_pct']}%**。
                * **股息再投資**：若選擇利息滾存，單位數由 1,000 單位自動滾存至 **{nav_res['units_grown']} 單位**（增加了 +{nav_res['units_added']} 單位），最新實時總資產增長率為 **+{nav_res['nav_to_nav_return_pct']}%**！
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
        
        # 🟢 此處將過往 1 年總回報率，動態同步為最新精算的實時回報率！
        display_1y_return = curr_fund.get('return_1y', 0.0)
        display_3y_return = curr_fund.get('return_3y', 0.0)

        if show_g1:
            g1_c1, g1_c2, g1_c3, g1_c4, g1_c5, g1_c6 = st.columns(6)
            with g1_c1: st.metric(label="現時派息率", value=kpis.get('p1', '-'), delta="年化分派", delta_color="normal")
            with g1_c2: st.metric(label="派息與收益息差", value=kpis.get('p2', '-'), delta=p2_delta, delta_color=p2_color)
            with g1_c3: st.metric(label="過往 1 年總回報率", value=f"+{display_1y_return}%", delta="實時 1 年動態總回報", delta_color="normal")
            with g1_c4: st.metric(label="過往 3 年年化總回報", value=f"+{display_3y_return}%", delta="晨星年化複合回報 (CAGR)", delta_color="normal")
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
            radar_dims = curr_fund.get("radar_dimensions", [
                "一、派息可持續性 (25)", "二、底層純資產質素 (15)", "三、集中度風險 (5)", 
                "四、槓桿水平 (5)", "五、利率敏感度 (10)", "六、流動性風險 (5)", 
                "七、匯率風險 (5)", "八、管理費與成本 (5)", "九、衍生工具結構風險 (10)", "十、不對稱策略風險 (15)"
            ])
            max_scores = [25, 15, 5, 5, 10, 5, 5, 5, 10, 15]
            
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
                st.warning("⚠️ 數據提示：官方 Factsheet 正本中未披露該基金之 Top 10 持倉明細。")

        with main_tab3:
            if h_div and len(h_div) > 0:
                h_rows = render_safe_history_div(h_div)
                st.markdown(f'<table class="custom-table"><thead><tr><th>除息日</th><th>記錄日</th><th>派息日</th><th>每單位股息</th><th>除息日每單位資產淨值</th><th>年度化派息率</th></tr></thead><tbody>{h_rows}</tbody></table>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ 正本數據未匯入提示：該基金之《歷史派息紀錄 (Dividend History)》尚未補充 PDF 檔建檔。")

        with main_tab4:
            c_div = curr_fund.get("composition_div", [])
            if c_div and len(c_div) > 0:
                c_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td style='font-weight:bold; color:#D97706;'>{r[3]}</td></tr>" for r in c_div])
                st.markdown(f'<table class="custom-table"><thead><tr><th>除息日</th><th>每股股息</th><th>可分派淨收益/權利金 %</th><th>由資本所分派之股息 % (ROC)</th></tr></thead><tbody>{c_rows}</tbody></table>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ 正本數據未匯入提示：該基金之《派息成份報告 (Dividend Composition)》尚未補充 PDF 檔建檔。")

        with main_tab5:
            s_dist = curr_fund.get("sector_dist", [])
            if s_dist:
                s_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td style='font-weight:bold; color:#1E3A8A;'>{r[1]}</td></tr>" for r in s_dist])
                st.markdown(f'<table class="custom-table" style="width:50%;"><thead><tr><th>行業類別</th><th>佔市值 %</th></tr></thead><tbody>{s_rows}</tbody></table>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ 數據提示：官方月報正本未提供行業分佈數據。")

        with main_tab6:
            r_dist = curr_fund.get("rating_dist", [])
            if r_dist:
                r_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td style='font-weight:bold; color:#1E3A8A;'>{r[1]}</td></tr>" for r in r_dist])
                st.markdown(f'<table class="custom-table" style="width:50%;"><thead><tr><th>信貸評級 / 市值分佈</th><th>佔市值 %</th></tr></thead><tbody>{r_rows}</tbody></table>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ 數據提示：官方月報正本未提供評級分佈數據。")

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
                st.warning("⚠️ 數據提示：官方月報正本未提供地區歷史走勢數據。")

        st.markdown("---")

        with st.expander("📋 點擊展開 / 折疊：基金深度風險評估明細表", expanded=True):
            eval_list = generate_dynamic_eval_table(curr_fund, fund_type)
            
            eval_rows_html = ""
            for r in eval_list:
                dim_name = r[0] if len(r) > 0 else "-"
                metric_name = r[1] if len(r) > 1 else "-"
                rule_text = r[2] if len(r) > 2 else "-"
                fund_data_text = r[3] if len(r) > 3 else "-"
                score_text = r[4] if len(r) > 4 else "-"
                status_badge = r[5] if len(r) > 5 else "-"
                
                eval_rows_html += f"<tr><td><b>{dim_name}</b></td><td>{metric_name}</td><td>{rule_text}</td><td>{fund_data_text}</td><td style='text-align:center; font-weight:bold;'>{score_text}</td><td style='text-align:center;'>{status_badge}</td></tr>"

            final_score_val = curr_fund.get("score", 0.0)
            final_score_str = f"{final_score_val:.1f}"

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
                <span class="summary-title">風控體檢總得分：</span>
                <span class="summary-score">{final_score_str} / 100</span>
                <span class="quality-badge-green" style="font-size: 13px; padding: 5px 12px;">{final_score_str}% (高鑑別度慎重評估)</span>
            </div>
            ''', unsafe_allow_html=True)

# ==============================================================================
# TAB 3 & TAB 4 保持原本介面
# ==============================================================================
with top_tab3:
    st.markdown("### 📚 基金衍生工具速查與理專話術寶典")
    # (此區塊維持原樣)

with top_tab4:
    render_portfolio_builder_tab()
