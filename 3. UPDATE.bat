@echo off

if not exist ".git" (
    git init
    git add .
    git remote add origin https://github.com/OxFF00FF/Hamster_Mayhem.git
    git fetch
    git checkout master
    git reset --hard
    git pull https://github.com/OxFF00FF/Hamster_Mayhem.git master
)

echo Getting updates...

git pull

echo Project was updatet to latest version

pause