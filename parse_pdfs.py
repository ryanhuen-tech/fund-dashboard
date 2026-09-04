# parse_pdfs.py - 全自動 PDF 股息與 NAV 解析引擎 (支援真實中文檔名)
import os
import re
import json
import pdfplumber

# 1. 綁定您電腦中的真實 PDF 檔案名稱與基金 Code
PDF_MAP = {
    "ZU6股息派發紀錄.pdf": "ZU6",
    "Z52股息派發紀錄.pdf": "Z52",
    "Z12股息派發紀錄.pdf": "Z12",
    "Z29股息派發紀錄.pdf": "Z29",
    "Z08股息派發紀錄.pdf": "Z08",
    "Z05股息派發紀錄.pdf": "Z05",
    "Z69股息派發紀錄.pdf": "Z69",
    "Z13股息派發紀錄.pdf": "Z13",
    "Z15股息派發紀錄.pdf": "Z15",
    "ZP4股息派發紀錄.pdf": "ZP4"
}

def extract_numbers_from_row(row_cells):
    """從表格的一行欄位中提取所有浮點數 (派息金額與 NAV)"""
    nums = []
    for cell in row_cells:
        if not cell:
            continue
        # 匹配浮點數 (過濾掉文字與符號)
        found = re.findall(r"\d+\.\d+", str(cell))
        for f in found:
            try:
                val = float(f)
                if val > 0:
                    nums.append(val)
            except:
                pass
    return nums

def parse_fund_pdf(pdf_path):
    """從 PDF 檔精確抽取最新 12 個月派息與 NAV 紀錄"""
    div_records = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        row_str = " ".join([str(c) for c in row if c])
                        # 檢查列中是否包含數字結構
                        if any(char.isdigit() for char in row_str):
                            nums = extract_numbers_from_row(row)
                            # 派息列通常含有派息金額與 NAV 兩個浮點數
                            if len(nums) >= 2:
                                payout = min(nums[0], nums[1])
                                nav = max(nums[0], nums[1])
                                
                                # 抓取日期
                                date_match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}|\d{2}[/.-]\d{2}[/.-]\d{2,4}", row_str)
                                date_str = date_match.group() if date_match else "最新期"
                                
                                if payout > 0 and nav > 0:
                                    div_records.append({
                                        "date": date_str,
                                        "payout": payout,
                                        "nav": nav
                                    })
    except Exception as e:
        print(f"  ❌ 讀取 {pdf_path} 時發生錯誤: {str(e)}")
        return []

    # 取最新前 12 個月不重複紀錄
    unique_records = []
    seen = set()
    for r in div_records:
        key = f"{r['payout']}_{r['nav']}"
        if key not in seen:
            seen.add(key)
            unique_records.append(r)
        if len(unique_records) == 12:
            break
            
    return unique_records

def run_auto_parser():
    """批次掃描 pdfs/ 資料夾並更新資料庫"""
    pdf_dir = "pdfs"
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        print(f"📁 已建立 '{pdf_dir}/' 資料夾！請將 PDF 檔案直接放進此目錄中。")
        return

    parsed_database = {}
    
    for filename, code in PDF_MAP.items():
        pdf_file_path = os.path.join(pdf_dir, filename)
        if os.path.exists(pdf_file_path):
            print(f"🔄 正在自動解析：{filename} (基金代號: {code})...")
            records = parse_fund_pdf(pdf_file_path)
            
            if records and len(records) >= 12:
                latest_nav = records[0]["nav"]
                initial_nav = records[-1]["nav"]
                
                # 股息再投資實時滾算
                current_units = 1000.0
                for r in reversed(records):
                    monthly_cash = current_units * r["payout"]
                    current_units += monthly_cash / r["nav"]
                    
                final_val = current_units * latest_nav
                init_val = 1000.0 * initial_nav
                
                nav_to_nav_pct = round(((final_val - init_val) / init_val) * 100, 2)
                cash_return_pct = round(((sum([r["payout"] for r in records]) / initial_nav) + ((latest_nav - initial_nav) / initial_nav)) * 100, 2)
                nav_change_pct = round(((latest_nav - initial_nav) / initial_nav) * 100, 2)
                
                parsed_database[code] = {
                    "records": records,
                    "nav_to_nav_return_pct": nav_to_nav_pct,
                    "cash_payout_return_pct": cash_return_pct,
                    "nav_capital_change_pct": nav_change_pct,
                    "units_grown": round(current_units, 3),
                    "initial_nav": initial_nav,
                    "latest_nav": latest_nav
                }
                print(f"  ✅ {code} 解析精算成功！實時 NAV-to-NAV 總回報: {nav_to_nav_pct}% (單位數: 1,000 ➔ {round(current_units, 3)})")
            else:
                print(f"  ⚠️ {code} 抽取紀錄未滿 12 個月，請確認 PDF 內容。")
        else:
            print(f"  ℹ️ 資料夾內尚未找到：{filename} (跳過)")

    # 將自動精算成果寫入 json 集中庫
    with open("parsed_funds_data.json", "w", encoding="utf-8") as f:
        json.dump(parsed_database, f, ensure_ascii=False, indent=4)
        
    print("\n🎉 全數 PDF 自動解析完成！結果已同步至 'parsed_funds_data.json'。")

if __name__ == "__main__":
    run_auto_parser()
