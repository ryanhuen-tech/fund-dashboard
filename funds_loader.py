# funds_loader.py - 強制停用快取與全類別 PDF 自動解析引擎
import os
import re
import importlib
import pdfplumber
import streamlit as st
from funds import ALL_FUNDS_MAP

# 0. 每次載入前強制作廢 Streamlit 記憶體快取
try:
    st.cache_data.clear()
    st.cache_resource.clear()
except:
    pass

def parse_generic_pdf_tables(pdf_path):
    """通用型 PDF 表格抽取器：相容股票型、債券型與混合型基金之月報表單"""
    history_records = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row:
                            continue
                        row_str = " ".join([str(c) for c in row if c])
                        
                        if any(char.isdigit() for char in row_str):
                            nums = []
                            for cell in row:
                                if cell:
                                    found = re.findall(r"\d+\.\d+|\d+", str(cell))
                                    for f in found:
                                        try:
                                            val = float(f)
                                            if 0 < val < 1000 and val not in [2024, 2025, 2026]:
                                                nums.append(val)
                                        except:
                                            pass
                            
                            date_match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}|\d{2}[/.-]\d{2}[/.-]\d{2,4}", row_str)
                            date_str = date_match.group() if date_match else "最新期"
                            
                            if len(nums) >= 2:
                                payout = min(nums[0], nums[1])
                                nav = max(nums[0], nums[1])
                                yield_str = f"{nums[2]}%" if len(nums) >= 3 else "7.0%"
                                
                                if payout > 0 and nav > 0 and payout != nav:
                                    history_records.append([
                                        date_str, date_str, date_str, 
                                        str(payout), str(nav), yield_str
                                    ])
    except Exception as e:
        print(f"⚠️ 解析 {pdf_path} 異常: {e}")
        return []

    unique_history = []
    seen = set()
    for r in history_records:
        key = f"{r[3]}_{r[4]}"
        if key not in seen:
            seen.add(key)
            unique_history.append(r)
        if len(unique_history) == 12:
            break
            
    return unique_history

def auto_update_all_funds_from_pdfs(funds_dict):
    """自動掃描 pdfs/ 目錄，即時覆蓋所有基金的歷史陣列"""
    pdf_dir = "pdfs"
    if not os.path.exists(pdf_dir):
        return

    pdf_files = os.listdir(pdf_dir)

    for f_key, f_obj in funds_dict.items():
        code = f_obj.get("code") or f_obj.get("代號")
        if not code:
            continue
            
        matched_pdf = None
        for pdf_name in pdf_files:
            if code.upper() in pdf_name.upper() and pdf_name.endswith(".pdf"):
                matched_pdf = pdf_name
                break
                
        if matched_pdf:
            pdf_path = os.path.join(pdf_dir, matched_pdf)
            extracted_history = parse_generic_pdf_tables(pdf_path)
            
            if extracted_history and len(extracted_history) >= 12:
                f_obj["history_div"] = extracted_history
                latest_yield_str = extracted_history[0][5].replace("%", "")
                try:
                    f_obj["last_yield"] = float(latest_yield_str)
                except:
                    pass

def load_all_funds():
    """全系統基金資料加載入口"""
    funds = {}
    for code, mod_name in ALL_FUNDS_MAP.items():
        try:
            mod = importlib.import_module(f"funds.{mod_name}")
            data_dict = getattr(mod, f"DATA_{code.upper()}", {})
            for k, v in data_dict.items():
                funds[k] = v
        except Exception as e:
            print(f"Error loading fund {code}: {e}")
            
    auto_update_all_funds_from_pdfs(funds)
    return funds
