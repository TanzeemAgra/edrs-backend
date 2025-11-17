#!/usr/bin/env python3
"""
EDRS Development Server Startup Script
Starts both backend and frontend servers with proper configuration
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path
import requests
import json

class EDRSDevServer:
    """EDRS Development Server Manager"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.processes = []
        self.running = False
        
    def check_ports(self):
        """Check if required ports are available"""
        print("🔍 Checking port availability...")
        
        ports_to_check = [8000, 3000]
        for port in ports_to_check:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    print(f"  ⚠️  Port {port} is already in use")
                    if port == 8000:
                        print("     Django backend might already be running")
                    elif port == 3000:
                        print("     Frontend dev server might already be running")
                else:
                    print(f"  ✅ Port {port} is available")
                    
            except Exception as e:
                print(f"  ❌ Error checking port {port}: {e}")
    
    def setup_environment(self):
        """Setup environment variables and check configuration"""
        print("⚙️  Setting up environment...")
        
        # Check backend .env file
        backend_env = self.backend_dir / ".env"
        if not backend_env.exists():
            print("  ⚠️  Backend .env file not found, creating one...")
            self.create_backend_env()
        else:
            print("  ✅ Backend .env file exists")
        
        # Check frontend .env file
        frontend_env = self.frontend_dir / ".env"
        if not frontend_env.exists():
            print("  ⚠️  Frontend .env file not found, creating one...")
            self.create_frontend_env()
        else:
            print("  ✅ Frontend .env file exists")
            
        # Verify API URL configuration
        self.verify_api_config()
    
    def create_backend_env(self):
        """Create backend .env file with correct configuration"""
        env_content = """# Development Environment Variables
SECRET_KEY=django-insecure-dev-key-change-in-production-very-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# OpenAI Configuration (Optional - for P&ID analysis)
OPENAI_API_KEY=your-openai-key-here
ENABLE_OPENAI_INTEGRATION=false
OPENAI_MODEL=gpt-4o
"""
        
        backend_env = self.backend_dir / ".env"
        with open(backend_env, 'w') as f:
            f.write(env_content)
        print("  ✅ Created backend .env file")
    
    def create_frontend_env(self):
        """Create frontend .env file with correct configuration"""
        env_content = """# EDRS Frontend Environment Configuration

# API Configuration  
VITE_API_URL=http://localhost:8000/api
VITE_DEV_API_URL=http://localhost:8000/api
VITE_API_BASE_URL=http://localhost:8000

# App Configuration
VITE_APP_NAME=EDRS
VITE_APP_VERSION=1.0.0-dev
VITE_APP_DESCRIPTION=Electronic Document Recording System

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_NOTIFICATIONS=true
"""
        
        frontend_env = self.frontend_dir / ".env"
        with open(frontend_env, 'w') as f:
            f.write(env_content)
        print("  ✅ Created frontend .env file")
    
    def verify_api_config(self):
        """Verify API configuration consistency"""
        try:
            frontend_env = self.frontend_dir / ".env"
            if frontend_env.exists():
                with open(frontend_env, 'r') as f:
                    content = f.read()
                    if "localhost:8000" in content:
                        print("  ✅ Frontend API URL correctly configured for port 8000")
                    else:
                        print("  ⚠️  Frontend API URL might be misconfigured")
        except Exception as e:
            print(f"  ❌ Error verifying API config: {e}")
    
    def start_backend(self):
        """Start Django backend server"""
        print("🚀 Starting Django backend server...")
        
        try:
            os.chdir(self.backend_dir)
            
            # Run migrations first
            print("  📊 Running database migrations...")
            migration_process = subprocess.run(
                [sys.executable, "manage.py", "migrate"],
                capture_output=True,
                text=True
            )
            
            if migration_process.returncode != 0:
                print(f"  ⚠️  Migration warnings: {migration_process.stderr}")
            else:
                print("  ✅ Database migrations completed")
            
            # Start Django server
            backend_process = subprocess.Popen(
                [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            self.processes.append(backend_process)
            
            # Monitor backend startup in separate thread
            threading.Thread(
                target=self.monitor_backend_output,
                args=(backend_process,),
                daemon=True
            ).start()
            
            print("  ✅ Django backend server started on http://localhost:8000")
            
        except Exception as e:
            print(f"  ❌ Failed to start backend: {e}")
            return False
            
        return True
    
    def monitor_backend_output(self, process):
        """Monitor backend server output"""
        for line in iter(process.stdout.readline, ''):
            if "Starting development server" in line:
                print("  🎉 Backend server is ready!")
            elif "Quit the server with CONTROL-C" in line:
                print("  📡 Backend API available at http://localhost:8000/api/")
            elif "error" in line.lower() or "exception" in line.lower():
                print(f"  ⚠️  Backend: {line.strip()}")
    
    def start_frontend(self):
        """Start React frontend server"""
        print("🚀 Starting React frontend server...")
        
        try:
            os.chdir(self.frontend_dir)
            
            # Check if node_modules exists
            if not (self.frontend_dir / "node_modules").exists():
                print("  📦 Installing frontend dependencies...")
                install_process = subprocess.run(
                    ["npm", "install"],
                    capture_output=True,
                    text=True
                )
                
                if install_process.returncode != 0:
                    print(f"  ❌ Failed to install dependencies: {install_process.stderr}")
                    return False
                else:
                    print("  ✅ Frontend dependencies installed")
            
            # Start Vite dev server
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            self.processes.append(frontend_process)
            
            # Monitor frontend startup
            threading.Thread(
                target=self.monitor_frontend_output,
                args=(frontend_process,),
                daemon=True
            ).start()
            
            print("  ✅ React frontend server started")
            
        except Exception as e:
            print(f"  ❌ Failed to start frontend: {e}")
            return False
            
        return True
    
    def monitor_frontend_output(self, process):
        """Monitor frontend server output"""
        for line in iter(process.stdout.readline, ''):
            if "Local:" in line and "localhost:3000" in line:
                print("  🎉 Frontend server is ready!")
                print("  🌐 Open http://localhost:3000 in your browser")
            elif "error" in line.lower() and "warning" not in line.lower():
                print(f"  ⚠️  Frontend: {line.strip()}")
    
    def wait_for_backend(self, timeout=30):
        """Wait for backend to be ready"""
        print("⏳ Waiting for backend to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://localhost:8000/health/", timeout=2)
                if response.status_code == 200:
                    print("  ✅ Backend is ready and responding")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            print("  ⏳ Still waiting for backend...")
        
        print("  ⚠️  Backend is taking longer than expected to start")
        return False
    
    def show_status(self):
        """Show server status and useful URLs"""
        print("\n" + "="*60)
        print("🎉 EDRS Development Servers Status")
        print("="*60)
        
        print("\n📡 Server URLs:")
        print("  • Frontend:  http://localhost:3000")
        print("  • Backend:   http://localhost:8000")
        print("  • Admin:     http://localhost:8000/admin/")
        print("  • API Docs:  http://localhost:8000/api/docs/")
        
        print("\n🧪 Test URLs:")
        print("  • Health Check:    http://localhost:8000/health/")
        print("  • P&ID Dashboard:  http://localhost:3000/pid-analysis")
        print("  • Main Dashboard:  http://localhost:3000/dashboard")
        
        print("\n💡 Quick Commands:")
        print("  • Stop servers:    Press Ctrl+C")
        print("  • Restart:         Run this script again")
        print("  • View logs:       Check the terminal output")
        
        if self.wait_for_backend():
            print("\n✅ All systems are GO! You can now:")
            print("  1. 🌐 Open http://localhost:3000 in your browser")
            print("  2. 📝 Create a P&ID project")
            print("  3. 📤 Upload diagrams")
            print("  4. ⚡ Test the analysis system")
    
    def cleanup(self, signum=None, frame=None):
        """Clean up processes"""
        print("\n🛑 Shutting down servers...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass
        
        print("✅ Servers stopped successfully")
        sys.exit(0)
    
    def run(self):
        """Main run function"""
        print("🚀 EDRS Development Server Startup")
        print("=" * 60)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        # Pre-flight checks
        self.check_ports()
        self.setup_environment()
        
        print("\n🔥 Starting servers...")
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend server")
            return
        
        # Wait a bit for backend to initialize
        time.sleep(3)
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend server")
            self.cleanup()
            return
        
        # Wait for both servers to be ready
        time.sleep(5)
        
        # Show status
        self.show_status()
        
        # Keep running
        self.running = True
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

if __name__ == "__main__":
    server = EDRSDevServer()
    server.run()