@echo off

echo Initialize Git repo...
git init

SET REMOTE_URL=https://github.com/OxFF00FF/Hamster_Mayhem.git
git remote add origin %REMOTE_URL%

echo Getting uodates...
git pull origin main

echo Project was updatet to latest version
pause