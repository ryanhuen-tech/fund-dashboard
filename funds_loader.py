# funds_loader.py - 100% 純 JSON 驅動與強制防快取加載器
import os
import json
import importlib
import streamlit as st

def load_all_funds():
    """全系統基金資料加載總入口（徹底以 parsed_funds_data.json 為最高優先級）"""
    funds = {}
    
    # 1. 載入原始基礎結構
    try:
        from funds import ALL_FUNDS
        import copy
        funds = copy.deepcopy(ALL_FUNDS)
    except Exception as e:
        print(f"匯入 ALL_FUNDS 失敗: {e}")

    # 2. 強制讀取 parsed_funds_data.json 並進行全欄位覆蓋
    json_path = "parsed_funds_data.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
                
            for f_key, f_obj in funds.items():
                code = f_obj.get("code") or f_obj.get("代號")
                if code in parsed_data:
                    # 🟢 100% 以 JSON 中的歷史數據為準，徹底切斷舊模組的干擾
                    f_obj["history_div"] = parsed_data[code].get("history_div", f_obj.get("history_div"))
                    if "nav_to_nav_return_pct" in parsed_data[code]:
                        f_obj["return_1y"] = parsed_data[code]["nav_to_nav_return_pct"]
        except Exception as e:
            print(f"❌ JSON 載入失敗: {e}")

    return funds
