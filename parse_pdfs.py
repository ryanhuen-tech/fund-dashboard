# parse_pdfs.py - 全自動 PDF 股息與 NAV 解析引擎
import os
import re
import json
import pdfplumber

# PDF 檔名與基金 Code 的對應關聯
PDF_MAP = {
    "ZU6.pdf": "ZU6",
    "Z52.pdf": "Z52",
    "Z12.pdf": "Z12",
    "Z29.pdf": "Z29",
    "Z08.pdf": "Z08",
    "Z05.pdf": "Z05",
    "Z69.pdf": "Z69",
    "Z13.pdf": "Z13",
    "Z15.pdf": "Z15",
    "ZP4.pdf": "ZP4"
}

def extract_numbers_from_row(row_cells):
    """從表格的一行數據中精確提取浮點數 (如每股派息與 NAV)"""
    nums = []
    for cell in row_cells:
        if not cell:
            continue
        # 匹配小數點或純數字 (過濾掉日期與貨幣符號)
        found = re.findall(r"\d+\.\d+|\d+", str(cell))
        for f in found:
            try:
                val = float(f)
                if val > 0:
                    nums.append(val)
            except:
                pass
    return nums

def parse_fund_pdf(pdf_path):
    """讀取單一 PDF 檔案並自動抽取 12 個月派息與 NAV 表格"""
    div_records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # 簡單過濾含有日期或數值的表格列
                    row_str = " ".join([str(c) for c in row if c])
                    if any(char.isdigit() for char in row_str):
                        nums = extract_numbers_from_row(row)
                        # 典型的派息表格列通常包含 [每股派息, NAV] 或 [NAV, 每股派息]
                        if len(nums) >= 2:
                            # 第一個小於 2 的極可能是每股派息，大於 2 的是 NAV (或相反)
                            payout = min(nums[0], nums[1]) if nums[0] < 5.0 or nums[1] < 5.0 else nums[0]
                            nav = max(nums[0], nums[1]) if payout != max(nums[0], nums[1]) else nums[1]
                            
                            # 提取日期關鍵字 (如 2026-06 或 06/2026)
                            date_match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}", row_str)
                            date_str = date_match.group() if date_match else "最新"
                            
                            if payout > 0 and nav > 0:
                                div_records.append({
                                    "date": date_str,
                                    "payout": payout,
                                    "nav": nav
                                })

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
    """批次解析 pdfs/ 資料夾內的所有 PDF 檔並寫入 json"""
    pdf_dir = "pdfs"
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        print(f"📁 已為您自動建立 '{pdf_dir}/' 資料夾，請將基金 PDF 檔放入此資料夾中！")
        return

    parsed_database = {}
    
    for filename, code in PDF_MAP.items():
        pdf_file_path = os.path.join(pdf_dir, filename)
        if os.path.exists(pdf_file_path):
            print(f"🔄 正在自動解析 {filename} ({code})...")
            records = parse_fund_pdf(pdf_file_path)
            if records and len(records) >= 12:
                # 實時計算 NAV-to-NAV 總回報
                latest_nav = records[0]["nav"]
                initial_nav = records[-1]["nav"]
                
                current_units = 1000.0
                for r in reversed(records):
                    monthly_cash = current_units * r["payout"]
                    current_units += monthly_cash / r["nav"]
                    
                final_val = current_units * latest_nav
                init_val = 1000.0 * initial_nav
                
                nav_to_nav_pct = round(((final_val - init_val) / init_val) * 100, 2)
                cash_return_pct = round((sum([r["payout"] for r in records]) / initial_nav) * 100 + ((latest_nav - initial_nav) / initial_nav * 100), 2)
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
                print(f"  ✅ {code} 解析成功！NAV-to-NAV 實時精算總回報: {nav_to_nav_pct}%")
            else:
                print(f"  ⚠️ {code} 表格提取紀錄不足 12 個月，請檢查 PDF 格式。")
        else:
            print(f"  ℹ️ 未找到 {filename}，跳過解析。")

    # 將成果儲存至集中資料庫
    with open("parsed_funds_data.json", "w", encoding="utf-8") as f:
        json.dump(parsed_database, f, ensure_ascii=False, indent=4)
        
    print("\n🎉 全數 PDF 解析完成！最新數據已寫入 'parsed_funds_data.json'。")

if __name__ == "__main__":
    run_auto_parser()
