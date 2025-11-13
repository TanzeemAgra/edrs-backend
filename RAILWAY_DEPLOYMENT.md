# Railway Backend Deployment

This backend is configured for deployment on Railway.

## Environment Variables

Set the following environment variables in your Railway project:

### Required Variables
```
DEBUG=False
SECRET_KEY=your-production-secret-key-change-this
ALLOWED_HOSTS=your-domain.railway.app,localhost
DATABASE_URL=postgresql://user:password@host:port/database
MONGODB_URI=mongodb://username:password@host:port/database
MONGO_DB_NAME=edrs_mongo
```

### Important Notes
- Railway automatically provides DATABASE_URL when you add PostgreSQL service
- For MongoDB, you can use Railway's MongoDB plugin or MongoDB Atlas
- Make sure to replace 'your-domain' with your actual Railway domain

### Optional Variables
```
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
REDIS_URL=redis://host:port/0
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Deployment Steps

1. **Connect to Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Link to your project
   railway link
   ```

2. **Set Environment Variables:**
   ```bash
   railway variables set DEBUG=False
   railway variables set SECRET_KEY=your-secret-key
   railway variables set ALLOWED_HOSTS=your-domain.railway.app
   # ... set other variables
   ```

3. **Add Database Services:**
   - PostgreSQL: Add PostgreSQL service in Railway dashboard
   - MongoDB: Add MongoDB service or use MongoDB Atlas
   - Redis: Add Redis service (optional)

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Fix Railway healthcheck and deployment"
   git push origin main
   ```

## Healthcheck Fix

The deployment includes a custom health check endpoint at `/health/` that:
- ✅ Doesn't require authentication 
- ✅ Returns JSON response with service status
- ✅ Works properly with Railway's healthcheck system

### Healthcheck Response:
```json
{
  "status": "healthy",
  "service": "EDRS Backend API", 
  "version": "1.0.0"
}
```

## Troubleshooting

### If healthcheck still fails:
1. Check Railway logs for detailed error messages
2. Verify DATABASE_URL is properly set
3. Ensure PostgreSQL service is running
4. Check if migrations ran successfully

### Common Issues:
- **Database connection timeout**: Increase healthcheck timeout in railway.json
- **Missing environment variables**: Double-check all required variables are set
- **Migration errors**: Check database permissions and connectivity
   ```bash
   railway up
   ```

## Database Setup

### PostgreSQL
Railway will automatically provide `DATABASE_URL` when you add a PostgreSQL service.

### MongoDB
You can use:
- Railway MongoDB service
- MongoDB Atlas (recommended)
- External MongoDB hosting

Set the `MONGODB_URI` environment variable accordingly.

## Static Files

Static files are handled by WhiteNoise and collected during deployment.

## Health Check

The application includes a health check endpoint at `/api/auth/user/` for Railway's health monitoring.

## Logs

View logs using:
```bash
railway logs
```

## Custom Domain

Configure your custom domain in Railway dashboard under Settings > Domains.