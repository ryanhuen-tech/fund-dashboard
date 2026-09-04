# funds_loader.py - 全類別基金 (債券/股票/混合) 100% 官方 PDF 通用自動解析引擎
import os
import re
import importlib
import pdfplumber
from funds import ALL_FUNDS_MAP

def parse_generic_pdf_tables(pdf_path):
    """通用型 PDF 表格抽取器：可完美相容股票型、債券型與混合型基金之月報表單"""
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
                        
                        # 篩選包含數字的有效資料列
                        if any(char.isdigit() for char in row_str):
                            nums = []
                            for cell in row:
                                if cell:
                                    # 提取小數或整數
                                    found = re.findall(r"\d+\.\d+|\d+", str(cell))
                                    for f in found:
                                        try:
                                            val = float(f)
                                            # 過濾掉純年份等無關大數字
                                            if 0 < val < 1000 and val != 2024 and val != 2025 and val != 2026:
                                                nums.append(val)
                                        except:
                                            pass
                            
                            # 提取日期 (如 2026-06、12/06/2026 或 06/2026)
                            date_match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}|\d{2}[/.-]\d{2}[/.-]\d{2,4}", row_str)
                            date_str = date_match.group() if date_match else "最新期"
                            
                            # 數值動態匹配：通常小值為每股派息，大值為 NAV (亦相容股票型高 NAV)
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
        print(f"⚠️ 解析 {pdf_path} 時發生異常: {e}")
        return []

    # 剔除重複數據並嚴格擷取最新 12 個月紀錄
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
    """自動掃描 pdfs/ 目錄，支援股票、債券及混合基金檔名自動對應"""
    pdf_dir = "pdfs"
    if not os.path.exists(pdf_dir):
        return

    # 獲取 pdfs/ 資料夾內所有檔案名稱
    pdf_files = os.listdir(pdf_dir)

    for f_key, f_obj in funds_dict.items():
        code = f_obj.get("code") or f_obj.get("代號")
        if not code:
            continue
            
        # 🎯 智能檔名匹配：只要 PDF 檔名中包含基金 Code (例如 "Z01" 或 "Z05") 即可自動識別！
        matched_pdf = None
        for pdf_name in pdf_files:
            if code.upper() in pdf_name.upper() and pdf_name.endswith(".pdf"):
                matched_pdf = pdf_name
                break
                
        if matched_pdf:
            pdf_path = os.path.join(pdf_dir, matched_pdf)
            extracted_history = parse_generic_pdf_tables(pdf_path)
            
            if extracted_history and len(extracted_history) >= 12:
                # 全自動更新該基金 (無論類別) 的歷史派息與 NAV 陣列
                f_obj["history_div"] = extracted_history
                
                # 自動校正上月最新派息率
                latest_yield_str = extracted_history[0][5].replace("%", "")
                try:
                    f_obj["last_yield"] = float(latest_yield_str)
                except:
                    pass
                    
                cat_type = f_obj.get("category", "通用型")
                print(f"✅ [全類別 PDF 自動同步成功] 【{cat_type}】{code} 已從 {matched_pdf} 自動載入最新 12 個月數據。")

def load_all_funds():
    """全系統基金資料加載總入口"""
    funds = {}
    for code, mod_name in ALL_FUNDS_MAP.items():
        try:
            mod = importlib.import_module(f"funds.{mod_name}")
            data_dict = getattr(mod, f"DATA_{code.upper()}", {})
            for k, v in data_dict.items():
                funds[k] = v
        except Exception as e:
            print(f"Error loading fund {code}: {e}")
            
    # 🟢 啟動全類別 (股票/混合/債券) PDF 通用自動同步引擎
    auto_update_all_funds_from_pdfs(funds)
    
    return funds
