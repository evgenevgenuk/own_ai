@echo off
echo Встановлення залежностей...

:: Оновлення pip
python -m pip install --upgrade pip

:: Встановлення всіх бібліотек
pip install tk PyPDF2 pandas json5 requests numpy matplotlib seaborn scikit-learn openai

:: Клонування репозиторію (якщо він ще не завантажений)
if not exist own_ai (
    git clone https://github.com/evgenevgenuk/own_ai.git
)

:: Перехід у папку проекту
cd own_ai

:: Запуск Python-скрипта (заміни main.py на потрібний файл)
python main.py

pause
