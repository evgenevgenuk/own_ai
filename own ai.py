@echo off
setlocal enabledelayedexpansion

:: Перевірка, чи встановлений Python
echo Перевірка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не знайдено! Завантажую та встановлюю...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe' -OutFile 'python_installer.exe'}"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo Python встановлено!
)

:: Перевірка, чи встановлений Git
echo Перевірка Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git не знайдено! Завантажую та встановлюю...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/latest/download/Git-2.42.0-64-bit.exe' -OutFile 'git_installer.exe'}"
    start /wait git_installer.exe /silent
    del git_installer.exe
    echo Git встановлено!
)

:: Клонування репозиторію, якщо його ще немає
if not exist "own_ai" (
    echo Клоную репозиторій...
    git clone https://github.com/evgenevgenuk/own_ai.git
) else (
    echo Репозиторій вже завантажено, оновлюю...
    cd own_ai
    git pull
    cd ..
)

:: Перехід у папку проекту
cd own_ai

:: Встановлення необхідних бібліотек
echo Встановлюю бібліотеки...
pip install tk PyPDF2 pandas googlesearch-python

:: Запуск Python-скрипта own ai.py
echo Запуск own ai.py...
python "own ai.py"

pause
