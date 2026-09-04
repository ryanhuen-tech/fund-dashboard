# funds_loader.py - 高效秒開版 JSON 數據加載器
import os
import json
import importlib
import streamlit as st
from funds import ALL_FUNDS_MAP

@st.cache_data(ttl=3600)
def load_all_funds():
    """全系統基金資料加載總入口（高速讀取，無任何卡頓）"""
    funds = {}
    for code, mod_name in ALL_FUNDS_MAP.items():
        try:
            mod = importlib.import_module(f"funds.{mod_name}")
            data_dict = getattr(mod, f"DATA_{code.upper()}", {})
            for k, v in data_dict.items():
                funds[k] = v
        except Exception as e:
            print(f"Error loading fund {code}: {e}")

    # 讀取預先解析好的 JSON 檔案
    json_path = "parsed_funds_data.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
                
            for f_key, f_obj in funds.items():
                code = f_obj.get("code") or f_obj.get("代號")
                if code in parsed_data:
                    # 直接以 JSON 最準確的 12 個月歷史覆蓋
                    f_obj["history_div"] = parsed_data[code].get("history_div", f_obj.get("history_div"))
        except Exception as e:
            print(f"JSON 載入異常: {e}")

    return funds
