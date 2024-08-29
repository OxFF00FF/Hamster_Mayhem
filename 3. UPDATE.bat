@echo off

echo Инициализация Git репозитория...
git init

SET REMOTE_URL=https://github.com/OxFF00FF/Hamster_Mayhem.git
git remote add origin %REMOTE_URL%

echo Получение последних изменений...
git pull origin main

echo Проект успешно обновлен
pause