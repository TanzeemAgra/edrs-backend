# 🔧 EDRS Scripts

This folder contains deployment, maintenance, and utility scripts for the EDRS system.

## 📁 Script Files

### 🚀 Deployment Scripts
- **railway_precheck.py** - Pre-deployment validation for Railway
- **railway_native_deploy.py** - Native Railway deployment script  
- **deploy.py** - General deployment automation
- **deploy.sh** - Shell-based deployment script

### 🧹 Maintenance Scripts
- **cleanup-git-history.ps1** - Git repository cleanup and optimization

## 🔧 Usage

### Railway Deployment
```bash
# Validate before deployment
python railway_precheck.py

# Deploy to Railway
python railway_native_deploy.py
```

### General Deployment
```bash
# Python-based deployment
python deploy.py

# Shell-based deployment (Linux/macOS)
./deploy.sh
```

### Git Maintenance
```powershell
# Clean up git history (PowerShell)
.\cleanup-git-history.ps1
```

## 📋 Prerequisites

### Python Scripts
- Python 3.8+
- Required packages: `requests`, `django`, `psycopg2`

### Shell Scripts  
- Bash (Linux/macOS)
- Git
- Railway CLI (for railway scripts)

### PowerShell Scripts
- PowerShell 5.1+ 
- Git for Windows

## ⚙️ Configuration

Most scripts use environment variables or configuration files from the project root:
- `.env` files for environment configuration
- `railway.toml` for Railway-specific settings
- Django settings for database connections

## 🔒 Security Notes

- **Never commit sensitive data** like API keys or passwords
- **Test scripts in development** before running in production
- **Review script permissions** before execution
- **Use environment variables** for sensitive configuration

## 📞 Support

For script issues or improvements:
- **Technical Lead**: Mohammed Agra (mohammed.agra@rejlers.ae)
- **Repository**: [EDRS Backend](https://github.com/TanzeemAgra/edrs-backend)

---

*Keep scripts well-documented and tested. Update this README when adding new scripts.*