# funds_loader.py
import glob
import importlib
import os

def load_all_funds():
    """
    使用絕對路徑動態加載 funds/ 資料夾下所有以 fund_ 開頭的 Python 檔案數據
    """
    all_funds = {}
    
    # 取得目前 funds_loader.py 所在的絕對資料夾路徑
    base_dir = os.path.dirname(os.path.abspath(__file__))
    funds_dir = os.path.join(base_dir, "funds")
    
    # 精準搜尋 funds/ 目錄下所有的 fund_*.py 檔案
    fund_files = glob.glob(os.path.join(funds_dir, "fund_*.py"))
    
    for file_path in fund_files:
        filename = os.path.basename(file_path)
        # 排除非 fund_ 開頭的檔案
        if not filename.startswith("fund_") or not filename.endswith(".py"):
            continue
            
        module_name = f"funds.{filename[:-3]}" # 去掉 .py 副檔名
        
        try:
            # 動態匯入模組
            mod = importlib.import_module(module_name)
            
            # 尋找模組中以 DATA_ 開頭的字典變數並合併
            for var_name in dir(mod):
                if var_name.startswith("DATA_"):
                    fund_dict = getattr(mod, var_name)
                    if isinstance(fund_dict, dict):
                        all_funds.update(fund_dict)
        except Exception as e:
            print(f"載入 {module_name} 失敗: {e}")
                    
    return all_funds

PRESET_FUNDS = load_all_funds()
