@echo off
cd /d C:\Users\FC\Documents\finance-app\SmartBank-main
echo Importing finance_data.json into Neon PostgreSQL...
echo 20 tables, one for each field (har field ka alag table)
echo.
echo Step 1: Creating tables and importing data...
node scripts\run_import_neon.cjs > neon_import.log 2>&1
echo.
echo Done! Check neon_import.log for details.
echo.
echo Quick summary:
findstr /C:"🎉" neon_import.log
findstr /C:"📊" neon_import.log
findstr /C:"🗂️" neon_import.log
echo.
pause
