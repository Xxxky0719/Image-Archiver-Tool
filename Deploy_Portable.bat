@echo off
:: 设置编码为简中，防止中文路径乱码
chcp 936 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ===========================================
echo    相机图片归档工具 - 绿色版部署
echo    Developed by Michael Xiang
echo ===========================================
echo.

:: 设置当前目录变量并去除末尾反斜杠
set "BASE_DIR=%~dp0"
set "BASE_DIR=%BASE_DIR:~0,-1%"

:: 1. 环境配置 (Environment Configuration)
set "PYTHON_EXE=%BASE_DIR%\python_env\python.exe"
set "SCRIPT_NAME=image_archiver_v2.py"
set "TASK_NAME=Camera_Image_Archiver_Portable"

:: 2. 预检 (Pre-flight Check)
if not exist "%PYTHON_EXE%" (
    echo [错误] 找不到 python_env 文件夹，请确保路径正确:
    echo %PYTHON_EXE%
    pause
    exit /b
)

if not exist "%BASE_DIR%\%SCRIPT_NAME%" (
    echo [错误] 找不到脚本文件: %SCRIPT_NAME%
    pause
    exit /b
)

echo [检测] 环境正常，正在准备注册任务...

:: 3. 注册 Windows 任务计划 (Registration)
:: 参数说明：/f 强制覆盖旧任务, /sc daily 每天, /st 02:00 凌晨两点执行
set "ACTION=\"%PYTHON_EXE%\" \"%BASE_DIR%\%SCRIPT_NAME%\""

schtasks /create /f /tn "%TASK_NAME%" /tr "%ACTION%" /sc daily /st 02:00 /rl LIMITED

if %errorlevel% equ 0 (
    echo.
    echo ===========================================
    echo [成功] 部署完成！
    echo 运行环境: 自带 (python_env)
    echo 任务名称: %TASK_NAME%
    echo 计划时间: 每天凌晨 02:00
    echo ===========================================
) else (
    echo [失败] 任务注册失败，请检查是否具备管理员权限。
    pause
    exit /b
)

echo.
:: 4. 立即测试功能 (Instant Verification)
set /p choice=是否立即触发一次“归档测试”以验证逻辑? (Y/N): 
if /i "%choice%"=="Y" (
    echo [执行] 正在通过任务计划程序启动任务...
    schtasks /run /tn "%TASK_NAME%"
    echo [提示] 任务已在后台启动，请检查 archive_log.txt 查看运行结果。
)

echo.
echo 按任意键退出部署程序...
pause >nul