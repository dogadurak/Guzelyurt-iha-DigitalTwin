@echo off
echo ========================================================
echo Guzelyurt Gercek Dokulu 3B Model Baslatiliyor...
echo Lutfen bekleyin, 163 MB model tarayicida yuklenecek.
echo ========================================================
echo.
echo (Tarayici otomatik olarak acilacaktir, bu siyah ekrani KAPATMAYIN!)

:: Start a local server at the current root directory
start "Local Server" /B python -m http.server 8000

:: Wait 2 seconds for the server to start
timeout /t 2 /nobreak > NUL

:: Open the browser to the HTML file
start http://localhost:8000/01_WebODM_YKNsiz_Python/Sonuclar/Gercek_3B_Model.html

echo.
echo Tarayici acildi. Isiniz bittiginde bu pencereyi kapatabilirsiniz.
pause
