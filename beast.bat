@echo off
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo [SYSTEM] Starting Ollama backend...
    start /B "" ollama serve >nul 2>&1
)
python "%~dp0beast.py" %*
