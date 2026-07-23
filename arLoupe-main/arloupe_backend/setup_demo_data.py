import os
import shutil
import sqlite3
from datetime import datetime

# 定義路徑
base_dir = r"C:\Users\user\Downloads\phase-2-admin-suite"
backend_dir = os.path.join(base_dir, "arLoupe-main", "arloupe_backend")
media_videos_dir = os.path.join(backend_dir, "media", "videos")
db_path = os.path.join(backend_dir, "db.sqlite3")

segments_src_dir = os.path.join(base_dir, "arloupe_data", "recordings", "2026-05-20")

# 確保目標媒體資料夾存在
os.makedirs(media_videos_dir, exist_ok=True)

# 定義患者名稱與對應的片段名稱
patient_mappings = [
    {"seg": "20260520_114537_arloupe01_seg00000.mp4", "name": "王大明_P-887_牙周治療_20260520"},
    {"seg": "20260520_114537_arloupe01_seg00001.mp4", "name": "陳小美_P-342_植牙手術_20260520"},
    {"seg": "20260520_114537_arloupe01_seg00002.mp4", "name": "林建國_P-992_拔牙手術_20260520"},
    {"seg": "20260520_114537_arloupe01_seg00003.mp4", "name": "張雅婷_P-101_洗牙保健_20260520"},
    {"seg": "20260520_114537_arloupe01_seg00004.mp4", "name": "李明輝_P-554_根管治療_20260520"}
]

print("--- 開始轉移實際 arLoupe 影片並重命名為患者姓名 ---")

# 1. 複製並命名實體檔案
copied_files = []
for mapping in patient_mappings:
    src_file_path = os.path.join(segments_src_dir, mapping["seg"])
    new_filename = f"{mapping['name']}.mp4"
    dest_file_path = os.path.join(media_videos_dir, new_filename)
    
    if os.path.exists(src_file_path):
        print(f"複製: {mapping['seg']} -> {new_filename}")
        shutil.copy2(src_file_path, dest_file_path)
        copied_files.append({"title": mapping["name"], "db_file_path": f"videos/{new_filename}"})
    else:
        print(f"找不到來源片段: {src_file_path}")

# 2. 清理並重新寫入 Django SQLite 資料庫
if copied_files:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # 清理舊資料（只保留新複製的專業患者資料）
        print("清理舊資料庫影片紀錄...")
        cur.execute("DELETE FROM video_api_video")
        
        # 寫入新紀錄
        for idx, item in enumerate(copied_files, start=1):
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            print(f"寫入資料庫 ID {idx}: {item['title']}")
            cur.execute(
                "INSERT INTO video_api_video (id, title, file, created_at) VALUES (?, ?, ?, ?)",
                (idx, item["title"], item["db_file_path"], created_at)
            )
            
        conn.commit()
        conn.close()
        print("--- 資料庫寫入成功！共建立 5 筆專業患者病例錄影資料 ---")
    except Exception as e:
        print(f"資料庫更新失敗: {e}")
else:
    print("沒有複製任何檔案，未更新資料庫。")
