# EDRS Backend

Professional Django REST API backend for the Engineering Document Review System - designed for industrial-grade document management and P&ID analysis.

## 🏗️ Architecture

- **Framework**: Django 4.2 + Django REST Framework
- **Authentication**: JWT Token-based authentication
- **Databases**: PostgreSQL (primary), MongoDB (analytics), Redis (cache)
- **Deployment**: Railway
- **API Documentation**: Swagger/OpenAPI via DRF Spectacular

## 🚀 Quick Start

### Local Development
```bash
# Clone this repository
git clone <backend-repo-url>
cd edrs-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 🐳 Docker Development
```bash
# Build and run with Docker
docker build -t edrs-backend .
docker run -p 8000:8000 edrs-backend
```

## 📊 Database Configuration

### Required Databases
1. **PostgreSQL** - Primary database for users, posts, categories
2. **MongoDB** - Analytics and logging data  
3. **Redis** - Caching and sessions (optional)

### Environment Variables
```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/edrs_db

# MongoDB
MONGODB_URI=mongodb://localhost:27017/edrs_mongo

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# CORS (for frontend)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

## 🚂 Railway Deployment

### Automatic Deployment
1. **Connect Repository**: Link this repository to Railway
2. **Add Services**: Add PostgreSQL, MongoDB, and Redis services
3. **Environment Variables**: Set production environment variables
4. **Deploy**: Push to main branch for automatic deployment

### Environment Variables for Railway
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-app.railway.app
DATABASE_URL=postgresql://... # Auto-provided by Railway
MONGODB_URI=mongodb://...     # From MongoDB service
REDIS_URL=redis://...         # From Redis service
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Railway Services Setup
1. **PostgreSQL Service**: Automatically provides `DATABASE_URL`
2. **MongoDB Service**: Use Railway MongoDB or external MongoDB Atlas
3. **Redis Service**: For caching (recommended for production)

## 📖 API Endpoints

### Authentication
```
POST /api/auth/login/          - User login
POST /api/auth/register/       - User registration  
POST /api/auth/logout/         - User logout
GET  /api/auth/user/           - Get current user
POST /api/auth/change-password/ - Change password
```

### Users
```
GET    /api/users/             - List users
GET    /api/users/me/          - Get current user profile
PUT    /api/users/me/          - Update current user profile
GET    /api/users/{id}/        - Get user by ID
```

### Content Management
```
GET    /api/core/posts/        - List posts
POST   /api/core/posts/        - Create post
GET    /api/core/posts/{slug}/ - Get post details
PUT    /api/core/posts/{slug}/ - Update post
DELETE /api/core/posts/{slug}/ - Delete post

GET    /api/core/categories/   - List categories
POST   /api/core/categories/   - Create category
GET    /api/core/tags/         - List tags
POST   /api/core/tags/         - Create tag
```

### Dashboard & Analytics
```
GET /api/core/dashboard/stats/ - Dashboard statistics
POST /api/core/analytics/track/ - Track user events
POST /api/core/activity/log/   - Log user activities
```

## 📚 API Documentation

Interactive API documentation is available at:
- **Development**: http://localhost:8000/api/docs/
- **Production**: https://your-app.railway.app/api/docs/

## 🧪 Development

### Running Tests
```bash
python manage.py test
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations  
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### Code Quality
```bash
# Format code with Black
black .

# Lint with Flake8
flake8 .
```

## 📁 Project Structure

```
backend/
├── core/                    # Django project settings
├── apps/
│   ├── authentication/     # JWT auth system
│   ├── users/              # User management  
│   └── core/               # Content management
├── requirements.txt        # Python dependencies
├── manage.py              # Django management
├── Dockerfile             # Docker configuration
├── railway.json           # Railway deployment
└── .env.example          # Environment template
```

## 🔒 Security Features

- JWT token authentication
- CORS configuration
- SQL injection protection
- XSS protection
- CSRF protection
- Rate limiting ready
- Secure headers configuration
- Environment-based settings

## 🛠️ Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Configure database connections
- [ ] Set up CORS for frontend domain
- [ ] Configure email backend (optional)
- [ ] Set up monitoring and logging
- [ ] Configure static file serving
- [ ] Set up database backups

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check `DATABASE_URL` format
   - Verify database service is running
   - Check network connectivity

2. **CORS Errors**  
   - Verify `CORS_ALLOWED_ORIGINS` includes frontend URL
   - Check for trailing slashes in URLs

3. **Migration Issues**
   - Run `python manage.py migrate --fake-initial` if needed
   - Check for conflicting migrations

4. **Import Errors**
   - Verify all dependencies in `requirements.txt`
   - Check Python version compatibility

## 📞 Support

- 🐛 **Issues**: Create GitHub issue in this repository
- 📖 **API Docs**: `/api/docs/` endpoint  
- 🚂 **Railway Logs**: `railway logs` command
- 📧 **Email**: backend-support@edrs.com

---

**Ready for production deployment on Railway! 🚂**