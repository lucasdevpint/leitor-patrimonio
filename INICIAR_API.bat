@echo off
title Sistema Patrimonial - API
color 0A
echo.
echo  ========================================
echo   Sistema Patrimonial - API + App Web
echo  ========================================
echo.
echo  Iniciando servidor...
echo  Acesse no PC:      http://localhost:8000/app
echo  Acesse no celular: http://SEU_IP:8000/app
echo.
echo  Para descobrir seu IP, abra outro terminal e digite: ipconfig
echo  Procure por "Endereco IPv4"
echo.
echo  Pressione CTRL+C para parar o servidor.
echo.

cd /d "%~dp0"
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

pause
