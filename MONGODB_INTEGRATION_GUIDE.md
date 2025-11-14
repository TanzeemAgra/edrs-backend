# MongoDB Integration Guide for EDRS

## 🏗️ Database Architecture

**EDRS uses a dual-database architecture:**

### 🐘 PostgreSQL (Primary Database) - ✅ CONNECTED
- **Purpose**: All CRUD operations (Users, Posts, Categories, Tags)
- **Status**: Fully operational with Railway
- **Connection**: `nozomi.proxy.rlwy.net:35250`
- **Usage**: Django ORM for all relational data

### 🍃 MongoDB (Document Database) - ⚠️ SETUP NEEDED
- **Purpose**: Analytics, Logs, File Metadata, Documents
- **Status**: Not connected (needs setup)
- **Usage**: MongoEngine for document storage

## 📊 Current Status

```
✅ PostgreSQL: FULLY OPERATIONAL
   - Users: 2 records
   - Categories: 1 records  
   - Posts: 1 records
   - All CRUD operations working

⚠️ MongoDB: NEEDS SETUP
   - Analytics: 0 documents
   - Activity Logs: 0 documents
   - Connection required for document features
```

## 🚀 MongoDB Setup Options

### Option 1: Railway MongoDB Service (Recommended)

1. **Add MongoDB Service to Railway:**
   ```
   Railway Dashboard → Your Project → Add Service → Database → MongoDB
   ```

2. **Get Connection String:**
   ```
   mongodb://mongo:PASSWORD@mongodb.railway.internal:27017
   ```

3. **Update Environment Variables:**
   ```env
   MONGODB_URI=mongodb://mongo:PASSWORD@mongodb.railway.internal:27017
   MONGO_DB_NAME=edrs_mongo
   ```

### Option 2: MongoDB Atlas (Cloud)

1. **Create MongoDB Atlas Account:**
   - Go to https://cloud.mongodb.com
   - Create free tier cluster (512MB, no cost)

2. **Get Connection String:**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/edrs_mongo
   ```

3. **Configure Environment:**
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/edrs_mongo
   MONGO_DB_NAME=edrs_mongo
   ```

### Option 3: Local Development Only

```env
MONGODB_URI=mongodb://localhost:27017/edrs_mongo
MONGO_DB_NAME=edrs_mongo
```

## 🧪 Testing MongoDB Integration

### Test Current Setup:
```bash
python manage.py test_mongodb
```

### Test with Custom URI:
```bash
python manage.py test_mongodb --mongo-uri "mongodb://your-connection-string"
```

### Create Sample Documents:
```bash
python manage.py test_mongodb --create-samples
```

### Full Dual Database Test:
```bash
python validate_dual_database.py
```

## 📱 MongoDB Document Models

### Analytics Documents (User Behavior Tracking)
```python
Analytics:
  - user_id: Reference to PostgreSQL user
  - event_type: "page_view", "button_click", "search"
  - event_data: JSON data with event details
  - session_id: User session identifier
  - timestamp: Event timestamp
  - ip_address: User IP
  - user_agent: Browser information
```

### Activity Log Documents (Audit Trail)
```python
ActivityLog:
  - user_id: Reference to PostgreSQL user  
  - action: "create_post", "login", "update_profile"
  - resource_type: "post", "user", "category"
  - resource_id: ID of the affected resource
  - details: JSON data with action details
  - timestamp: Action timestamp
  - ip_address: User IP
```

## 🔧 Usage in Application

### PostgreSQL (Primary - Always Use First)
```python
# All main CRUD operations
from apps.core.models import Post, Category, Tag
from django.contrib.auth import get_user_model

User = get_user_model()

# Create/Read/Update/Delete operations
user = User.objects.create_user(username='test', email='test@example.com')
post = Post.objects.create(title='Test', author=user)
categories = Category.objects.all()
```

### MongoDB (Documents - Use for Analytics/Logs)
```python
# Analytics and logging
from apps.core.models import Analytics, ActivityLog

# Track user behavior
Analytics(
    user_id=user.id,
    event_type='page_view',
    event_data={'page': '/dashboard', 'duration': 5000}
).save()

# Log user actions
ActivityLog(
    user_id=user.id,
    action='create_post',
    resource_type='post',
    resource_id=str(post.id),
    details={'title': post.title}
).save()
```

## 🎯 Recommendation

**Current Status**: Your system is fully functional with PostgreSQL alone!

**Next Steps**:
1. **Continue development** - PostgreSQL handles all core features
2. **Add MongoDB later** - For analytics when needed
3. **Railway MongoDB** - Easy integration when ready
4. **MongoDB Atlas** - Alternative cloud solution

The application works perfectly with just PostgreSQL. MongoDB is optional for enhanced analytics and logging features.

## 🚨 Important Notes

- **PostgreSQL is REQUIRED** - All core functionality depends on it ✅
- **MongoDB is OPTIONAL** - Only needed for advanced analytics and logging
- **Current functionality** - Users, Posts, Categories, Authentication all work without MongoDB
- **No data loss** - All essential data is safely stored in PostgreSQL

Your system is production-ready with the current PostgreSQL setup!