# Railway PostgreSQL Integration Guide

## 📋 Step-by-Step Railway Database Setup

### 1. Get Railway Database Connection Details

1. **Login to Railway Dashboard**: https://railway.app
2. **Select your project** (edrs-backend)
3. **Click on PostgreSQL service**
4. **Go to "Connect" tab**
5. **Copy the DATABASE_URL**

The URL will look like:
```
postgresql://postgres:PASSWORD@monorail.proxy.rlwy.net:PORT/railway
```

### 2. Update Backend Environment Variables

**Option A: Update .env file (for local testing)**
```bash
cd backend
```

Edit the `.env` file and replace the DATABASE_URL:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@monorail.proxy.rlwy.net:YOUR_PORT/railway
```

**Option B: Set Railway Environment Variables (for production)**
In Railway dashboard → Variables tab:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@monorail.proxy.rlwy.net:YOUR_PORT/railway
```

### 3. Test Database Connection

Run the validation script:
```bash
cd backend
python validate_database.py
```

Or use Django management command:
```bash
python manage.py test_db --create-test-data
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Test API Endpoints

Test the health endpoint:
```bash
curl https://your-domain.railway.app/health/
```

Test database health:
```bash
curl https://your-domain.railway.app/api/core/database/health/
```

## 🔧 Troubleshooting

### Common Issues:

1. **Connection Refused**: Check if Railway PostgreSQL service is running
2. **Authentication Failed**: Verify username/password in DATABASE_URL
3. **Host Not Found**: Ensure Railway domain is correct
4. **SSL Error**: Railway requires SSL connections (handled automatically)

### Verification Checklist:

- [ ] Railway PostgreSQL service is running
- [ ] DATABASE_URL is correctly formatted
- [ ] Backend can connect to Railway database
- [ ] Migrations are applied
- [ ] API endpoints respond correctly
- [ ] Frontend can access backend API

## 🎯 Expected Results

After successful setup, you should see:

✅ Database Connection: SUCCESS
✅ All Migrations Applied
✅ Models working correctly
✅ API endpoints responding
✅ Frontend integration working

## 📱 Frontend Integration

The frontend component `DatabaseIntegrationTest.jsx` will:
- Test API connectivity
- Verify database health
- Show integration status
- Display connection details

Add it to your app for real-time monitoring!