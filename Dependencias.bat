@echo off
title Instalador de Dependencias - Montar Personagens
cd /d "%~dp0"

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao foi encontrado no sistema.
    echo Instale o Python por aqui: https://www.python.org/downloads/
    pause
    exit /b
)

:: Verifica se tkinter está disponível
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [ERRO] O modulo 'tkinter' nao foi encontrado.
    echo Isso indica que sua instalacao do Python esta incompleta.
    echo Baixe a versao oficial completa em: https://www.python.org/downloads/
    pause
    exit /b
)

:: Instala o Pillow
echo Instalando a biblioteca Pillow...
pip install pillow

if errorlevel 1 (
    echo [ERRO] Falha ao instalar a biblioteca Pillow.
    pause
    exit /b
)

echo ---------------------------------------------
echo [✔] Todas as dependencias foram instaladas!
echo Agora voce pode rodar o script com o outro .bat
echo ---------------------------------------------
pause
