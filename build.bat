@echo off
echo ==============================
echo   BUILD TOKY (.EXE)
echo ==============================

pip install -r requirements.txt >nul
pip install pyinstaller >nul

rmdir /s /q build
rmdir /s /q dist

pyinstaller ^
--name toky ^
--onefile ^
--windowed ^
--icon=app-icon.ico ^
--add-data "resources;resources" ^
--add-data "styles;styles" ^
--add-data "translations;translations" ^
--add-data "app-logo.png;." ^
--hidden-import pyotp ^
--hidden-import pkgutil ^
--hidden-import cryptography ^
--clean --noconfirm main.py

echo.
echo ==============================
echo   BUILD FINALIZADO
echo ==============================
echo Arquivo em: dist\toky.exe
pause