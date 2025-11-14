# 🚨 Railway Deployment Fix - Docker vs Native Issue

## **Problem Identified**

Your Railway deployment is **still using Docker mode** instead of the native Python buildpack, which is causing the `postgres.railway.internal` error. The logs show:

```
psycopg2.OperationalError: could not translate host name "postgres.railway.internal" to address: Name or service not known
```

This happens because:
- Railway is building with Docker (despite our nixpacks configuration)
- Docker uses internal networking (`postgres.railway.internal`) 
- Your database URL should be the external Railway PostgreSQL URL

## **Immediate Fix Required**

### **Step 1: Force Railway to Use Native Buildpack**

In your **Railway Dashboard**:

1. Go to your backend service
2. Click **"Settings"** tab
3. Look for **"Build"** or **"Source"** section
4. If you see **"Builder: Docker"**, change it to **"Builder: Nixpacks"**
5. If there's a **"Root Directory"** setting, make sure it's set to `/` (root)
6. **Save changes**

### **Step 2: Verify Environment Variables**

Ensure these variables are set in Railway Dashboard → Variables:

```bash
# CRITICAL: Use external Railway PostgreSQL URL (NOT internal)
DATABASE_URL=postgresql://postgres:[password]@[external-host]:[port]/[database]

# Other required variables
SECRET_KEY=your-django-secret-key-here
DEBUG=False  
DJANGO_SETTINGS_MODULE=core.settings
RAILWAY_ENVIRONMENT=production
```

### **Step 3: Get Correct DATABASE_URL**

1. Go to Railway Dashboard
2. Find your **PostgreSQL service** (separate from backend)
3. Click **"Connect"** tab
4. Copy the **"External Connection URL"** (NOT internal)
5. It should look like: `postgresql://postgres:password@host.railway.app:5432/database`
6. Set this as your `DATABASE_URL` environment variable

## **Files I've Updated for Native Deployment**

### ✅ **Removed**: `railway.json` (was forcing Docker mode)
### ✅ **Added**: `nixpacks.toml` (forces native Python buildpack)

```toml
[phases.setup]
nixPkgs = ["python311", "gcc", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["python manage.py collectstatic --noinput"]

[start]
cmd = "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - core.wsgi:application"
```

### ✅ **Updated**: Django settings
- Fixed static files directory issue
- Added Railway-specific database SSL configuration  
- Improved error handling

### ✅ **Added**: Railway setup management command
- `python manage.py railway_setup`
- Handles migrations, static files, and admin user creation
- Better error detection and reporting

## **Complete Fix Process**

### **1. Railway Dashboard Changes**
```bash
Service Settings → Build → Builder: Nixpacks
Service Settings → Variables → DATABASE_URL: [external postgresql url]
```

### **2. Redeploy**
After changing the builder and environment variables:
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** 
3. Monitor build logs for native Python buildpack usage

### **3. Expected Success Logs**
You should see:
```bash
✅ Using Nixpacks Python provider
✅ Installing Python 3.11.6
✅ Installing dependencies from requirements.txt
✅ Collecting static files
✅ Running migrations
✅ Starting Gunicorn server
✅ Health check passed: /health/
```

## **Verification Steps**

### **Test Locally First**
```bash
# Test the railway setup command
python manage.py railway_setup

# Should show:
# ✅ Database connection successful
# ✅ Migrations completed  
# ✅ Static files collected
# ✅ Admin user created/verified
```

### **After Deployment**
Test these endpoints:
- Health: `https://your-app.railway.app/health/`
- API: `https://your-app.railway.app/api/`
- Admin: `https://your-app.railway.app/admin/`

## **Key Differences: Docker vs Native**

| Issue | Docker Mode | Native Buildpack |
|-------|-------------|------------------|
| **Database URL** | `postgres.railway.internal` | External Railway URL |
| **Build Time** | 40+ seconds | 15-20 seconds |
| **Network** | Internal Docker network | Direct Railway network |
| **Static Files** | Container filesystem | Railway persistent volume |
| **Debugging** | Container logs | Direct Python logs |
| **Reliability** | Container + app layers | Single Python process |

## **If Still Having Issues**

1. **Check Railway Builder**: Dashboard → Service → Settings → Ensure "Nixpacks" is selected
2. **Verify DATABASE_URL**: Must be external Railway PostgreSQL URL
3. **Check Logs**: Should show "Nixpacks Python provider" not Docker
4. **Force Rebuild**: Delete and recreate Railway service if needed

The root cause is Railway using Docker mode instead of native Python buildpack. Once you fix the builder setting and use the correct external DATABASE_URL, the deployment should work perfectly! 🚀