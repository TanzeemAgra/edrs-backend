# 🚨 EDRS API Connection & Upload Issues - TROUBLESHOOTING GUIDE

## 🎯 Problem Analysis

Based on your console errors, the main issues are:

1. **API Connection Issue**: Frontend trying to connect to `http://localhost:8001/api` (wrong port)
2. **React Router Warnings**: Future compatibility warnings (non-critical)
3. **Upload/Analysis Issues**: Related to API connection problems

## ✅ IMMEDIATE FIX - Follow These Steps

### Step 1: Stop All Running Servers
```powershell
# Press Ctrl+C in all terminal windows where servers are running
# Or close all terminal windows
```

### Step 2: Fix API Configuration
The fix has been applied to:
- ✅ `frontend/.env` - Updated API URL to port 8000
- ✅ `frontend/src/services/api.js` - Fixed default URL
- ✅ `frontend/src/main.jsx` - Fixed React Router warnings

### Step 3: Start Backend Server (Port 8000)
```powershell
cd "C:\Users\Mohammed.Agra\OneDrive - Rejlers AB\Desktop\EDRS\backend"
python manage.py runserver 0.0.0.0:8000
```

**Expected Output:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

### Step 4: Start Frontend Server (Port 3000)
```powershell
# In a NEW terminal window
cd "C:\Users\Mohammed.Agra\OneDrive - Rejlers AB\Desktop\EDRS\frontend"
npm run dev
```

**Expected Output:**
```
VITE v4.x.x  ready in xxx ms
➜  Local:   http://localhost:3000/
➜  Network: http://192.168.x.x:3000/
```

### Step 5: Test the Connection
Open browser to: `http://localhost:3000`

**You should see:**
- ✅ No console errors about API connection
- ✅ Login page loads properly
- ✅ Dashboard loads after login
- ✅ P&ID analysis section works

## 🔧 Alternative: Use Automated Startup Script

Instead of manual steps, use the automated script:

```powershell
cd "C:\Users\Mohammed.Agra\OneDrive - Rejlers AB\Desktop\EDRS"
python start_dev_server.py
```

This script will:
- ✅ Check port availability
- ✅ Verify environment configuration
- ✅ Start both servers automatically
- ✅ Show status and test URLs

## 🎯 What Should Happen After Fix

### Frontend Console (Should be clean):
```
✅ No more "localhost:8001" connection errors
✅ No more React Router warnings
✅ API calls show "localhost:8000/api"
✅ Login/Dashboard work properly
```

### Network Tab (DevTools):
```
✅ API calls to localhost:8000/api/auth/login/ - Status 200
✅ API calls to localhost:8000/api/dashboard/stats/ - Status 200
✅ No failed requests to localhost:8001
```

## 🧪 Test P&ID Upload Functionality

After servers are running:

1. **Navigate to P&ID Section:**
   - Go to `http://localhost:3000/pid-analysis`
   - Click "New Project"

2. **Create Test Project:**
   ```json
   {
     "name": "Test P&ID Project",
     "project_type": "upstream",
     "engineering_standard": "ISA-5.1"
   }
   ```

3. **Upload Test Diagram:**
   - Click "Upload Diagram"
   - Select any PDF/PNG/JPG file
   - Fill in metadata
   - Click "Upload"

4. **Test Analysis:**
   - Click "Analyze" on uploaded diagram
   - Should see progress indicators
   - Results should appear (AI or fallback)

## 🚨 If Issues Persist

### Check Backend is Running:
```powershell
curl http://localhost:8000/health/
# Should return: {"status": "healthy"}
```

### Check Frontend Environment:
```javascript
// In browser console
console.log('API URL:', import.meta.env.VITE_API_URL)
// Should show: http://localhost:8000/api
```

### Check Network Connectivity:
```powershell
# Test backend API directly
curl http://localhost:8000/api/
# Should return API information
```

## 🎯 Expected Result After Fix

### ✅ SUCCESS INDICATORS:

1. **Clean Console Output:**
   ```
   ✅ No React Router warnings
   ✅ No API connection errors  
   ✅ Successful API requests to localhost:8000
   ✅ Login/authentication works
   ```

2. **Functional Features:**
   ```
   ✅ Dashboard loads with data
   ✅ P&ID project creation works
   ✅ Diagram upload works
   ✅ Analysis starts and completes
   ✅ Results display properly
   ```

3. **Network Requests:**
   ```
   ✅ GET http://localhost:8000/api/auth/login/ - 200
   ✅ GET http://localhost:8000/api/dashboard/stats/ - 200
   ✅ POST http://localhost:8000/api/pid-analysis/projects/ - 201
   ✅ No failed requests to port 8001
   ```

## 💡 Pro Tips

1. **Always check both servers are running on correct ports**
2. **Clear browser cache if old API URLs are cached**
3. **Use browser DevTools Network tab to verify API calls**
4. **Check terminal output for any error messages**

## 🆘 Emergency Fallback

If nothing else works:

```powershell
# Reset everything
cd "C:\Users\Mohammed.Agra\OneDrive - Rejlers AB\Desktop\EDRS"

# Backend
cd backend
python manage.py migrate
python manage.py runserver 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

The fixes have been applied and your system should now work correctly! 🎉