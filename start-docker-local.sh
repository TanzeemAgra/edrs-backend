#!/bin/bash

# EDRS Docker Local Environment Startup Script
# Automated deployment with smart dependency management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.local.yml"
ENV_FILE=".env.local"
PROJECT_NAME="edrs-local"

echo -e "${BLUE}🚀 EDRS P&ID Analysis System - Docker Local Deployment${NC}"
echo "=================================================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop."
    exit 1
fi
print_status "Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi
print_status "Docker Compose is installed"

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi
print_status "Docker is running"

# Environment setup
echo -e "${BLUE}🔧 Setting up environment...${NC}"

# Create .env.local from example if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    if [ -f ".env.local.example" ]; then
        cp .env.local.example "$ENV_FILE"
        print_status "Created $ENV_FILE from example"
        print_warning "Please edit $ENV_FILE with your OpenAI API key and other settings"
    else
        print_error ".env.local.example not found"
        exit 1
    fi
else
    print_status "Environment file exists"
fi

# Check for OpenAI API key
if ! grep -q "OPENAI_API_KEY=sk-" "$ENV_FILE" 2>/dev/null; then
    print_warning "OpenAI API key not configured. P&ID analysis will run in demo mode."
fi

# Clean up previous containers (optional)
echo -e "${BLUE}🧹 Cleaning up previous containers...${NC}"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" down --remove-orphans 2>/dev/null || true
print_status "Previous containers cleaned up"

# Build and start services
echo -e "${BLUE}🏗️ Building and starting services...${NC}"

# Build without cache for fresh start
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" build --no-cache

# Start databases first
echo -e "${YELLOW}📊 Starting databases...${NC}"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" up -d postgres mongodb redis

# Wait for databases
echo -e "${YELLOW}⏳ Waiting for databases to be ready...${NC}"
sleep 10

# Check database health
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" exec -T "$service" echo "Health check" &> /dev/null; then
            return 0
        fi
        echo -e "${YELLOW}Attempt $attempt/$max_attempts: Waiting for $service...${NC}"
        sleep 2
        ((attempt++))
    done
    return 1
}

# Wait for postgres
if check_health postgres; then
    print_status "PostgreSQL is ready"
else
    print_error "PostgreSQL failed to start"
    exit 1
fi

# Wait for redis
if check_health redis; then
    print_status "Redis is ready"
else
    print_error "Redis failed to start"
    exit 1
fi

# Start backend
echo -e "${YELLOW}🔧 Starting backend...${NC}"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" up -d backend

# Wait for backend
sleep 15

# Start frontend
echo -e "${YELLOW}🎨 Starting frontend...${NC}"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" up -d frontend

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 20

# Health checks
echo -e "${BLUE}🏥 Performing health checks...${NC}"

# Check backend health
if curl -f -s http://localhost:8001/health/ > /dev/null; then
    print_status "Backend is healthy"
else
    print_warning "Backend health check failed. Service may still be starting..."
fi

# Check frontend health
if curl -f -s http://localhost:3001 > /dev/null; then
    print_status "Frontend is healthy"
else
    print_warning "Frontend health check failed. Service may still be starting..."
fi

# Display status
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" ps

# Display URLs
echo ""
echo -e "${GREEN}🎉 EDRS P&ID Analysis System is running!${NC}"
echo "=================================================================="
echo -e "${BLUE}🌐 Access URLs:${NC}"
echo "   Frontend:     http://localhost:3001"
echo "   Backend API:  http://localhost:8001"
echo "   Admin Panel:  http://localhost:8001/admin"
echo "   API Docs:     http://localhost:8001/api/docs/"
echo ""
echo -e "${BLUE}👤 Default Admin User:${NC}"
echo "   Username: admin"
echo "   Password: admin123"
echo "   Email:    admin@edrs.local"
echo ""
echo -e "${BLUE}📊 Database Access:${NC}"
echo "   PostgreSQL:   localhost:5433"
echo "   MongoDB:      localhost:27018"
echo "   Redis:        localhost:6380"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Open http://localhost:3001 in your browser"
echo "2. Login with admin credentials"
echo "3. Navigate to P&ID Analysis section"
echo "4. Upload a P&ID diagram to test the system"
echo ""
echo -e "${YELLOW}🛠️ Useful Commands:${NC}"
echo "   View logs:    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE -p $PROJECT_NAME logs -f"
echo "   Stop all:     docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE -p $PROJECT_NAME down"
echo "   Restart:      docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE -p $PROJECT_NAME restart"
echo "   Shell access: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE -p $PROJECT_NAME exec <service> /bin/bash"
echo ""
echo -e "${GREEN}✨ Happy analyzing! 🏗️📊${NC}"