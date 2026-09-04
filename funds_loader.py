# funds_loader.py - 高效安全版 JSON 數據加載器
import os
import json
import importlib
import streamlit as st

# 1. 直接於內部定義基金模組對應表，防止 ImportError 崩潰
SAFE_FUNDS_MAP = {
    "Z01": "fund_z01", "Z03": "fund_z03", "Z04": "fund_z04", "Z05": "fund_z05",
    "Z06": "fund_z06", "Z07": "fund_z07", "Z08": "fund_z08", "Z12": "fund_z12",
    "Z13": "fund_z13", "Z15": "fund_z15", "Z17": "fund_z17", "Z18": "fund_z18",
    "Z20": "fund_z20", "Z29": "fund_z29", "Z33": "fund_z33", "Z51": "fund_z51",
    "Z52": "fund_z52", "Z69": "fund_z69", "Z77": "fund_z77", "ZP4": "fund_zp4",
    "ZU6": "fund_zu6"
}

@st.cache_data(ttl=86400)
def load_all_funds():
    """全系統基金資料加載總入口（快取 24 小時，畫面秒開）"""
    funds = {}
    
    # 嘗試匯入全量基金地圖
    try:
        from funds import ALL_FUNDS_MAP
        target_map = ALL_FUNDS_MAP
    except (ImportError, AttributeError):
        target_map = SAFE_FUNDS_MAP

    # 加載 funds/ 資料夾內各基金檔
    for code, mod_name in target_map.items():
        try:
            mod = importlib.import_module(f"funds.{mod_name}")
            data_dict = getattr(mod, f"DATA_{code.upper()}", {})
            for k, v in data_dict.items():
                funds[k] = v
        except Exception as e:
            print(f"Error loading fund {code}: {e}")

    # 讀取 JSON 快取檔覆蓋派息紀錄
    json_path = "parsed_funds_data.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
                
            for f_key, f_obj in funds.items():
                code = f_obj.get("code") or f_obj.get("代號")
                if code in parsed_data:
                    f_obj["history_div"] = parsed_data[code].get("history_div", f_obj.get("history_div"))
        except Exception as e:
            print(f"JSON 載入異常: {e}")

    return funds
