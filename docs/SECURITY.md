# EDRS Security Configuration Guide

## 🔒 Environment Variables Setup

### Backend Environment Files

Create these files locally (they are gitignored for security):

#### `backend/.env` (for production)
```bash
# Django Configuration
DEBUG=False
SECRET_KEY=your-super-secret-production-key-here-minimum-50-chars

# Database Configuration
DATABASE_URL=postgresql://username:password@hostname:port/database_name

# MongoDB Configuration  
MONGO_URL=mongodb://username:password@hostname:port/database_name

# Redis Configuration
REDIS_URL=redis://username:password@hostname:port/0

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_S3_BUCKET_NAME=your-s3-bucket-name
AWS_S3_REGION=your-aws-region

# Email Configuration
EMAIL_HOST_PASSWORD=your-app-password
AWS_SES_SMTP_PASSWORD=your-ses-smtp-password

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4000

# Security Settings
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### `backend/.env.local` (for local development)
```bash
# Local Development Configuration
DEBUG=True
SECRET_KEY=your-local-development-secret-key-here

# Local Database URLs
DATABASE_URL=postgresql://postgres:your-local-password@localhost:5433/edrs_local
MONGO_URL=mongodb://admin:your-local-password@localhost:27018/edrs_mongo_local?authSource=admin
REDIS_URL=redis://localhost:6380/0

# Local AWS (optional for development)
AWS_ACCESS_KEY_ID=your-dev-aws-key
AWS_SECRET_ACCESS_KEY=your-dev-aws-secret

# Development Email (optional)
EMAIL_HOST_PASSWORD=your-dev-email-password

# OpenAI for development
# OPENAI_API_KEY=your-dev-openai-key
```

### Frontend Environment Files

#### `frontend/.env.local`
```bash
# Frontend Configuration
REACT_APP_API_URL=http://localhost:8001
REACT_APP_ENVIRONMENT=local
REACT_APP_VERSION=1.0.0
```

## 🛡️ Security Best Practices

1. **Never commit environment files** - They are in .gitignore
2. **Use strong secrets** - Minimum 50 characters for SECRET_KEY
3. **Rotate credentials regularly** - Especially API keys
4. **Use different credentials** for development and production
5. **Monitor for exposed secrets** - Use tools like GitGuardian

## 🚨 If Secrets Are Exposed

1. **Immediately rotate/revoke** the exposed credentials
2. **Remove from git history** using git filter-branch or BFG Repo-Cleaner
3. **Update .gitignore** to prevent future exposure
4. **Notify your team** about the security incident

## 📝 Environment File Templates

Use the `.env.example` files as templates:
- Copy `.env.example` to `.env`
- Replace placeholder values with real credentials
- Never commit the actual `.env` files

## 🔐 Recommended Secret Management

For production environments, consider using:
- AWS Secrets Manager
- Azure Key Vault  
- HashiCorp Vault
- Environment variables in your deployment platform