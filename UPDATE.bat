@echo off

SET REMOTE=https://github.com/OxFF00FF/Hamster_Mayhem.git

if not exist ".git" (
    git init
    git add .
    git remote add origin %REMOTE%
    git fetch
    git checkout master
    git reset --hard
    git pull %REMOTE% master
)

echo Getting updates...

git pull

echo Project was updatet to latest version

pause