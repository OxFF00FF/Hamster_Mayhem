@echo off

if not exist ".env" (
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    pause
    start .env
)

pause

echo Starting...
docker-compose up -d

pause
