@echo off
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama is not installed or not in your PATH.
    echo [FIX] Please run 'OllamaSetup.exe' in this folder to install the local engine.
    pause
    exit /b
)

tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo [SYSTEM] Starting Ollama backend...
    start /B "" ollama serve >nul 2>&1
    timeout /t 5 >nul
)
python "%~dp0beast.py" %*
