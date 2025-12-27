# 📊 Database Schema: RAG Assistant

This schema shows how all users share the same tables, with user_id and conversation_id linking data together.

---

## users
| Column      | Type    | Description                  |
|-------------|---------|------------------------------|
| user_id     | INTEGER | Primary key, unique per user |
| username    | TEXT    | Unique username              |
| email       | TEXT    | User email                   |
| password    | TEXT    | Hashed password              |
| created_at  | DATETIME| Account creation time        |

---

## documents
| Column      | Type    | Description                          |
|-------------|---------|--------------------------------------|
| doc_id      | TEXT    | Primary key, unique per document     |
| user_id     | INTEGER | Foreign key to users(user_id)        |
| filename    | TEXT    | Name of the uploaded file            |
| file_size   | INTEGER | Size in bytes                        |
| file_type   | TEXT    | pdf, docx, txt, etc.                 |
| storage_url | TEXT    | Path to file in local/cloud storage   |
| status      | TEXT    | processing/completed/failed          |
| num_chunks  | INTEGER | Number of chunks in vector DB        |
| created_at  | DATETIME| Upload time                          |

---

## conversations
| Column          | Type    | Description                          |
|-----------------|---------|--------------------------------------|
| conversation_id | TEXT    | Primary key, unique per conversation |
| user_id         | INTEGER | Foreign key to users(user_id)        |
| title           | TEXT    | Conversation title                   |
| created_at      | DATETIME| Start time                           |

---

## messages
| Column          | Type    | Description                              |
|-----------------|---------|------------------------------------------|
| message_id      | TEXT    | Primary key, unique per message          |
| conversation_id | TEXT    | Foreign key to conversations(conversation_id) |
| role            | TEXT    | 'user' or 'assistant'                    |
| content         | TEXT    | The message text                         |
| timestamp       | DATETIME| When the message was sent                |
| sources         | TEXT    | JSON of retrieved document chunks        |
| tokens_used     | INTEGER | (Optional) Number of tokens in message   |
| feedback        | TEXT    | (Optional) 'helpful'/'not_helpful'       |

---

**All users share these tables. Data is filtered by user_id and conversation_id for privacy and organization.**
