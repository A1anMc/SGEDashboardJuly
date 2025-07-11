# SGE Dashboard Database Setup Guide

This guide helps you configure the database connection for the SGE Dashboard application.

## 🚨 Important: DATABASE_URL Configuration

The application **requires** a valid `DATABASE_URL` environment variable to connect to your database. There are no localhost fallbacks in production.

## 📋 Quick Setup

### 1. Copy Environment Template
```bash
cp .env.template .envV2
```

### 2. Set Your DATABASE_URL
Edit `.envV2` and set your database connection string:

```bash
# For local PostgreSQL
DATABASE_URL="postgresql://username:password@localhost:5432/database_name"

# For Render PostgreSQL (use Internal Database URL)
DATABASE_URL="postgresql://username:password@host:5432/database_name"

# For Supabase
DATABASE_URL="postgresql://postgres:password@host:5432/postgres"
```

### 3. Validate Configuration
```bash
python scripts/validate_database.py
```

## 🔧 Render Deployment Setup

### Step 1: Create PostgreSQL Database
1. Go to your Render dashboard
2. Click "New" → "PostgreSQL"
3. Choose a name for your database
4. Select region and plan
5. Click "Create Database"

### Step 2: Get Database URL
1. In your PostgreSQL dashboard, find the "Connections" section
2. **Use the "Internal Database URL"** (not External)
3. Copy the full connection string

### Step 3: Configure Backend Service
1. Go to your backend service in Render
2. Go to "Environment" tab
3. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: Your Internal Database URL from Step 2

### Step 4: Deploy
Your backend will now connect to the PostgreSQL database on startup.

## 🛠️ Troubleshooting

### Error: "connection to server at localhost, port 5432 failed"
**Cause**: The app is trying to connect to localhost instead of your production database.

**Solution**:
1. Check that `DATABASE_URL` is set in your Render environment variables
2. Use the **Internal Database URL** from Render (not External)
3. Ensure the URL starts with `postgresql://`

### Error: "DATABASE_URL environment variable is required"
**Cause**: No DATABASE_URL is configured.

**Solution**:
1. Set `DATABASE_URL` in your `.envV2` file (local)
2. Set `DATABASE_URL` in Render environment variables (production)

### Error: "Database connection failed: authentication failed"
**Cause**: Wrong username/password in DATABASE_URL.

**Solution**:
1. Double-check your database credentials
2. For Render: Use the exact Internal Database URL from dashboard
3. For Supabase: Use the connection string from project settings

### Error: "Database connection failed: SSL connection required"
**Cause**: Production database requires SSL connection.

**Solution**: The app automatically adds SSL for known providers, but you can manually add:
```
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
```

## 🧪 Testing Database Connection

### 1. Validate Configuration
```bash
python scripts/validate_database.py
```

### 2. Test Health Endpoint
```bash
# Start the server
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "development",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

## 🔍 Database URL Formats

### PostgreSQL (Recommended)
```
postgresql://username:password@hostname:port/database_name
```

### PostgreSQL with SSL
```
postgresql://username:password@hostname:port/database_name?sslmode=require
```

### Supabase
```
postgresql://postgres:password@db.project.supabase.co:5432/postgres
```

### Local Development
```
postgresql://username:password@localhost:5432/sge_dashboard
```

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Full database connection string |
| `DATABASE_POOL_SIZE` | No | Connection pool size (default: 5) |
| `DATABASE_MAX_OVERFLOW` | No | Max overflow connections (default: 10) |
| `DATABASE_POOL_TIMEOUT` | No | Connection timeout seconds (default: 30) |
| `DATABASE_MAX_RETRIES` | No | Connection retry attempts (default: 5) |
| `DATABASE_RETRY_DELAY` | No | Retry delay seconds (default: 1) |

## 🏗️ Database Schema

The application uses Alembic for database migrations. On startup, it will:

1. Test the database connection
2. Create tables if they don't exist
3. Run any pending migrations

## 📝 Security Notes

- Never commit real DATABASE_URL values to git
- Use environment variables for all database credentials
- In production, ensure SSL connections are enabled
- The app validates that localhost is not used in production

## 🆘 Getting Help

If you're still having issues:

1. Run the validation script: `python scripts/validate_database.py`
2. Check the application logs for specific error messages
3. Verify your DATABASE_URL format matches the examples above
4. Ensure your database server is running and accessible

## 📚 Related Files

- `.env.template` - Environment variable template
- `.env.production` - Production environment template
- `scripts/validate_database.py` - Database validation script
- `app/db/session.py` - Database session configuration
- `app/core/config.py` - Application configuration 