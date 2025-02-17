@echo off
:: Перевірка, чи встановлений Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не знайдено! Будь ласка, встановіть Python.
    exit /b
)

:: Перевірка, чи встановлені необхідні бібліотеки
echo Перевіряю необхідні бібліотеки...
pip show PyPDF2 >nul 2>&1
if %errorlevel% neq 0 (
    echo Бібліотека PyPDF2 не знайдена. Встановлюю...
    pip install PyPDF2
)

pip show pandas >nul 2>&1
if %errorlevel% neq 0 (
    echo Бібліотека pandas не знайдена. Встановлюю...
    pip install pandas
)

pip show googlesearch-python >nul 2>&1
if %errorlevel% neq 0 (
    echo Бібліотека googlesearch-python не знайдена. Встановлюю...
    pip install googlesearch-python
)

:: Запуск Python файлу
echo Запуск Python скрипту...
python your_script.py

pause
