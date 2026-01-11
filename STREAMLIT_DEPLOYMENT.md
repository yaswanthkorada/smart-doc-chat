# Streamlit Cloud Deployment Guide

## Problem Fixed
The app was failing with `sqlalchemy.exc.OperationalError` because it couldn't connect to a PostgreSQL database on Streamlit Cloud. This has been fixed to properly use Supabase PostgreSQL database.

## Setup Instructions for Streamlit Cloud

### Step 1: Set up Supabase Database

1. **Go to [Supabase](https://supabase.com)** and sign in
2. **Create a new project** or use an existing one
3. **Note down these credentials** (you'll need them for secrets):
   - Project URL: `https://xxxxx.supabase.co` (from Settings > API)
   - Anon key: Your public API key (from Settings > API)
   - Service role key: Your service role key (from Settings > API)
   - Database password: From Settings > Database

### Step 2: Get Database Connection String

1. In Supabase, go to **Settings > Database**
2. Find the **Connection String** section
3. Select **URI** mode
4. Copy the connection string (it looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password

### Step 3: Create Database Tables (Optional)

If you want to manually create tables in Supabase:

1. Go to **SQL Editor** in Supabase
2. The app will automatically create tables when it first runs
3. Or you can run the table creation scripts manually

### Step 4: Configure Streamlit Cloud Secrets

1. **Deploy your app to Streamlit Cloud**
2. **Go to your app dashboard**
3. **Click on "⋮" menu** and select **"Settings"**
4. **Open the "Secrets" section**
5. **Paste the following** (replace with your actual values):

```toml
# API Keys
[api_keys]
OPENAI_API_KEY = "sk-your-openai-key"
GOOGLE_API_KEY = "your-gemini-key"

# Supabase Configuration
[supabase]
url = "https://your-project.supabase.co"
key = "your-supabase-anon-key"
service_role_key = "your-supabase-service-role-key"
project_id = "your-project-id"
bucket = "documents"
db_password = "your-database-password"

# Database Connection
[database]
connection_string = "postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres"
```

6. **Click "Save"**
7. **Reboot your app**

### Step 5: Verify Deployment

1. Check the app logs for any errors
2. The app should now start successfully
3. Test user registration and login

## How It Works

The fix implements the following:

1. **Automatic Database URL Construction**: If you don't provide a full `connection_string`, the app can construct it from your Supabase URL and password
2. **Better Error Handling**: The database initialization now has better error messages
3. **Connection Reliability**: Added connection pooling and health checks for PostgreSQL
4. **Fallback to SQLite**: For local development, it automatically uses SQLite if no PostgreSQL is configured

## Local Development

For local development, you can either:

1. **Use SQLite** (default - no configuration needed)
2. **Use Supabase**: Create `.streamlit/secrets.toml` (see `.streamlit/secrets.toml.example`)

## Troubleshooting

### Error: "Failed to initialize database"

- **Check**: Your database password is correct
- **Check**: Your Supabase project URL is correct
- **Check**: The connection string format is correct
- **Try**: Copy the connection string directly from Supabase Settings > Database

### Error: "Connection timeout"

- **Check**: Your Supabase project is active (free tier projects pause after 7 days of inactivity)
- **Try**: Wake up your project by visiting the Supabase dashboard

### Error: "Authentication failed"

- **Check**: Your database password doesn't have special characters that need encoding
- **Try**: Use the connection string directly from Supabase

### Database tables not created

- **Check**: The app logs to see the actual error
- **Try**: Restart the app after configuring secrets
- **Try**: Manually create tables using SQL Editor in Supabase

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Security Notes

- ⚠️ **Never commit** `.streamlit/secrets.toml` to git
- ⚠️ **Use service_role_key** only when necessary (it bypasses Row Level Security)
- ✅ **Use anon key** (key) for most operations
- ✅ **Enable Row Level Security** in Supabase for production
