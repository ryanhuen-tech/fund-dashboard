# funds_loader.py
import glob
import importlib
import os

def load_all_funds():
    """
    自動動態加載 funds/ 資料夾下所有以 fund_ 開頭的 Python 檔案中的數據
    """
    all_funds = {}
    
    # 搜尋 funds/ 資料夾下的所有 fund_*.py 檔案
    fund_files = glob.glob(os.path.join("funds", "fund_*.py"))
    
    for file_path in fund_files:
        filename = os.path.basename(file_path)
        module_name = f"funds.{filename[:-3]}" # 去掉 .py 副檔名
        
        # 動態匯入模組
        mod = importlib.import_module(module_name)
        
        # 尋找模組中以 DATA_ 開頭的字典變數並合併
        for var_name in dir(mod):
            if var_name.startswith("DATA_"):
                fund_dict = getattr(mod, var_name)
                if isinstance(fund_dict, dict):
                    all_funds.update(fund_dict)
                    
    return all_funds

PRESET_FUNDS = load_all_funds()
