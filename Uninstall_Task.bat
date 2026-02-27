@echo off
chcp 936 >nul
setlocal
cd /d "%~dp0"

echo ===========================================
echo    相机图片归档工具 - 一键卸载工具
echo ===========================================
echo.

set "TASK_NAME=Camera_Image_Archiver_Portable"

echo [执行] 正在尝试从系统中移除任务: %TASK_NAME%...
echo.

schtasks /query /tn "%TASK_NAME%" >nul 2>&1

if %errorlevel% equ 0 (
schtasks /delete /tn "%TASK_NAME%" /f

) else (
echo [提示] 系统中未找到任务 "%TASK_NAME%"，无需卸载。
)

echo.
pause