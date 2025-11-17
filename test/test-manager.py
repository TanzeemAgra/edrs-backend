"""
EDRS Test Environment Management Script
Smart automation for isolated Docker test environment
Maintains complete separation from production and development
"""

import os
import sys
import subprocess
import time
import json
import argparse
from pathlib import Path

class EDRSTestManager:
    def __init__(self):
        self.test_root = Path(__file__).parent  # test folder
        self.project_root = self.test_root.parent  # EDRS root
        self.compose_file = self.test_root / "docker-compose.test.yml"
        self.env_file = self.test_root / ".env.test"
        self.reports_dir = self.test_root / "reports"
        
    def setup_environment(self):
        """Setup isolated test environment configuration"""
        print("🧪 Setting up EDRS Test Environment...")
        print("🔒 Isolated from production and development")
        
        # Validate test environment file exists
        if not self.env_file.exists():
            print(f"❌ Test environment file not found: {self.env_file}")
            print("The .env.test file should have been created during test setup.")
            return False
        
        # Create test directories
        directories = [
            self.test_root / "reports",
            self.test_root / "reports" / "backend",
            self.test_root / "reports" / "frontend", 
            self.test_root / "reports" / "integration",
            self.test_root / "reports" / "performance",
            self.test_root / "logs",
            self.test_root / "temp_data",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created test directory: {directory}")
        
        print("✅ Test environment setup complete!")
        return True
    
    def check_docker(self):
        """Check if Docker is running"""
        try:
            subprocess.run(["docker", "version"], 
                         capture_output=True, check=True)
            subprocess.run(["docker-compose", "version"], 
                         capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker or Docker Compose not available!")
            print("Please ensure Docker Desktop is running.")
            return False
    
    def build_services(self, services=None):
        """Build isolated test Docker services"""
        print("🏗️  Building EDRS Test Services...")
        print("🔒 Using test-specific containers and network")
        
        cmd = ["docker-compose", "-f", str(self.compose_file)]
        cmd.extend(["--env-file", str(self.env_file)])
        cmd.extend(["--project-name", "edrs-test"])
        
        cmd.append("build")
        if services:
            cmd.extend(services)
        
        try:
            subprocess.run(cmd, check=True, cwd=self.test_root)
            print("✅ Test services built successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Test build failed: {e}")
            return False
    
    def start_services(self, services=None, detached=True):
        """Start isolated test Docker services"""
        print("🚀 Starting EDRS Test Environment...")
        print("🔒 Isolated network and ports (no conflicts with dev/prod)")
        
        cmd = ["docker-compose", "-f", str(self.compose_file)]
        cmd.extend(["--env-file", str(self.env_file)])
        cmd.extend(["--project-name", "edrs-test"])
        
        cmd.append("up")
        if detached:
            cmd.append("-d")
        
        if services:
            cmd.extend(services)
        
        try:
            subprocess.run(cmd, check=True, cwd=self.test_root)
            print("✅ Test services started successfully!")
            self.show_service_urls()
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start test services: {e}")
            return False
    
    def stop_services(self):
        """Stop isolated test Docker services"""
        print("🛑 Stopping EDRS Test Environment...")
        
        cmd = ["docker-compose", "-f", str(self.compose_file)]
        cmd.extend(["--env-file", str(self.env_file)])
        cmd.extend(["--project-name", "edrs-test"])
        cmd.append("down")
        
        try:
            subprocess.run(cmd, check=True, cwd=self.test_root)
            print("✅ Test services stopped successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop test services: {e}")
            return False
    
    def show_logs(self, service=None, follow=False):
        """Show service logs"""
        cmd = ["docker-compose", "-f", str(self.compose_file)]
        if self.env_file.exists():
            cmd.extend(["--env-file", str(self.env_file)])
        
        cmd.append("logs")
        if follow:
            cmd.append("-f")
        
        if service:
            cmd.append(service)
        
        try:
            subprocess.run(cmd, cwd=self.project_root)
        except KeyboardInterrupt:
            print("\n👋 Log viewing stopped.")
    
    def show_status(self):
        """Show service status"""
        print("📊 EDRS Service Status:")
        
        cmd = ["docker-compose", "-f", str(self.compose_file)]
        if self.env_file.exists():
            cmd.extend(["--env-file", str(self.env_file)])
        cmd.append("ps")
        
        try:
            subprocess.run(cmd, cwd=self.project_root)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get status: {e}")
    
    def show_service_urls(self):
        """Display test service URLs"""
        print("\n🧪 EDRS Test Environment URLs:")
        print("=" * 55)
        print("🎯 Frontend:     http://localhost:3002 (TEST)")
        print("🔧 Backend:      http://localhost:8002 (TEST)")
        print("📚 API Docs:     http://localhost:8002/api/docs/")
        print("👤 Admin:        http://localhost:8002/admin/")
        print("🔍 Health:       http://localhost:8002/health/")
        print("📊 Test Runner:  Check Docker logs for results")
        print("=" * 55)
        print("📊 Test Database Ports:")
        print("   PostgreSQL:   localhost:5434 (TEST)")
        print("   MongoDB:      localhost:27019 (TEST)")
        print("   Redis:        localhost:6381 (TEST)")
        print("=" * 55)
        print("🔒 Isolated from dev (ports 3001, 8001, 5433, 27018, 6380)")
        print("🔒 Isolated from prod (standard ports)")
        print("=" * 55)
    
    def reset_environment(self):
        """Reset the entire local environment"""
        print("🔄 Resetting EDRS Local Environment...")
        
        # Stop and remove containers
        cmd = ["docker-compose", "-f", str(self.compose_file)]
        if self.env_file.exists():
            cmd.extend(["--env-file", str(self.env_file)])
        cmd.extend(["down", "-v", "--remove-orphans"])
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print("✅ Containers and volumes removed!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: {e}")
        
        # Remove images
        print("🗑️  Removing EDRS images...")
        try:
            subprocess.run(["docker", "rmi", "edrs_backend_local", "edrs_frontend_local"], 
                         capture_output=True, check=True)
            print("✅ Images removed!")
        except subprocess.CalledProcessError:
            print("ℹ️  No images to remove or removal failed.")
    
    def run_comprehensive_tests(self, test_suite="full"):
        """Run comprehensive test suite in isolated environment"""
        print("🧪 Running EDRS Comprehensive Test Suite...")
        print(f"📋 Test Suite: {test_suite}")
        print("🔒 Isolated test environment (no impact on dev/prod)")
        
        # Start test runner container
        test_cmd = [
            "docker-compose", "-f", str(self.compose_file),
            "--env-file", str(self.env_file),
            "--project-name", "edrs-test",
            "run", "--rm"
        ]
        
        # Set test suite environment variable
        test_cmd.extend(["-e", f"TEST_SUITE={test_suite}"])
        test_cmd.extend(["-e", "TEST_PARALLEL=true"])
        test_cmd.extend(["-e", "TEST_VERBOSE=true"])
        test_cmd.append("test-runner")
        
        try:
            print("🚀 Starting comprehensive test execution...")
            result = subprocess.run(test_cmd, cwd=self.test_root)
            
            if result.returncode == 0:
                print("🎉 All tests passed successfully!")
                self.show_test_reports()
            else:
                print("💥 Some tests failed. Check reports for details.")
                self.show_test_reports()
            
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Test execution failed: {e}")
            return False
    
    def show_test_reports(self):
        """Display test report locations"""
        print("\n📊 Test Reports Available:")
        print("=" * 40)
        if self.reports_dir.exists():
            for report_type in ["backend", "frontend", "integration", "performance"]:
                report_path = self.reports_dir / report_type
                if report_path.exists():
                    print(f"📈 {report_type.title()}: {report_path}")
        print("=" * 40)

def main():
    parser = argparse.ArgumentParser(description='EDRS Test Environment Manager - Isolated Testing')
    parser.add_argument('command', choices=[
        'setup', 'build', 'start', 'stop', 'restart', 
        'status', 'logs', 'reset', 'test', 'urls', 'clean'
    ], help='Command to execute')
    
    parser.add_argument('--service', help='Specific service to target')
    parser.add_argument('--follow', '-f', action='store_true', help='Follow logs')
    parser.add_argument('--no-detach', action='store_true', help='Run in foreground')
    parser.add_argument('--test-suite', choices=['full', 'backend', 'frontend', 'integration', 'performance'], 
                       default='full', help='Test suite to run')
    
    args = parser.parse_args()
    
    manager = EDRSTestManager()
    
    # Check Docker availability for most commands
    if args.command != 'setup' and not manager.check_docker():
        sys.exit(1)
    
    if args.command == 'setup':
        if manager.setup_environment():
            print("\n🎉 Test environment setup complete! Next steps:")
            print("1. Run: python test-manager.py build")
            print("2. Run: python test-manager.py start") 
            print("3. Run: python test-manager.py test")
            print("\n🔒 Fully isolated from development and production!")
    
    elif args.command == 'build':
        services = [args.service] if args.service else None
        manager.build_services(services)
    
    elif args.command == 'start':
        services = [args.service] if args.service else None
        detached = not args.no_detach
        manager.start_services(services, detached)
    
    elif args.command == 'stop':
        manager.stop_services()
    
    elif args.command == 'restart':
        manager.stop_services()
        time.sleep(2)
        manager.start_services()
    
    elif args.command == 'status':
        manager.show_status()
    
    elif args.command == 'logs':
        manager.show_logs(args.service, args.follow)
    
    elif args.command == 'reset':
        confirm = input("⚠️  This will delete all TEST data (isolated from dev/prod). Continue? (y/N): ")
        if confirm.lower() == 'y':
            manager.reset_environment()
    
    elif args.command == 'test':
        manager.run_comprehensive_tests(args.test_suite)
    
    elif args.command == 'urls':
        manager.show_service_urls()
    
    elif args.command == 'clean':
        print("🧹 Cleaning test environment...")
        manager.stop_services()
        time.sleep(1)
        manager.reset_environment()

if __name__ == '__main__':
    main()