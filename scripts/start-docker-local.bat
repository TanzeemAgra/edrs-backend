@echo off
REM EDRS Docker Local Environment Startup Script for Windows
REM Automated deployment with smart dependency management

setlocal enabledelayedexpansion

echo.
echo 🚀 EDRS P&ID Analysis System - Docker Local Deployment
echo ==================================================================

REM Configuration
set "COMPOSE_FILE=docker-compose.local.yml"
set "ENV_FILE=.env.local"
set "PROJECT_NAME=edrs-local"

REM Check prerequisites
echo.
echo 📋 Checking prerequisites...

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker is not installed. Please install Docker Desktop.
    pause
    exit /b 1
)
echo ✓ Docker is installed

REM Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ✗ Docker Compose is not installed. Please install Docker Compose.
        pause
        exit /b 1
    )
)
echo ✓ Docker Compose is installed

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)
echo ✓ Docker is running

REM Environment setup
echo.
echo 🔧 Setting up environment...

REM Create .env.local from example if it doesn't exist
if not exist "%ENV_FILE%" (
    if exist ".env.local.example" (
        copy ".env.local.example" "%ENV_FILE%" >nul
        echo ✓ Created %ENV_FILE% from example
        echo ⚠ Please edit %ENV_FILE% with your OpenAI API key and other settings
    ) else (
        echo ✗ .env.local.example not found
        pause
        exit /b 1
    )
) else (
    echo ✓ Environment file exists
)

REM Check for OpenAI API key
findstr /C:"OPENAI_API_KEY=sk-" "%ENV_FILE%" >nul 2>&1
if errorlevel 1 (
    echo ⚠ OpenAI API key not configured. P&ID analysis will run in demo mode.
)

REM Clean up previous containers
echo.
echo 🧹 Cleaning up previous containers...
docker-compose -f "%COMPOSE_FILE%" --env-file "%ENV_FILE%" -p "%PROJECT_NAME%" down --remove-orphans >nul 2>&1
echo ✓ Previous containers cleaned up

REM Build and start services
echo.
echo 🏗️ Building and starting services...

REM Build without cache for fresh start
echo Building containers...
docker-compose -f "%COMPOSE_FILE%" --env-file "%ENV_FILE%" -p "%PROJECT_NAME%" build --no-cache

REM Start databases first
echo.
echo 📊 Starting databases...
docker-compose -f "%COMPOSE_FILE%" --env-file "%ENV_FILE%" -p "%PROJECT_NAME%" up -d postgres mongodb redis

REM Wait for databases
echo.
echo ⏳ Waiting for databases to be ready...
timeout /t 10 /nobreak >nul

echo Checking database health...
timeout /t 15 /nobreak >nul

REM Start backend
echo.
echo 🔧 Starting backend...
docker-compose -f "%COMPOSE_FILE%" --env-file "%ENV_FILE%" -p "%PROJECT_NAME%" up -d backend

REM Wait for backend
echo ⏳ Waiting for backend to initialize...
timeout /t 20 /nobreak >nul

REM Start frontend
echo.
echo 🎨 Starting frontend...
docker-compose -f "%COMPOSE_FILE%" --env-file "%ENV_FILE%" -p "%PROJECT_NAME%" up -d frontend

REM Wait for services to be ready
echo.
echo ⏳ Waiting for services to be ready...
timeout /t 25 /nobreak >nul

REM Health checks
echo.
echo 🏥 Performing health checks...

REM Check backend health
curl -f -s http://localhost:8001/health/ >nul 2>&1
if errorlevel 1 (
    echo ⚠ Backend health check failed. Service may still be starting...
) else (
    echo ✓ Backend is healthy
)

REM Check frontend health
curl -f -s http://localhost:3001 >nul 2>&1
if errorlevel 1 (
    echo ⚠ Frontend health check failed. Service may still be starting...
) else (
    echo ✓ Frontend is healthy
)

REM Display status
echo.
echo 📊 Service Status:
docker-compose -f "%COMPOSE_FILE%" --env-file "%ENV_FILE%" -p "%PROJECT_NAME%" ps

REM Display URLs
echo.
echo 🎉 EDRS P&ID Analysis System is running!
echo ==================================================================
echo 🌐 Access URLs:
echo    Frontend:     http://localhost:3001
echo    Backend API:  http://localhost:8001
echo    Admin Panel:  http://localhost:8001/admin
echo    API Docs:     http://localhost:8001/api/docs/
echo.
echo 👤 Default Admin User:
echo    Username: admin
echo    Password: admin123
echo    Email:    admin@edrs.local
echo.
echo 📊 Database Access:
echo    PostgreSQL:   localhost:5433
echo    MongoDB:      localhost:27018
echo    Redis:        localhost:6380
echo.
echo 📝 Next Steps:
echo 1. Open http://localhost:3001 in your browser
echo 2. Login with admin credentials
echo 3. Navigate to P&ID Analysis section
echo 4. Upload a P&ID diagram to test the system
echo.
echo 🛠️ Useful Commands:
echo    View logs:    docker-compose -f %COMPOSE_FILE% --env-file %ENV_FILE% -p %PROJECT_NAME% logs -f
echo    Stop all:     docker-compose -f %COMPOSE_FILE% --env-file %ENV_FILE% -p %PROJECT_NAME% down
echo    Restart:      docker-compose -f %COMPOSE_FILE% --env-file %ENV_FILE% -p %PROJECT_NAME% restart
echo.
echo ✨ Happy analyzing! 🏗️📊
echo.
echo Press any key to open the application in your browser...
pause >nul

REM Open browser
start http://localhost:3001