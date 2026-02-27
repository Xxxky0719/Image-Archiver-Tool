import os
import shutil
from datetime import datetime, timedelta
import sys

# =====================================================
#  Image Archiver Tool
#  Developed by: Michael Xiang 
#  Mail:mxiang@Aligntech.com
# =====================================================

# ================= 路径与逻辑自适应配置 =================
# 脚本所在目录 (用于存放日志)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置清理周期（天）
RETENTION_DAYS = 45

# 设置归档处理的时间窗口（天）
# 仅处理最近 N 天内的文件
PROCESS_DAYS_WINDOW = 1 #时间需要 ≥ 1天

# 新增：指定需要归档的文件类型（请使用小写，并以.开头）
# 可以添加多种类型，例如: ('.jpg', '.jpeg', '.png')
ARCHIVE_FILE_TYPES = ('.jpg',)

# 手动配置需要处理的文件夹路径列表 (按顺序依次处理)
# 请在列表中填写绝对路径，例如: [r"C:\Photos", r"D:\Images"]
SOURCE_DIRECTORIES = [
    SCRIPT_DIR,  # 默认包含脚本所在目录，你可以添加更多路径
]
# =====================================================

def write_log(message):
    """记录日志到脚本所在目录下的 archive_log.txt"""
    log_file = os.path.join(SCRIPT_DIR, "archive_log.txt")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"无法写入日志: {e}")

def run_full_archive():
    print("--- 请注意  ---")
    print("--- 进程已进入 run_full_archive  ---")
    print("--- 正在进行图片自动归档，请勿关闭弹窗 ---")
    print("--- Tool Developed by Michael ---")
    print("--- 将会持续3-5分钟，请耐心等待 ---")
    print("--- 可以最小化窗口 ---")
    print("--- 不影响正常操作 ---")
    print("--- Please note  ---")
    print("--- The process has entered run_full_archive ---")
    print("--- Automatic image archiving is in progress; please do not close the window. ---")
    print("--- This will take 3-5 minutes, please wait patiently. ---")
    print("--- You can minimize the window. ---")
    print("--- It will not affect normal operation. ---")
    write_log("任务开始...")

    if PROCESS_DAYS_WINDOW <= 0:
        write_log(f"配置警告: PROCESS_DAYS_WINDOW 设置为 {PROCESS_DAYS_WINDOW}。此值应为正整数(>=1)，当值为0或负数时，将不会归档任何文件。")

    now = datetime.now()
    today_str = now.strftime('%Y%m%d')
    
    # --- 新增：定义处理窗口 (Time Window) ---
    # 仅处理最近 N 天内的历史文件
    process_limit_start = (now - timedelta(days=PROCESS_DAYS_WINDOW)).strftime('%Y%m%d')
    # 自动清理设定时间外的图片
    expiry_limit = (now - timedelta(days=RETENTION_DAYS)).strftime('%Y%m%d')
    
    write_log(f"--- 归档启动 (仅处理范围: {process_limit_start} 至 {today_str}) ---")
    
    for source_dir in SOURCE_DIRECTORIES:
        write_log(f"\n>>> 正在处理目录: {source_dir}")
        
        if not os.path.exists(source_dir):
            write_log(f"目录不存在，跳过: {source_dir}")
            continue

        moved_count = 0
        error_count = 0
        created_folders = set()

        try:
            with os.scandir(source_dir) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.lower().endswith(ARCHIVE_FILE_TYPES):
                        # 获取文件最后修改时间
                        mtime_dt = datetime.fromtimestamp(entry.stat().st_mtime)
                        mtime_str = mtime_dt.strftime('%Y%m%d')
                        
                        # --- 核心逻辑修改：范围过滤 ---
                        # 1. 必须早于今天 (mtime_str < today_str)
                        # 2. 必须在设定窗口内 (mtime_str >= process_limit_start)
                        if process_limit_start <= mtime_str < today_str:
                            target_dir = os.path.join(source_dir, mtime_str)
                            
                            if not os.path.exists(target_dir):
                                os.makedirs(target_dir)
                                created_folders.add(mtime_str)
                            
                            try:
                                # 增加文件占用检查，防止搬运正在写入的文件
                                shutil.move(entry.path, os.path.join(target_dir, entry.name))
                                moved_count += 1
                            except (IOError, OSError) as move_error:
                                error_count += 1
                                write_log(f"  [错误] 移动文件失败: {entry.path}. 原因: {move_error}")
                        
                        # 如果文件超出了设定窗口且早于今天，脚本将直接跳过它（避免全量扫描带来的负担）

            if created_folders:
                write_log(f"新建文件夹: {', '.join(sorted(created_folders))}")
            
            summary_log = f"执行结果: 成功移动 {moved_count} 个文件。"
            if error_count > 0:
                summary_log += f" {error_count} 个文件移动失败 (详见上方错误日志)。"
            write_log(summary_log)

        except Exception as e:
            write_log(f"扫描异常: {str(e)}")

        # 2. 过期数据清理 (针对 YYYYMMDD 格式的文件夹)
        try:
            with os.scandir(source_dir) as entries:
                for entry in entries:
                    if entry.is_dir() and len(entry.name) == 8 and entry.name.isdigit():
                        if entry.name <= expiry_limit:
                            shutil.rmtree(entry.path)
                            write_log(f"清理成功: 已删除过期目录 {entry.name}")
        except Exception as e:
            write_log(f"清理异常: {str(e)}")

    write_log("--- 任务结束 ---\n")

if __name__ == "__main__":
    run_full_archive()