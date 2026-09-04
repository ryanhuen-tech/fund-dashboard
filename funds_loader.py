# funds_loader.py - 完美契合內部 ALL_FUNDS 結構之高效率加載引擎
import os
import json
import copy
import streamlit as st

@st.cache_data(ttl=86400)
def load_all_funds():
    """全系統基金資料加載總入口（快取 24 小時，絕不重複載入，畫面秒開）"""
    try:
        from funds import ALL_FUNDS
        funds = copy.deepcopy(ALL_FUNDS)
    except Exception as e:
        print(f"從 funds 匯入 ALL_FUNDS 失敗: {e}")
        funds = {}

    # 讀取 JSON 預解析好的數據，進行快速精確覆蓋
    json_path = "parsed_funds_data.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
                
            for f_key, f_obj in funds.items():
                code = f_obj.get("code") or f_obj.get("代號")
                if code in parsed_data:
                    # 以 JSON 最新 PDF 解析陣列覆蓋 history_div
                    f_obj["history_div"] = parsed_data[code].get("history_div", f_obj.get("history_div"))
        except Exception as e:
            print(f"JSON 載入異常: {e}")

    return funds
