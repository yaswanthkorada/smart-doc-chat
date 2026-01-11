-- ==============================================================
-- SUPABASE SQL SETUP FOR RAG APP
-- Run these commands in Supabase SQL Editor
-- ==============================================================

-- 1. Add subscription_tier column to users table (if missing)
ALTER TABLE users
ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free';

-- 2. Enable Row Level Security on documents table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 3. Create RLS Policy for authenticated users to manage their documents
CREATE POLICY IF NOT EXISTS "Users can manage their own documents"
ON documents
FOR ALL
TO authenticated
USING (auth.uid()::text = user_id::text)
WITH CHECK (auth.uid()::text = user_id::text);

-- 4. Enable Row Level Security on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 5. Create RLS Policy for users to read/update their own data
CREATE POLICY IF NOT EXISTS "Users can read their own data"
ON users
FOR SELECT
TO authenticated
USING (auth.uid() = id);

CREATE POLICY IF NOT EXISTS "Users can update their own data"
ON users
FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- 6. Allow service role to bypass RLS (for app backend operations)
-- This allows your Streamlit app (using service_role_key) to manage all data
CREATE POLICY IF NOT EXISTS "Service role can manage all documents"
ON documents
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY IF NOT EXISTS "Service role can manage all users"
ON users
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- 7. Create policy for authenticated users to insert their own documents
CREATE POLICY IF NOT EXISTS "Users can insert their own documents"
ON documents
FOR INSERT
TO authenticated
WITH CHECK (auth.uid()::text = user_id::text);

-- 8. Enable Storage policies for document uploads
-- Go to Storage → documents bucket → Policies and create:
--    Name: "Authenticated users can upload"
--    Allowed operations: INSERT
--    Policy definition: (bucket_id = 'documents' AND auth.role() = 'authenticated')

--    Name: "Users can view their own documents"
--    Allowed operations: SELECT
--    Policy definition: (bucket_id = 'documents' AND auth.role() = 'authenticated')

--    Name: "Users can delete their own documents"
--    Allowed operations: DELETE
--    Policy definition: (bucket_id = 'documents' AND auth.role() = 'authenticated')

-- ==============================================================
-- VERIFICATION QUERIES
-- ==============================================================

-- Check if subscription_tier column exists
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'subscription_tier';

-- Check RLS policies on documents table
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'documents';

-- Check RLS policies on users table
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'users';

-- Test user count
SELECT COUNT(*) as total_users FROM users;

-- Test document count
SELECT COUNT(*) as total_documents FROM documents;

-- ==============================================================
-- NOTES
-- ==============================================================
-- 1. After running this, users who sign up via Supabase Auth will automatically
--    have access to their own data through RLS policies.
--
-- 2. The service_role_key (used by your Streamlit app backend) bypasses RLS,
--    allowing the app to perform operations on behalf of users.
--
-- 3. For Storage policies, you need to set them in the Supabase Dashboard UI:
--    Storage → documents bucket → Policies tab
--
-- 4. Make sure your Streamlit secrets include:
--    - SUPABASE_KEY (anon key for client-side operations)
--    - SUPABASE_SERVICE_KEY (service role key for server-side operations)
