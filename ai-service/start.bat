@echo off
echo ========================================
echo   SQL Pilot AI Service
echo ========================================
echo.

echo [1/3] 检查环境...
python test_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ 环境检查失败，请先解决问题
    pause
    exit /b 1
)

echo.
echo [2/3] 检查端口 8000...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ⚠ 端口 8000 已被占用，尝试使用 8001
    set PORT=8001
) else (
    set PORT=8000
)

echo.
echo [3/3] 启动服务...
echo.
echo ========================================
echo   服务将在 http://localhost:%PORT% 启动
echo   Swagger 文档: http://localhost:%PORT%/docs
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

uvicorn app:app --host 0.0.0.0 --port %PORT% --reload

pause