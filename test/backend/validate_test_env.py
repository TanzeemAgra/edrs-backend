#!/usr/bin/env python3
"""
EDRS Test Environment Validator
Validates that the test environment is properly configured
"""

import os
import sys
from pathlib import Path
import subprocess
import json

class TestEnvironmentValidator:
    def __init__(self):
        self.test_root = Path(__file__).parent
        self.project_root = self.test_root.parent
        self.errors = []
        self.warnings = []
        
    def validate_files(self):
        """Validate all required test files exist"""
        print("🔍 Validating Test Environment Files...")
        
        required_files = [
            "docker-compose.test.yml",
            ".env.test", 
            "Dockerfile.backend.test",
            "Dockerfile.frontend.test",
            "Dockerfile.test-runner",
            "test-manager.py",
            "TEST_ENVIRONMENT_GUIDE.md"
        ]
        
        for file_name in required_files:
            file_path = self.test_root / file_name
            if file_path.exists():
                print(f"✅ {file_name}")
            else:
                self.errors.append(f"Missing required file: {file_name}")
                print(f"❌ {file_name}")
        
        # Check scripts directory
        scripts_dir = self.test_root / "scripts"
        if scripts_dir.exists():
            print("✅ scripts/ directory")
            
            required_scripts = [
                "health_check.sh",
                "wait_for_services.sh", 
                "run_backend_tests.sh",
                "run_frontend_tests.sh"
            ]
            
            for script in required_scripts:
                script_path = scripts_dir / script
                if script_path.exists():
                    print(f"✅ scripts/{script}")
                else:
                    self.errors.append(f"Missing script: {script}")
                    print(f"❌ scripts/{script}")
        else:
            self.errors.append("Missing scripts/ directory")
            print("❌ scripts/ directory")
    
    def validate_docker_config(self):
        """Validate Docker configuration"""
        print("\n🐳 Validating Docker Configuration...")
        
        # Check Docker availability
        try:
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
            print("✅ Docker available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append("Docker not available")
            print("❌ Docker not available")
        
        try:
            subprocess.run(["docker-compose", "--version"], 
                         capture_output=True, check=True)
            print("✅ Docker Compose available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append("Docker Compose not available")  
            print("❌ Docker Compose not available")
        
        # Validate compose file syntax
        compose_file = self.test_root / "docker-compose.test.yml"
        if compose_file.exists():
            try:
                result = subprocess.run([
                    "docker-compose", "-f", str(compose_file),
                    "config"
                ], capture_output=True, check=True, cwd=self.test_root)
                print("✅ Docker Compose syntax valid")
            except subprocess.CalledProcessError as e:
                self.errors.append(f"Docker Compose syntax error: {e}")
                print("❌ Docker Compose syntax invalid")
    
    def validate_env_config(self):
        """Validate environment configuration"""
        print("\n⚙️  Validating Environment Configuration...")
        
        env_file = self.test_root / ".env.test"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    env_content = f.read()
                
                required_vars = [
                    "TEST_POSTGRES_DB",
                    "TEST_POSTGRES_USER", 
                    "TEST_POSTGRES_PASSWORD",
                    "TEST_MONGO_DB",
                    "TEST_REDIS_URL",
                    "DJANGO_SETTINGS_MODULE"
                ]
                
                for var in required_vars:
                    if var in env_content:
                        print(f"✅ {var}")
                    else:
                        self.warnings.append(f"Missing environment variable: {var}")
                        print(f"⚠️  {var}")
                        
            except Exception as e:
                self.errors.append(f"Error reading .env.test: {e}")
                print("❌ Error reading .env.test")
        
    def validate_network_config(self):
        """Validate network configuration for isolation"""
        print("\n🌐 Validating Network Isolation...")
        
        compose_file = self.test_root / "docker-compose.test.yml"
        if compose_file.exists():
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    compose_content = f.read()
                
                # Check for test network
                if "edrs_test_network" in compose_content:
                    print("✅ Test network configured")
                else:
                    self.warnings.append("Test network not found")
                    print("⚠️  Test network not configured")
                
                # Check for isolated ports
                test_ports = ["3002", "8002", "5434", "27019", "6381"]
                for port in test_ports:
                    if port in compose_content:
                        print(f"✅ Test port {port} configured")
                    else:
                        self.warnings.append(f"Test port {port} not found")
                        print(f"⚠️  Test port {port} not configured")
                        
            except Exception as e:
                self.errors.append(f"Error validating network config: {e}")
    
    def validate_isolation(self):
        """Validate isolation from dev/prod"""
        print("\n🔒 Validating Environment Isolation...")
        
        # Check that we're not using dev ports
        dev_ports = ["3001", "8001", "5433", "27018", "6380"]
        compose_file = self.test_root / "docker-compose.test.yml"
        
        if compose_file.exists():
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    compose_content = f.read()
                
                conflicts = []
                for port in dev_ports:
                    if f":{port}" in compose_content:
                        conflicts.append(port)
                
                if conflicts:
                    self.errors.append(f"Port conflicts with dev environment: {conflicts}")
                    print(f"❌ Port conflicts detected: {conflicts}")
                else:
                    print("✅ No port conflicts with development")
                    
            except Exception as e:
                self.errors.append(f"Error checking isolation: {e}")
    
    def generate_report(self):
        """Generate validation report"""
        print("\n📊 Test Environment Validation Report")
        print("=" * 50)
        
        if not self.errors and not self.warnings:
            print("🎉 Test environment is properly configured!")
            print("✅ All validations passed")
            print("🚀 Ready to run: python test-manager.py setup")
            return True
        
        if self.errors:
            print("❌ ERRORS (must fix):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("⚠️  WARNINGS (recommended fixes):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("\n📚 Next Steps:")
        if self.errors:
            print("1. Fix the errors listed above")
            print("2. Re-run this validation")
        else:
            print("1. Review warnings (optional)")
            print("2. Run: python test-manager.py setup")
        
        print("3. Refer to TEST_ENVIRONMENT_GUIDE.md for details")
        
        return len(self.errors) == 0

def main():
    print("🧪 EDRS Test Environment Validator")
    print("===================================")
    
    validator = TestEnvironmentValidator()
    
    validator.validate_files()
    validator.validate_docker_config()
    validator.validate_env_config()
    validator.validate_network_config() 
    validator.validate_isolation()
    
    success = validator.generate_report()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()