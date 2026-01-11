-- Supabase SQL Queries for RAG Production Database

-- 1. List all users
SELECT * FROM users;

-- 2. Count total users
SELECT COUNT(*) AS total_users FROM users;

-- 3. List all messages
SELECT * FROM messages;

-- 4. Count total messages
SELECT COUNT(*) AS total_messages FROM messages;

-- 5. Show messages for a specific user
SELECT m.*
FROM messages m
JOIN chat_sessions s ON m.session_id = s.id
WHERE s.user_id = '<USER_ID>';
-- Replace <USER_ID> with the actual user id

-- 6. List all documents
SELECT * FROM documents;

-- 7. Count documents per user
SELECT user_id, COUNT(*) AS document_count
FROM documents
GROUP BY user_id;

-- 8. Show chat history for a user
SELECT *
FROM chat_history
WHERE user_id = '<USER_ID>';
-- Replace <USER_ID> with the actual user id

-- 9. Show all conversations
SELECT * FROM conversations;

-- 10. Query analytics (usage stats)
SELECT * FROM query_analytics;
