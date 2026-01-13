@echo off
setlocal enabledelayedexpansion

:: Financial Agent - Windows Build Script
:: Usage: make.bat [command]

:: Check Docker function
goto :skip_check_docker
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    echo.
    exit /b 1
)
goto :eof
:skip_check_docker

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="install" goto install
if "%1"=="env" goto env
if "%1"=="db" goto db
if "%1"=="run" goto run
if "%1"=="api" goto api
if "%1"=="docker-cli" goto docker-cli
if "%1"=="docker-api" goto docker-api
if "%1"=="docker-down" goto docker-down
if "%1"=="clean" goto clean

echo Unknown command: %1
goto help

:help
echo.
echo Financial Agent - Available Commands
echo =====================================
echo.
echo Docker (recommended):
echo   make docker-cli    Start PostgreSQL + CLI interactivo
echo   make docker-api    Start PostgreSQL + API REST
echo   make docker-down   Stop all containers
echo.
echo Local development:
echo   make setup         Full setup (venv + deps + .env)
echo   make db            Start only PostgreSQL in Docker
echo   make run           Run CLI (requires: make db)
echo   make api           Run API (requires: make db)
echo.
echo Utilities:
echo   make install       Install dependencies only
echo   make clean         Remove venv and cache files
echo.
goto :eof

:setup
call :venv
call :install
call :env
call :db
echo Waiting for PostgreSQL to be ready...
timeout /t 3 /nobreak >nul
.venv\Scripts\python scripts\init_db.py
echo.
echo Setup complete!
echo.
echo Next steps:
echo   1. Edit .env and add your API key (GEMINI_API_KEY, OPENAI_API_KEY, etc.)
echo   2. Run: make run   (start CLI)
echo.
goto :eof

:venv
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)
goto :eof

:install
call :venv
echo Installing dependencies...
.venv\Scripts\pip install -r requirements.txt
goto :eof

:env
if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Remember to edit .env and add your API key!
)
goto :eof

:db
call :check_docker
if errorlevel 1 goto :eof
echo Starting PostgreSQL...
docker-compose up -d db
echo PostgreSQL running on localhost:5433
goto :eof

:run
.venv\Scripts\python cli.py
goto :eof

:api
.venv\Scripts\python main.py
goto :eof

:docker-cli
call :check_docker
if errorlevel 1 goto :eof
call :env
echo Starting Financial Agent CLI...
docker-compose run --rm cli
goto :eof

:docker-api
call :check_docker
if errorlevel 1 goto :eof
call :env
echo Starting Financial Agent API on http://localhost:8000
docker-compose up --build
goto :eof

:docker-down
call :check_docker
if errorlevel 1 goto :eof
docker-compose down
goto :eof

:clean
if exist ".venv" rmdir /s /q .venv
if exist "__pycache__" rmdir /s /q __pycache__
for /d /r "src" %%d in (__pycache__) do if exist "%%d" rmdir /s /q "%%d"
if exist ".pytest_cache" rmdir /s /q .pytest_cache
echo Cleaned!
goto :eof
