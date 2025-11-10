@echo off
echo ========================================
echo   PlayZone Inventory System
echo   Puerto unico: 8000
echo ========================================
echo.
echo Iniciando servidor...
echo Frontend + Backend en http://localhost:8000
echo.
cd /d "%~dp0"
python main.py
pause
