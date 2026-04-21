@echo off
REM start.bat — Arrancar Blackbox en Windows (para pruebas en VSCode)

echo.
echo   ⬛  BLACKBOX — Modo desarrollo Windows
echo.

cd /d "%~dp0"

REM Arrancar backend Flask
echo   🐉 Backend Flask en puerto 5000...
start "Blackbox Backend" cmd /k "python server.py"
timeout /t 2 /nobreak > nul

REM Arrancar frontend
echo   ♫  Frontend en puerto 8080...
start "Blackbox Frontend" cmd /k "python -m http.server 8080"
timeout /t 1 /nobreak > nul

echo.
echo   ✦  Abre en el navegador:
echo   ^> http://localhost:8080
echo.
pause
