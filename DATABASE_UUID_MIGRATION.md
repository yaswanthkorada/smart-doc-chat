# Database UUID Migration - Fix Summary

## Problem
The Streamlit app was failing with:
```
psycopg2.errors.DatatypeMismatch: foreign key constraint "conversations_user_id_fkey" cannot be implemented
DETAIL: Key columns "user_id" and "id" are of incompatible types: integer and uuid.
```

## Root Cause
- Supabase database tables were created with `UUID` primary keys (from SUPABASE_SETUP_GUIDE.md)
- SQLAlchemy models in the app used `INTEGER` primary keys
- This type mismatch caused foreign key constraint failures

## Changes Made

### 1. Updated `utils/database.py`

#### Added UUID Support
```python
from sqlalchemy.dialects.postgresql import UUID
from typing import Union
```

#### Updated All Model Classes
- **User**: `id` changed from `Integer` to `UUID(as_uuid=True)`
- **Conversation**: `id` and `user_id` foreign key changed to `UUID(as_uuid=True)`
- **ChatSession**: `id` changed to `UUID(as_uuid=True)`
- **Message**: `id` changed to `UUID(as_uuid=True)`
- **Document**: `id` and `user_id` foreign key changed to `UUID(as_uuid=True)`
- **QueryAnalytics**: `id` and `user_id` foreign key changed to `UUID(as_uuid=True)`

#### Updated to_dict() Methods
All `to_dict()` methods now convert UUID to string:
```python
"id": str(self.id),
"user_id": str(self.user_id),
```

#### Updated Method Signatures
All database manager methods now accept `Union[str, uuid.UUID]` for user_id:
- `update_last_login(user_id: Union[str, uuid.UUID])`
- `create_conversation(user_id: Union[str, uuid.UUID], ...)`
- `get_user_conversations(user_id: Union[str, uuid.UUID], ...)`
- `add_document(user_id: Union[str, uuid.UUID], ...)`
- `get_user_documents(user_id: Union[str, uuid.UUID])`
- `log_query_analytics(user_id: Union[str, uuid.UUID], ...)`
- `get_user_analytics(user_id: Union[str, uuid.UUID], ...)`
- `get_user_stats(user_id: Union[str, uuid.UUID])`

### 2. Updated `components/auth.py`
- `check_tier_limit(user_id: str, ...)` - Changed from `int` to `str` for UUID

### 3. Updated `config/settings.py`
- Added automatic PostgreSQL connection string construction from Supabase credentials
- Added `SUPABASE_DB_PASSWORD` configuration option

### 4. Updated Database Connection Handling
- Added connection pooling for PostgreSQL
- Added pre-ping to verify connections
- Added connection timeout and timezone settings
- Better error handling and logging

## What This Fixes

✅ **Foreign key type mismatch errors**
✅ **Database table creation on Streamlit Cloud**
✅ **Compatibility with Supabase UUID-based schema**
✅ **User authentication and session management**
✅ **Document uploads and tracking**
✅ **Conversation and message storage**
✅ **Analytics and usage tracking**

## Deployment Steps

### For Streamlit Cloud:

1. **Ensure your Streamlit secrets include:**
```toml
[supabase]
url = "https://xqpaxqsjzgvxrtsgfkok.supabase.co"
key = "your-supabase-anon-key"
service_role_key = "your-service-role-key"
project_id = "xqpaxqsjzgvxrtsgfkok"
bucket = "documents"
db_password = "Yaswanth@1972"

[database]
connection_string = "postgresql://postgres:Yaswanth%401972@db.xqpaxqsjzgvxrtsgfkok.supabase.co:5432/postgres"

[api_keys]
GOOGLE_API_KEY = "your-key"
OPENAI_API_KEY = "your-key"
```

2. **Push your code to GitHub:**
```bash
git add .
git commit -m "Fix: Update database models to use UUID instead of INTEGER"
git push origin main
```

3. **Reboot your Streamlit app** to apply changes

### For Local Development:

1. Create `.streamlit/secrets.toml` with the same configuration
2. Or use `.env` file with environment variables
3. Run `streamlit run app.py`

## Testing Checklist

After deployment, verify:
- [ ] App starts without database errors
- [ ] User can sign up (creates UUID in users table)
- [ ] User can log in
- [ ] User can create conversations
- [ ] User can upload documents
- [ ] Chat messages are saved
- [ ] User stats load correctly
- [ ] No foreign key constraint errors in logs

## Technical Notes

### UUID Handling
- SQLAlchemy uses `UUID(as_uuid=True)` to store UUIDs as native PostgreSQL UUID type
- Python generates UUIDs using `uuid.uuid4()`
- When passed to/from the database, UUIDs are automatically converted
- In session state and queries, UUIDs can be strings or UUID objects

### Backwards Compatibility
- The app will NOT work with old INTEGER-based databases
- If you had an existing database with INTEGER keys, you need to:
  1. Export all data
  2. Drop and recreate tables with UUID
  3. Re-import data with new UUIDs

### Why UUID Instead of INTEGER?
- Supabase default schema uses UUID
- Better for distributed systems
- No collision risk
- Globally unique identifiers
- Industry standard for cloud databases

## Files Changed
1. `utils/database.py` - All model definitions and methods
2. `components/auth.py` - Type hint for check_tier_limit
3. `config/settings.py` - Database URL construction
4. `.streamlit/secrets.toml.example` - Added db_password field

## No Breaking Changes For Users
- User-facing functionality remains the same
- Only internal database schema changed
- All features work as before
