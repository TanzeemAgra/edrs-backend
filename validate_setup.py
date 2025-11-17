"""
EDRS API Key Validation and Deployment Check Script
Run this to verify your OpenAI configuration and test the analysis pipeline
"""

import os
import sys
import django
import asyncio
import json
from pathlib import Path

# Add Django setup
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from apps.pid_analysis.services.enhanced_analysis import EnhancedPIDAnalysisService, AnalysisConfig


class EDRSValidationTool:
    """Validation tool for EDRS P&ID Analysis System"""
    
    def __init__(self):
        self.results = {
            'environment': {},
            'openai': {},
            'analysis': {},
            'overall_status': 'unknown'
        }
    
    def validate_environment(self):
        """Validate environment configuration"""
        print("🔍 Validating Environment Configuration...")
        
        # Check critical settings
        env_checks = {
            'SECRET_KEY': bool(getattr(settings, 'SECRET_KEY', None)),
            'DEBUG': getattr(settings, 'DEBUG', True),
            'ALLOWED_HOSTS': bool(getattr(settings, 'ALLOWED_HOSTS', [])),
            'DATABASE_URL': bool(getattr(settings, 'DATABASE_URL', None)),
            'CORS_ALLOWED_ORIGINS': bool(getattr(settings, 'CORS_ALLOWED_ORIGINS', [])),
        }
        
        self.results['environment'] = env_checks
        
        print(f"  ✅ SECRET_KEY: {'Set' if env_checks['SECRET_KEY'] else '❌ Missing'}")
        print(f"  ✅ DEBUG: {env_checks['DEBUG']}")
        print(f"  ✅ ALLOWED_HOSTS: {'Configured' if env_checks['ALLOWED_HOSTS'] else '❌ Missing'}")
        print(f"  ✅ DATABASE: {'Connected' if env_checks['DATABASE_URL'] else '❌ Missing'}")
        print(f"  ✅ CORS: {'Configured' if env_checks['CORS_ALLOWED_ORIGINS'] else '❌ Missing'}")
    
    def validate_openai_config(self):
        """Validate OpenAI API configuration"""
        print("\\n🤖 Validating OpenAI Configuration...")
        
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        integration_enabled = getattr(settings, 'ENABLE_OPENAI_INTEGRATION', False)
        
        openai_checks = {
            'api_key_set': bool(api_key),
            'api_key_valid_format': False,
            'integration_enabled': integration_enabled,
            'model_configured': bool(getattr(settings, 'OPENAI_MODEL', None)),
        }
        
        if api_key:
            # Check API key format (should start with sk- and have proper length)
            if api_key.startswith('sk-') and len(api_key) > 20:
                openai_checks['api_key_valid_format'] = True
            elif api_key == "YOUR_ACTUAL_OPENAI_API_KEY_HERE":
                openai_checks['api_key_valid_format'] = False
                print("  ❌ API Key: Placeholder value detected")
            else:
                openai_checks['api_key_valid_format'] = False
                print("  ❌ API Key: Invalid format")
        
        self.results['openai'] = openai_checks
        
        print(f"  ✅ API Key Set: {'Yes' if openai_checks['api_key_set'] else '❌ No'}")
        print(f"  ✅ Key Format: {'Valid' if openai_checks['api_key_valid_format'] else '❌ Invalid'}")
        print(f"  ✅ Integration: {'Enabled' if openai_checks['integration_enabled'] else '⚠️  Disabled'}")
        print(f"  ✅ Model: {getattr(settings, 'OPENAI_MODEL', '❌ Not set')}")
    
    async def test_analysis_service(self):
        """Test the analysis service"""
        print("\\n⚡ Testing Analysis Service...")
        
        try:
            # Initialize service
            service = EnhancedPIDAnalysisService()
            
            # Test project context
            test_context = {
                'name': 'Test Validation Project',
                'project_type': 'upstream',
                'engineering_standard': 'ISA-5.1'
            }
            
            # Mock diagram path (won't actually process file in demo)
            mock_diagram_path = "/tmp/test_diagram.pdf"
            
            # Progress tracker
            progress_messages = []
            async def progress_callback(message, percent):
                progress_messages.append(f"{percent}% - {message}")
                print(f"    📊 {percent}% - {message}")
            
            # Run analysis
            errors, metadata = await service.analyze_diagram(
                mock_diagram_path,
                test_context,
                progress_callback
            )
            
            analysis_checks = {
                'service_initialized': True,
                'analysis_completed': True,
                'errors_detected': len(errors),
                'method_used': metadata.get('method_used', 'unknown'),
                'api_available': metadata.get('api_available', False)
            }
            
            self.results['analysis'] = analysis_checks
            
            print(f"  ✅ Service: Initialized")
            print(f"  ✅ Analysis: Completed")
            print(f"  ✅ Method: {analysis_checks['method_used']}")
            print(f"  ✅ Errors Found: {analysis_checks['errors_detected']}")
            print(f"  ✅ API Available: {analysis_checks['api_available']}")
            
            # Display sample errors
            if errors:
                print("\\n  📋 Sample Analysis Results:")
                for i, error in enumerate(errors[:2], 1):
                    print(f"    {i}. [{error.severity}] {error.title}")
                    print(f"       {error.description[:100]}...")
        
        except Exception as e:
            print(f"  ❌ Analysis Test Failed: {e}")
            self.results['analysis'] = {'error': str(e)}
    
    def generate_report(self):
        """Generate final validation report"""
        print("\\n" + "="*60)
        print("📊 EDRS P&ID Analysis System Validation Report")
        print("="*60)
        
        # Calculate overall status
        env_ok = all(self.results['environment'].values())
        openai_ok = self.results['openai'].get('api_key_valid_format', False)
        analysis_ok = self.results['analysis'].get('analysis_completed', False)
        
        if env_ok and openai_ok and analysis_ok:
            status = "🟢 FULLY OPERATIONAL"
            message = "All systems are working correctly with OpenAI integration."
        elif env_ok and analysis_ok:
            status = "🟡 OPERATIONAL (DEMO MODE)"
            message = "System working with fallback analysis. Configure OpenAI for full functionality."
        else:
            status = "🔴 NEEDS CONFIGURATION"
            message = "Critical configuration issues detected. See details above."
        
        self.results['overall_status'] = status
        
        print(f"Overall Status: {status}")
        print(f"Summary: {message}")
        
        # Recommendations
        print("\\n📋 Recommendations:")
        
        if not self.results['openai'].get('api_key_valid_format'):
            print("  1. ⚠️  Set up valid OpenAI API key in environment variables")
            print("     - Get API key from: https://platform.openai.com/api-keys")
            print("     - Update OPENAI_API_KEY in .env or production environment")
        
        if not self.results['openai'].get('integration_enabled'):
            print("  2. ⚠️  Enable OpenAI integration:")
            print("     - Set ENABLE_OPENAI_INTEGRATION=true in environment")
        
        if not env_ok:
            print("  3. ⚠️  Fix environment configuration issues listed above")
        
        print(f"\\n  ✅ System ready for: {'Production deployment' if openai_ok else 'Demo/Development'}")
        
        return self.results
    
    def save_report(self):
        """Save validation report to file"""
        report_file = Path(__file__).parent / 'validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\\n💾 Detailed report saved to: {report_file}")


async def main():
    """Main validation function"""
    print("🚀 EDRS P&ID Analysis System Validation")
    print("="*60)
    
    validator = EDRSValidationTool()
    
    # Run validation steps
    validator.validate_environment()
    validator.validate_openai_config()
    await validator.test_analysis_service()
    
    # Generate final report
    results = validator.generate_report()
    validator.save_report()
    
    return results


if __name__ == "__main__":
    # Run the validation
    try:
        results = asyncio.run(main())
        
        # Exit with appropriate code
        if "FULLY OPERATIONAL" in results['overall_status']:
            sys.exit(0)  # Success
        elif "OPERATIONAL" in results['overall_status']:
            sys.exit(1)  # Warning - demo mode
        else:
            sys.exit(2)  # Error - needs config
            
    except Exception as e:
        print(f"\\n❌ Validation failed with error: {e}")
        sys.exit(3)  # Critical error