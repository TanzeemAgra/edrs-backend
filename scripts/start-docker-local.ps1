# EDRS Docker Local Environment Startup Script for PowerShell
# Automated deployment with smart dependency management

param(
    [switch]$Clean,
    [switch]$Logs,
    [switch]$Stop,
    [switch]$Help
)

# Configuration
$ComposeFile = "docker-compose.local.yml"
$EnvFile = ".env.local"
$ProjectName = "edrs-local"

# Colors for output
$Red = "Red"
$Green = "Green" 
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Status {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor $Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠ $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor $Red
}

function Write-Info {
    param($Message)
    Write-Host "$Message" -ForegroundColor $Blue
}

function Show-Help {
    Write-Host @"
EDRS P&ID Analysis System - Docker Local Deployment

Usage: .\start-docker-local.ps1 [OPTIONS]

Options:
  -Clean    Clean up all containers and start fresh
  -Logs     Show service logs
  -Stop     Stop all services
  -Help     Show this help message

Examples:
  .\start-docker-local.ps1           # Start the system
  .\start-docker-local.ps1 -Clean    # Clean start
  .\start-docker-local.ps1 -Logs     # View logs
  .\start-docker-local.ps1 -Stop     # Stop services
"@ -ForegroundColor $Blue
}

if ($Help) {
    Show-Help
    exit 0
}

Write-Host ""
Write-Info "EDRS P&ID Analysis System - Docker Local Deployment"
Write-Info "=================================================================="

# Handle different actions
if ($Stop) {
    Write-Info "Stopping all services..."
    docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName down --remove-orphans
    Write-Status "All services stopped"
    exit 0
}

if ($Logs) {
    Write-Info "Showing service logs..."
    docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName logs -f
    exit 0
}

# Check prerequisites
Write-Info "Checking prerequisites..."

# Check Docker
try {
    $null = docker --version
    Write-Status "Docker is installed"
} catch {
    Write-Error "Docker is not installed. Please install Docker Desktop."
    exit 1
}

# Check Docker Compose
try {
    $null = docker-compose --version
    Write-Status "Docker Compose is installed"
} catch {
    try {
        $null = docker compose version
        Write-Status "Docker Compose is installed"
    } catch {
        Write-Error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    }
}

# Check if Docker is running
try {
    $null = docker info 2>$null
    Write-Status "Docker is running"
} catch {
    Write-Error "Docker is not running. Please start Docker Desktop."
    exit 1
}

# Environment setup
Write-Info "Setting up environment..."

# Create .env.local from example if it doesn't exist
if (-not (Test-Path $EnvFile)) {
    if (Test-Path ".env.local.example") {
        Copy-Item ".env.local.example" $EnvFile
        Write-Status "Created $EnvFile from example"
        Write-Warning "Please edit $EnvFile with your OpenAI API key and other settings"
    } else {
        Write-Error ".env.local.example not found"
        exit 1
    }
} else {
    Write-Status "Environment file exists"
}

# Check for OpenAI API key
$envContent = Get-Content $EnvFile -Raw
if ($envContent -notmatch "OPENAI_API_KEY=sk-") {
    Write-Warning "OpenAI API key not configured. P&ID analysis will run in demo mode."
}

# Clean up if requested
if ($Clean) {
    Write-Info "Performing clean startup..."
    docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName down --remove-orphans --volumes 2>$null
    docker system prune -f 2>$null
}

# Clean up previous containers
Write-Info "Cleaning up previous containers..."
docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName down --remove-orphans 2>$null
Write-Status "Previous containers cleaned up"

# Build and start services
Write-Info "Building and starting services..."

# Build without cache for fresh start
Write-Host "Building containers..." -ForegroundColor $Yellow
docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to build containers"
    exit 1
}

# Start databases first
Write-Info "Starting databases..."
docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName up -d postgres mongodb redis

# Wait for databases
Write-Host "⏳ Waiting for databases to be ready..." -ForegroundColor $Yellow
Start-Sleep -Seconds 15

# Start backend
Write-Info "Starting backend..."
docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName up -d backend

# Wait for backend
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor $Yellow
Start-Sleep -Seconds 25

# Start frontend  
Write-Info "Starting frontend..."
docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName up -d frontend

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor $Yellow
Start-Sleep -Seconds 30

# Health checks
Write-Info "Performing health checks..."

# Check backend health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health/" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Status "Backend is healthy"
    }
} catch {
    Write-Warning "Backend health check failed. Service may still be starting..."
}

# Check frontend health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Status "Frontend is healthy"
    }
} catch {
    Write-Warning "Frontend health check failed. Service may still be starting..."
}

# Display status
Write-Info "Service Status:"
docker-compose -f $ComposeFile --env-file $EnvFile -p $ProjectName ps

# Display URLs
Write-Host ""
Write-Status "EDRS P`&ID Analysis System is running!"
Write-Info "=================================================================="
Write-Info "Access URLs:"
Write-Host "   Frontend:     http://localhost:3001" -ForegroundColor White
Write-Host "   Backend API:  http://localhost:8001" -ForegroundColor White
Write-Host "   Admin Panel:  http://localhost:8001/admin" -ForegroundColor White
Write-Host "   API Docs:     http://localhost:8001/api/docs/" -ForegroundColor White
Write-Host ""
Write-Info "Default Admin User:"
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host "   Email:    admin@edrs.local" -ForegroundColor White
Write-Host ""
Write-Info "Database Access:"
Write-Host "   PostgreSQL:   localhost:5433" -ForegroundColor White
Write-Host "   MongoDB:      localhost:27018" -ForegroundColor White
Write-Host "   Redis:        localhost:6380" -ForegroundColor White
Write-Host ""
Write-Info "Next Steps:"
Write-Host "1. Open http://localhost:3001 in your browser" -ForegroundColor White
Write-Host "2. Login with admin credentials" -ForegroundColor White
Write-Host "3. Navigate to P&ID Analysis section" -ForegroundColor White
Write-Host "4. Upload a P&ID diagram to test the system" -ForegroundColor White
Write-Host ""
Write-Info "Useful Commands:"
Write-Host "   View logs:    .\start-docker-local.ps1 -Logs" -ForegroundColor White
Write-Host "   Stop all:     .\start-docker-local.ps1 -Stop" -ForegroundColor White
Write-Host "   Clean start:  .\start-docker-local.ps1 -Clean" -ForegroundColor White
Write-Host ""
Write-Status "Happy analyzing!"

# Ask if user wants to open browser
Write-Host ""
$openBrowser = Read-Host "Open application in browser? (Y/n)"
if ($openBrowser -ne "n" -and $openBrowser -ne "N") {
    Start-Process "http://localhost:3001"
}