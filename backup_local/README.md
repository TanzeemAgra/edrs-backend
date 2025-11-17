# EDRS - Engineering Document Review System

Professional engineering document management platform designed for industrial projects, P&ID analysis, and regulatory compliance. Built with enterprise-grade architecture using Django REST API and React frontend.

## 🏗️ Project Structure

```
EDRS/
├── backend/              # Django REST API
├── frontend/             # React Application  
├── docker/              # Docker configurations
├── test/                # Isolated test environment
├── docker-compose.local.yml  # Local development
├── .env.example         # Environment template
├── .env.local.example   # Local environment template
└── README.md            # This file
```

## 🧪 Testing & Development Environments

### Test Environment (Completely Isolated)
- **Location**: `test/` folder
- **Purpose**: Automated testing without affecting development/production
- **Features**: Isolated Docker network, separate ports, ephemeral data
- **Usage**: `cd test && python test-manager.py setup`

### Local Development Environment  
- **Configuration**: `docker-compose.local.yml` + `.env.local`
- **Purpose**: Full-featured development environment
- **Features**: Hot reloading, debug tools, separate from production ports

This project supports multiple deployment strategies:

### Backend Repository Structure (Railway Deployment)
```
backend/
├── core/                  # Django project settings
├── apps/                  # Django applications
│   ├── authentication/    # JWT auth & user management
│   ├── users/            # User profiles & management
│   └── core/             # Posts, categories, analytics
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── railway.json          # Railway deployment config
├── .env.example          # Environment template
├── README.md             # Backend documentation
└── manage.py             # Django management script
```

### Frontend Repository Structure (Vercel Deployment)
```
frontend/
├── src/                  # React source code
│   ├── components/       # Reusable UI components
│   ├── pages/           # Page components
│   ├── stores/          # Zustand state management
│   └── services/        # API services
├── public/              # Static assets
├── package.json         # Node.js dependencies
├── vite.config.js       # Vite configuration
├── vercel.json          # Vercel deployment config
├── .env.example         # Environment template
└── README.md            # Frontend documentation
```

## 🚀 Tech Stack

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Authentication**: Token-based authentication with custom user model
- **Databases**: 
  - **PostgreSQL**: Primary relational database
  - **MongoDB**: Document storage for analytics & logs
  - **Redis**: Caching and session management
- **API Documentation**: DRF Spectacular (Swagger/OpenAPI)
- **Deployment**: Railway

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS + Headless UI
- **State Management**: Zustand
- **Routing**: React Router v6
- **Forms**: React Hook Form
- **HTTP Client**: Axios with interceptors
- **UI Components**: Custom component library
- **Deployment**: Vercel

### DevOps & Deployment
- **Containerization**: Docker (Railway deployment)
- **Backend Hosting**: Railway (PostgreSQL, MongoDB, Redis)
- **Frontend Hosting**: Vercel (CDN, Edge Functions)
- **Repository Strategy**: Separate repositories for independent deployment
- **Environment Management**: Platform-specific environment configs

## 🎯 Features

### 📋 Core Features
- ✅ User authentication & authorization
- ✅ Document/post management system
- ✅ Category and tag organization
- ✅ User profiles and settings
- ✅ Responsive dashboard interface
- ✅ RESTful API with documentation

### 🔧 Technical Features
- ✅ JWT token authentication
- ✅ CORS configuration for cross-origin requests
- ✅ Database migrations and admin interface
- ✅ Static file handling with WhiteNoise
- ✅ MongoDB integration for analytics
- ✅ Redis caching layer
- ✅ Docker containerization
- ✅ Production-ready deployment configs

## 🚀 Quick Start

### 1. Test Environment (Isolated Testing)
```bash
# Navigate to test environment
cd test/

# Validate environment setup
python validate_test_env.py

# Setup and run tests
python test-manager.py setup
python test-manager.py build
python test-manager.py start
python test-manager.py test

# View test results
python test-manager.py urls
```

### 2. Local Development Environment
```bash
# Setup environment
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Start local development
docker-compose -f docker-compose.local.yml --env-file .env.local up

# Access services:
# Frontend: http://localhost:3001
# Backend: http://localhost:8001
```

### 3. Separate Repository Setup (Production)

**Backend Repository:**
```bash
# Clone backend repository
git clone <backend-repo-url>
cd edrs-backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

pip install -r requirements.txt
cp .env.example .env  # Configure your environment
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Frontend Repository:**
```bash
# Clone frontend repository
git clone <frontend-repo-url>
cd edrs-frontend

# Setup and run
npm install
cp .env.example .env  # Configure your API URL
npm run dev
```

### Access Applications

**Local Development:**
- **Backend**: http://localhost:8001/api
- **Frontend**: http://localhost:3001
- **Admin Panel**: http://localhost:8001/admin
- **API Docs**: http://localhost:8001/api/docs

**Test Environment:**
- **Backend**: http://localhost:8002/api
- **Frontend**: http://localhost:3002
- **Admin Panel**: http://localhost:8002/admin
- **API Docs**: http://localhost:8002/api/docs

**Production (Separate Repos):**
- **Backend**: http://localhost:8000/api
- **Frontend**: http://localhost:3000

## 📊 Database Schema

### PostgreSQL Tables
- **Users**: Custom user model with extended profile fields
- **Categories**: Document organization categories
- **Tags**: Flexible tagging system
- **Posts**: Main content entities

### MongoDB Collections
- **Analytics**: User behavior tracking
- **Activity Logs**: System activity logging
- **User Profiles**: Extended user data and preferences

## 🔐 Authentication Flow

1. **Registration**: Create account with email verification
2. **Login**: Obtain JWT token for API access
3. **Token Management**: Automatic refresh and logout handling
4. **Protected Routes**: Frontend route protection
5. **API Security**: Token-based API authentication

## 🌍 Deployment

### Production Deployment

#### Backend Deployment (Railway)
1. **Create separate GitHub repository for backend**
2. **Push backend folder contents to the repository**
3. **Connect Railway to your backend repository**
4. **Add database services** (PostgreSQL, MongoDB, Redis)
5. **Set environment variables** in Railway dashboard
6. **Deploy automatically** on git push

#### Frontend Deployment (Vercel)
1. **Create separate GitHub repository for frontend**
2. **Push frontend folder contents to the repository**
3. **Connect Vercel to your frontend repository**
4. **Configure build settings** (Vite framework preset)
5. **Set environment variables** in Vercel dashboard
6. **Deploy automatically** on git push

### Environment Configuration
```bash
# Backend (.env)
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
MONGODB_URI=mongodb://...
ALLOWED_HOSTS=your-domain.railway.app

# Frontend (.env)
VITE_API_URL=https://your-backend.railway.app/api
```

## 📖 API Documentation

Interactive API documentation is available at:
- **Development**: http://localhost:8000/api/docs/
- **Production**: https://your-backend.railway.app/api/docs/

### Key API Endpoints
```
Authentication:
POST /api/auth/login/          - User login
POST /api/auth/register/       - User registration
POST /api/auth/logout/         - User logout
GET  /api/auth/user/           - Get current user

Users:
GET    /api/users/             - List users
GET    /api/users/{id}/        - Get user details
PUT    /api/users/{id}/        - Update user
DELETE /api/users/{id}/        - Delete user

Content:
GET    /api/core/posts/        - List posts
POST   /api/core/posts/        - Create post
GET    /api/core/posts/{slug}/ - Get post details
PUT    /api/core/posts/{slug}/ - Update post
DELETE /api/core/posts/{slug}/ - Delete post
```

## 🧪 Development

### Code Quality Tools
- **Backend**: Black (formatting), Flake8 (linting), pytest (testing)
- **Frontend**: Prettier (formatting), ESLint (linting), Vite (bundling)

### Development Commands
```bash
# Backend
python manage.py test                    # Run tests
python manage.py makemigrations         # Create migrations
python manage.py migrate               # Apply migrations
python manage.py collectstatic         # Collect static files

# Frontend
npm run dev                            # Development server
npm run build                          # Production build
npm run preview                        # Preview build
npm run lint                           # ESLint check
npm run format                         # Prettier format
```

## 📁 Project Structure Details

### Backend Apps
- **`core`**: Project settings and shared utilities
- **`authentication`**: JWT auth, login/logout, password management
- **`users`**: User model, profiles, user management
- **`core` (app)**: Posts, categories, tags, analytics

### Frontend Structure
- **`components/`**: Reusable UI components (Layout, Auth, Forms)
- **`pages/`**: Page-level components (Home, Dashboard, Auth)
- **`stores/`**: Zustand state management (auth, app state)
- **`services/`**: API service layer and HTTP client setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔍 Troubleshooting

Common issues and solutions:

1. **CORS Errors**: Check `CORS_ALLOWED_ORIGINS` in Django settings
2. **Database Connection**: Verify database URLs and credentials
3. **Build Failures**: Check Node.js version and dependency compatibility
4. **Authentication Issues**: Verify JWT token handling and API endpoints

For detailed deployment instructions, see [SEPARATE_DEPLOYMENT.md](SEPARATE_DEPLOYMENT.md).

## 📞 Support

- 📧 Email: support@edrs.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/edrs/issues)
- 📖 Documentation: [Wiki](https://github.com/your-username/edrs/wiki)

---

**Built with ❤️ using Django & React**