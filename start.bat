@echo off
cd /d %~dp0

if not exist venv (
    echo Первый запуск: создаю окружение...
    python -m venv venv
)

call venv\Scripts\activate.bat

pip install -r requirements.txt --quiet

if not exist .env (
    copy .env.example .env
    echo Создан файл .env — заполните его перед первым запуском и запустите снова.
    pause
    exit /b
)

echo Запускаю... через пару секунд откроется браузер.
python review_app.py

pause
