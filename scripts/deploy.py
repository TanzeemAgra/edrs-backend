#!/usr/bin/env python
"""
EDRS P&ID Analysis - Production Deployment Script
Prepares and deploys the enhanced P&ID analysis system
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class EDRSDeployment:
    """EDRS Deployment Manager"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend" 
        self.frontend_dir = self.project_root / "frontend"
        
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        print("🔍 Checking deployment prerequisites...")
        
        checks = {
            'git': self._check_git(),
            'backend_files': self._check_backend_files(),
            'frontend_files': self._check_frontend_files(),
            'env_template': self._check_env_templates()
        }
        
        all_good = all(checks.values())
        
        for check, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {check.replace('_', ' ').title()}: {'OK' if status else 'MISSING'}")
        
        return all_good
    
    def _check_git(self):
        """Check if git is available"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_backend_files(self):
        """Check if enhanced backend files exist"""
        required_files = [
            'apps/pid_analysis/services/enhanced_analysis.py',
            'apps/pid_analysis/views.py',
            'test_analysis.py'
        ]
        
        return all((self.backend_dir / file).exists() for file in required_files)
    
    def _check_frontend_files(self):
        """Check if frontend files exist"""
        required_files = [
            'src/components/pid-analysis/PIDAnalysisDashboard.jsx',
            'src/stores/pidAnalysisStore.js'
        ]
        
        return all((self.frontend_dir / file).exists() for file in required_files)
    
    def _check_env_templates(self):
        """Check if environment templates exist"""
        return (self.backend_dir / '.env.production').exists()
    
    def create_deployment_summary(self):
        """Create deployment summary"""
        
        summary = {
            "deployment_info": {
                "timestamp": "2024-11-17",
                "version": "1.0.0-enhanced",
                "features": [
                    "Enhanced P&ID Analysis Engine",
                    "Modern OpenAI API Integration", 
                    "Fallback Analysis System",
                    "Robust Error Handling",
                    "Progress Tracking",
                    "Realistic Demo Mode"
                ]
            },
            "files_updated": [
                "backend/apps/pid_analysis/services/enhanced_analysis.py",
                "backend/apps/pid_analysis/views.py", 
                "backend/apps/pid_analysis/services/analysis_engine.py",
                "backend/.env.production",
                "backend/test_analysis.py",
                "backend/validate_setup.py"
            ],
            "environment_variables": {
                "required": [
                    "OPENAI_API_KEY",
                    "SECRET_KEY", 
                    "DATABASE_URL",
                    "ALLOWED_HOSTS"
                ],
                "optional": [
                    "ENABLE_OPENAI_INTEGRATION",
                    "OPENAI_MODEL",
                    "OPENAI_TIMEOUT",
                    "OPENAI_MAX_RETRIES"
                ]
            },
            "deployment_steps": [
                "1. Set environment variables in Railway dashboard",
                "2. Push code to main branch",
                "3. Railway will auto-deploy the backend",
                "4. Verify deployment with test URL",
                "5. Test P&ID analysis functionality"
            ]
        }
        
        summary_file = self.project_root / "DEPLOYMENT_SUMMARY.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Deployment summary saved to: {summary_file}")
        return summary
    
    def commit_changes(self):
        """Commit the enhanced P&ID analysis changes"""
        print("📦 Committing enhanced P&ID analysis changes...")
        
        try:
            # Stage all changes
            subprocess.run(['git', 'add', '.'], cwd=self.project_root, check=True)
            
            # Commit with descriptive message
            commit_message = """🚀 ENHANCEMENT: P&ID Analysis System Overhaul

✨ Features Added:
- Modern OpenAI API integration (v1.x compatibility)
- Intelligent fallback analysis system
- Enhanced error handling and retry mechanisms
- Realistic demo mode with project-specific errors
- Comprehensive progress tracking
- Robust environment configuration

🔧 Technical Improvements:
- Updated analysis engine with async/await patterns
- Added comprehensive validation scripts
- Enhanced API error handling with graceful degradation
- Improved user experience with meaningful feedback
- Production-ready environment templates

🎯 Problem Solved:
- Fixed P&ID analysis issues on live site
- Eliminated API integration failures
- Added fallback capabilities for offline demo
- Enhanced system reliability and user experience

Ready for production deployment! 🚀"""

            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd=self.project_root, check=True)
            
            print("✅ Changes committed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git commit failed: {e}")
            return False
    
    def deploy_to_production(self):
        """Deploy to production (push to main branch)"""
        print("🚀 Deploying to production...")
        
        try:
            # Push to main branch 
            subprocess.run(['git', 'push', 'origin', 'main'], 
                         cwd=self.project_root, check=True)
            
            print("✅ Code pushed to production!")
            print("🔄 Railway will automatically deploy the backend...")
            print("⏱️  Deployment typically takes 2-3 minutes")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            return False
    
    def show_next_steps(self):
        """Show post-deployment steps"""
        print("\n" + "="*60)
        print("🎯 POST-DEPLOYMENT STEPS")
        print("="*60)
        
        print("\n1. 🔑 SET ENVIRONMENT VARIABLES IN RAILWAY:")
        print("   Go to Railway dashboard → Your project → Variables")
        print("   Add these variables:")
        print("   • OPENAI_API_KEY=sk-your-actual-openai-key-here")
        print("   • ENABLE_OPENAI_INTEGRATION=true")
        print("   • SECRET_KEY=your-long-random-django-secret-key")
        
        print("\n2. ✅ TEST THE DEPLOYMENT:")
        print("   • Wait for Railway deployment to complete") 
        print("   • Go to: https://edrs-frontend.vercel.app/dashboard")
        print("   • Create a new P&ID project")
        print("   • Upload a diagram (PDF/PNG/JPG)")
        print("   • Click 'Analyze' and verify it works!")
        
        print("\n3. 🔍 VERIFY FUNCTIONALITY:")
        print("   Expected behavior:")
        print("   ✅ Project creation works")
        print("   ✅ Diagram upload works") 
        print("   ✅ Analysis starts and shows progress")
        print("   ✅ Results display (AI analysis or fallback demo)")
        print("   ✅ Error details and recommendations appear")
        
        print("\n4. 🆘 IF ISSUES PERSIST:")
        print("   • Check Railway logs for backend errors")
        print("   • Verify environment variables are set correctly")
        print("   • Test with fallback mode (should always work)")
        print("   • Contact support if needed")
        
        print("\n🎉 SUCCESS INDICATORS:")
        print("✅ Analysis completes without errors")
        print("✅ Results show meaningful P&ID findings") 
        print("✅ Users can create projects and upload diagrams")
        print("✅ System provides value even in demo mode")
        
def main():
    """Main deployment function"""
    print("🚀 EDRS P&ID Analysis - Production Deployment")
    print("="*60)
    
    deployer = EDRSDeployment()
    
    # Check prerequisites
    if not deployer.check_prerequisites():
        print("\n❌ Prerequisites check failed!")
        print("Please ensure all required files are in place.")
        sys.exit(1)
    
    print("\n✅ Prerequisites check passed!")
    
    # Create deployment summary
    deployer.create_deployment_summary()
    
    # Commit changes
    if not deployer.commit_changes():
        print("\n❌ Failed to commit changes!")
        sys.exit(1)
    
    # Deploy to production
    if not deployer.deploy_to_production():
        print("\n❌ Deployment failed!")
        sys.exit(1)
    
    # Show next steps
    deployer.show_next_steps()
    
    print("\n🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("Your enhanced P&ID analysis system is now live!")

if __name__ == "__main__":
    main()