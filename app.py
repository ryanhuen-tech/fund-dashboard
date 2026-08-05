# app.py
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from funds_loader import PRESET_FUNDS # 從加載器自動動態匯入所有基金

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

        st.info("💡 預設測試帳號：`admin` | 預設密碼：`888888`")
    st.stop()

# ==============================================================================
# 🎯 登入後的系統主要內容
# ==============================================================================

# 2. 注入自訂 CSS 樣式
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
    .main-title { font-size: 26px; font-weight: 800; color: #1E3A8A; margin-bottom: 15px; }
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
    .custom-table td { padding: 12px 14px; border-bottom: 1px solid #E2E8F0; vertical-align: middle; color: #334155; line-height: 1.6; text-align: left; white-space: nowrap; }
    .custom-table tr:hover { background-color: #F8FAFC; }
    .quality-badge-green { background-color: #D1FAE5; color: #065F46; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; display: inline-block; text-align: center; }
    .quality-badge-yellow { background-color: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; display: inline-block; text-align: center; }
    .quality-badge-red { background-color: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; display: inline-block; text-align: center; }
    .summary-footer { background-color: #F1F5F9; padding: 14px 24px; border-radius: 0 0 8px 8px; display: flex; justify-content: flex-end; align-items: center; gap: 15px; border: 1px solid #E2E8F0; border-top: none; margin-top: -1px; margin-bottom: 25px; }
    .summary-title { font-size: 14px; font-weight: 700; color: #334155; }
    .summary-score { font-size: 18px; font-weight: 800; color: #1E3A8A; }
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

top_tab1, top_tab2 = st.tabs(["📊 跨基金總體風險比較表 (全基金縱覽)", "🔍 單一基金深度風險剖析"])

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
        if selected_category != "全部類別" and f["category"] != selected_category:
            continue
        score_val = float(f["score"])
        risk_deduction = 100.0 - score_val
        return_1y_val = f["return_1y"]
        eff_score = round((return_1y_val / (risk_deduction + 10.0)) * 100, 2)

        matrix_data.append({
            "代號": f["code"], "基金簡稱": f["zh"], "基金類別": f["category"],
            "晨星評級": f["star"], "star_num": f["star_num"], "上月年化派息率 (%)": f["last_yield"],
            "近1年總回報 (%)": return_1y_val, "近3年年化總回報 (%)": f["return_3y"],
            "綜合風險總分": score_val, "風險與回報對比指數": eff_score,
            "一、派息可持續性 (20)": f["radar_scores"][0], "二、底層質素 (15)": f["radar_scores"][1],
            "三、集中度 (5)": f["radar_scores"][2], "四、信用與風控 (10)": f["radar_scores"][3],
            "五、槓桿與天花板 (10)": f["radar_scores"][4], "六、利率/大盤敏感度 (10)": f["radar_scores"][5],
            "七、流動性 (10)": f["radar_scores"][6], "八、匯率風險 (10)": f["radar_scores"][7],
            "九、區域風險 (5)": f["radar_scores"][8], "十、淨值波動與回撤 (5)": f["radar_scores"][9]
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
            b1 = "quality-badge-green" if r['一、派息可持續性 (20)']>=15 else "quality-badge-yellow"
            b2 = "quality-badge-green" if r['二、底層質素 (15)']>=15 else "quality-badge-yellow"
            b3 = "quality-badge-green" if r['三、集中度 (5)']>=5 else "quality-badge-yellow"
            b4 = "quality-badge-green" if r['四、信用與風控 (10)']>=10 else "quality-badge-yellow"
            b5 = "quality-badge-green" if r['五、槓桿與天花板 (10)']>=10 else "quality-badge-yellow"
            b6 = "quality-badge-green" if r['六、利率/大盤敏感度 (10)']>=10 else "quality-badge-yellow"
            b7 = "quality-badge-green" if r['七、流動性 (10)']>=10 else "quality-badge-yellow"
            b8 = "quality-badge-green" if r['八、匯率風險 (10)']>=10 else "quality-badge-yellow"
            b9 = "quality-badge-green" if r['九、區域風險 (5)']>=5 else "quality-badge-yellow"
            b10 = "quality-badge-green" if r['十、淨值波動與回撤 (5)']>=5 else "quality-badge-yellow"

            rows_list.append(f"<tr><td><b>{r['代號']}</b></td><td><b>{r['基金簡稱']}</b></td><td><span class='type-tag'>{r['基金類別']}</span></td><td><span class='yield-tag'>📈 {r['上月年化派息率 (%)']}%</span></td><td style='font-weight:bold; color:#059669;'>+{r['近1年總回報 (%)']}%</td><td style='font-weight:bold; color:#0284C7;'>+{r['近3年年化總回報 (%)']}%</td><td><span class='ms-star-tag'>{r['晨星評級']}</span></td><td style='font-size:15px; font-weight:800; color:#1E3A8A;'>{r['綜合風險總分']} / 100</td><td style='font-size:15px; font-weight:800; color:#059669;'><b>{r['風險與回報對比指數']}</b></td><td><span class='{b1}'>{r['一、派息可持續性 (20)']} 分</span></td><td><span class='{b2}'>{r['二、底層質素 (15)']} 分</span></td><td><span class='{b3}'>{r['三、集中度 (5)']} 分</span></td><td><span class='{b4}'>{r['四、信用與風控 (10)']} 分</span></td><td><span class='{b5}'>{r['五、槓桿與天花板 (10)']} 分</span></td><td><span class='{b6}'>{r['六、利率/大盤敏感度 (10)']} 分</span></td><td><span class='{b7}'>{r['七、流動性 (10)']} 分</span></td><td><span class='{b8}'>{r['八、匯率風險 (10)']} 分</span></td><td><span class='{b9}'>{r['九、區域風險 (5)']} 分</span></td><td><span class='{b10}'>{r['十、淨值波動與回撤 (5)']} 分</span></td></tr>")

        component_html = f"""
        <!DOCTYPE html><html><head><style>
        body {{ font-family: sans-serif; margin:0; background: transparent; }}
        .custom-table {{ width:100%; border-collapse:collapse; background:#FFF; border:1px solid #E2E8F0; font-size:13px; }}
        .custom-table th {{ background:#1E3A8A; color:#FFF; padding:12px 14px; text-align:left; white-space:nowrap; }}
        .custom-table td {{ padding:12px 14px; border-bottom:1px solid #E2E8F0; white-space:nowrap; }}
        .type-tag {{ background:#E0E7FF; color:#3730A3; padding:3px 8px; border-radius:4px; font-weight:bold; }}
        .quality-badge-green {{ background:#D1FAE5; color:#065F46; padding:4px 10px; border-radius:4px; font-weight:700; }}
        .quality-badge-yellow {{ background:#FEF3C7; color:#92400E; padding:4px 10px; border-radius:4px; font-weight:700; }}
        .ms-star-tag {{ background:#FEF08A; color:#854D0E; padding:3px 8px; border-radius:4px; font-weight:bold; }}
        .yield-tag {{ background:#E0F2FE; color:#0369A1; padding:3px 8px; border-radius:4px; font-weight:bold; }}
        </style></head><body><div style="overflow-x:auto;">
        <table class="custom-table" style="min-width:1650px;"><thead><tr><th>代號</th><th>基金名稱</th><th>類別</th><th>上月派息率</th><th>近1年回報</th><th>近3年年化</th><th>晨星</th><th>風險總分</th><th>風險與回報對比指數 🏆</th><th>一、派息可持續性</th><th>二、底層質素</th><th>三、集中度</th><th>四、信用/風控</th><th>五、槓桿/天花板</th><th>六、敏感度/Beta</th><th>七、流動性</th><th>八、匯率風險</th><th>九、區域風險</th><th>十、淨值波動</th></tr></thead>
        <tbody>{"".join(rows_list)}</tbody></table></div></body></html>
        """
        components.html(component_html, height=360, scrolling=True)

        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_l, col_r = st.columns([1.3, 1])
        with col_l:
            st.markdown("#### 🕸️ 雷達圖多基金重疊對比")
            selected_compare = st.multiselect("請選擇要對比的基金：", list(PRESET_FUNDS.keys()), default=list(PRESET_FUNDS.keys())[:2])
            if selected_compare:
                radar_data = []
                for f_name in selected_compare:
                    f_obj = PRESET_FUNDS[f_name]
                    for dim, score, m_score in zip(f_obj["radar_dimensions"], f_obj["radar_scores"], [20, 15, 5, 10, 10, 10, 10, 10, 5, 5]):
                        radar_data.append({"基金": f_obj["code"] + " " + f_obj["zh"], "維度": dim, "得分率 (%)": (score / m_score) * 100})
                fig_radar = px.line_polar(pd.DataFrame(radar_data), r='得分率 (%)', theta='維度', color='基金', line_close=True, markers=True, range_r=[0, 100], template="plotly_dark")
                fig_radar.update_layout(height=450, paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_radar, use_container_width=True)

        with col_r:
            st.markdown("#### 🏆 風險與回報對比指數排行榜")
            fig_rank = px.bar(df_matrix.sort_values("風險與回報對比指數", ascending=True), x='風險與回報對比指數', y='代號', text='風險與回報對比指數', orientation='h', color='風險與回報對比指數', color_continuous_scale='Greens', template="plotly_white")
            fig_rank.update_layout(height=450)
            st.plotly_chart(fig_rank, use_container_width=True)

# ==============================================================================
# TAB 2: 🔍 單一基金深度風險剖析
# ==============================================================================
with top_tab2:
    ctrl_col1, ctrl_col2 = st.columns([1.8, 1.2])
    with ctrl_col1: selected_preset = st.selectbox("📌 選擇基金名稱：", list(PRESET_FUNDS.keys()))
    curr_fund = PRESET_FUNDS[selected_preset]
    with ctrl_col2: fund_type = st.selectbox("📌 風險評估類別：", ["債券基金", "股票基金", "股債混合基金"], index=1 if curr_fund["category"]=="股票基金" else 0)

    st.markdown(f'<div class="fund-header"><span class="source-tag">📍 {curr_fund["zh"]}</span> <span class="yield-tag">📈 派息率: {curr_fund["last_yield"]}%</span> <span class="ms-star-tag">⭐ {curr_fund.get("star")}</span><br><span style="font-size:20px; font-weight:bold; color:#FFF;">{curr_fund["zh"]}</span> <span style="font-size:14px; color:#AAA;">({curr_fund["en"]})</span></div>', unsafe_allow_html=True)

    with st.expander(f"🏢 基金公司簡介 — {curr_fund['company_name']}", expanded=False):
        st.markdown(f'<ul class="company-profile-list">{"".join([f"<li>{item}</li>" for item in curr_fund["company_profile"]])}</ul>', unsafe_allow_html=True)

    st.markdown('<div class="data-disclaimer-note"><b>📑 數據來源聲明備註：</b> 本 Dashboard 內所有財務數據、持倉比率、派息成分與營運損益，均完全依據<b>基金官方發布之基金月報 (Factsheet)、派息分派紀錄及年度財務報告</b> 客觀建檔分析。</div>', unsafe_allow_html=True)

    # 4 大關鍵 KPI 數據名片
    g1_c1, g1_c2, g1_c3, g1_c4 = st.columns(4)
    with g1_c1: st.metric(label="現時派息率", value=curr_fund['kpis']['p1'])
    with g1_c2: st.metric(label="過往 1 年總回報", value=f"+{curr_fund['return_1y']}%")
    with g1_c3: st.metric(label="過往 3 年年化總回報", value=f"+{curr_fund['return_3y']}%")
    with g1_c4: st.metric(label="總基金資產值 (AUM)", value=curr_fund['kpis']['p8'])

    st.markdown("<br>", unsafe_allow_html=True)

    # 7 大詳細數據分頁
    main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6, main_tab7 = st.tabs([
        "🕸️ 風險維度雷達圖", 
        "📋 底層資產清單 (Top 10)", 
        "📅 歷史派息紀錄", 
        "💰 派息組成 (收益 vs 資本)", 
        "🏭 十大行業分佈 (%)", 
        "🛡️ 評級/市值分佈 (%)", 
        "🌍 地區分佈歷年走勢 (%)"
    ])

    # Tab 1: 雷達圖
    with main_tab1:
        df_chart = pd.DataFrame(dict(
            Score=[(s/m)*100 for s,m in zip(curr_fund["radar_scores"], [20,15,5,10,10,10,10,10,5,5])], 
            RawScore=curr_fund["radar_scores"],
            MaxScore=[20,15,5,10,10,10,10,10,5,5],
            Dimension=curr_fund["radar_dimensions"]
        ))
        fig = px.line_polar(df_chart, r='Score', theta='Dimension', line_close=True, markers=True, range_r=[0, 100], color_discrete_sequence=['#00E676'])
        fig.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.35)', line=dict(color='#00E676', width=2.5))
        fig.update_layout(height=480, margin=dict(l=60, r=60, t=30, b=30), paper_bgcolor="rgba(0,0,0,0)", polar=dict(bgcolor="#1E222D"))
        st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Top 10 底層資產
    with main_tab2:
        top10_html = "".join([f"<tr><td><b>{r['排名']}</b></td><td><b>{r['持倉名稱']}</b></td><td style='color:#475569;'>{r.get('bg','')}</td><td>{r['資產類別']}</td><td style='font-weight:bold;'>{r['佔比 (%)']}</td><td style='text-align:center;'>{r['badge']}</td></tr>" for r in curr_fund.get("top10", [])])
        st.markdown(f'<table class="custom-table"><thead><tr><th>排名</th><th>底層資產名稱</th><th>資產背景簡介</th><th>資產類別</th><th>佔比 (%)</th><th style="text-align:center;">品質評級</th></tr></thead><tbody>{top10_html}</tbody></table>', unsafe_allow_html=True)

    # Tab 3: 歷史派息紀錄
    with main_tab3:
        h_rows = "".join([f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td><b>{r[3]}</b></td><td>{r[4]}</td><td style='font-weight:bold; color:#059669;'>{r[5]}</td></tr>" for r in curr_fund.get("history_div", [])])
        st.markdown(f'<table class="custom-table"><thead><tr><th>除息日</th><th>記錄日</th><th>派息日</th><th>每單位股息</th><th>除息日每單位資產淨值</th><th>年度化派息率</th></tr></thead><tbody>{h_rows}</tbody></table>', unsafe_allow_html=True)

    # Tab 4: 派息組成
    with main_tab4:
        c_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td style='font-weight:bold; color:#D97706;'>{r[3]}</td></tr>" for r in curr_fund.get("composition_div", [])])
        st.markdown(f'<table class="custom-table"><thead><tr><th>除息日</th><th>每股股息</th><th>可分派淨收益/權利金 %</th><th>由資本所分派之股息 % (ROC)</th></tr></thead><tbody>{c_rows}</tbody></table>', unsafe_allow_html=True)

    # Tab 5: 十大行業分佈
    with main_tab5:
        s_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td style='font-weight:bold; color:#1E3A8A;'>{r[1]}</td></tr>" for r in curr_fund.get("sector_dist", [])])
        st.markdown(f'<table class="custom-table" style="width:50%;"><thead><tr><th>行業類別</th><th>佔市值 %</th></tr></thead><tbody>{s_rows}</tbody></table>', unsafe_allow_html=True)

    # Tab 6: 評級/市值分佈
    with main_tab6:
        r_rows = "".join([f"<tr><td><b>{r[0]}</b></td><td style='font-weight:bold; color:#1E3A8A;'>{r[1]}</td></tr>" for r in curr_fund.get("rating_dist", [])])
        st.markdown(f'<table class="custom-table" style="width:50%;"><thead><tr><th>信貸評級 / 市值分佈</th><th>佔市值 %</th></tr></thead><tbody>{r_rows}</tbody></table>', unsafe_allow_html=True)

    # Tab 7: 地區分佈歷年走勢
    with main_tab7:
        if curr_fund.get("geo_dist_history"):
            col_chart_geo, col_table_geo = st.columns([1.2, 1])
            df_geo = pd.DataFrame(curr_fund["geo_dist_history"])
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

    st.markdown("---")

    # 基金深度風險評估明細表
    with st.expander("📋 點擊展開 / 折疊：基金深度風險評估明細表", expanded=True):
        eval_rows_html = "".join([f"<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td style='text-align:center; font-weight:bold;'>{r[4]}</td><td style='text-align:center;'>{r[5]}</td></tr>" for r in curr_fund.get("eval_table", [])])
        st.markdown(f'''
        <table class="custom-table">
            <thead>
                <tr>
                    <th style="width: 14%;">評估維度</th>
                    <th style="width: 18%;">具體檢查指標</th>
                    <th style="width: 25%;">專屬評分簡算規則</th>
                    <th style="width: 27%;">基金真實數據與解析</th>
                    <th style="width: 8%; text-align: center;">得分/滿分</th>
                    <th style="width: 8%; text-align: center;">風險狀態</th>
                </tr>
            </thead>
            <tbody>{eval_rows_html}</tbody>
        </table>
        <div class="summary-footer">
            <span class="summary-title">總得分 / 得分率：</span>
            <span class="summary-score">{curr_fund["score"]} / 100</span>
            <span class="quality-badge-green" style="font-size: 13px; padding: 5px 12px;">{curr_fund["score"]}% (極佳健康/低風險)</span>
        </div>
        ''', unsafe_allow_html=True)

    st.info(f"**💡 AI 智能洞察 ({curr_fund['zh']})**：{curr_fund['summary']}")
