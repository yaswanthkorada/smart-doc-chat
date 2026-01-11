# Document Schema Fix - Column Mismatch Resolution

## Problem
```
ProgrammingError: (psycopg2.errors.UndefinedColumn) column documents.doc_id does not exist
```

The app's SQLAlchemy Document model didn't match the Supabase database schema created from SUPABASE_SETUP_GUIDE.md

## Changes Made

### 1. Updated Document Model ([utils/database.py](utils/database.py))

**Removed:**
- `doc_id` Column(String) - Not in Supabase schema
- `storage_url` Column(String) 
- `num_chunks` Column(Integer)
- `status` Column(String) - "processing", "completed", "failed"
- `error_message` Column(Text)

**Added/Updated to Match Supabase:**
- `file_path` Column(Text) - Matches Supabase `file_path`
- `chunk_count` Column(Integer) - Matches Supabase `chunk_count`
- `processed` Column(Boolean) - Matches Supabase `processed`
- `metadata` Column(Text) - Matches Supabase `metadata` (JSONB stored as text)

### 2. Updated Database Methods

#### `add_document()` - [utils/database.py](utils/database.py#L606)
**Before:**
```python
def add_document(self, user_id, doc_id: str, filename: str, 
                file_size: int, file_type: str, storage_url: str)
```
**After:**
```python
def add_document(self, user_id, filename: str, 
                file_size: int, file_type: str, file_path: str)
```
- Removed `doc_id` parameter (auto-generated UUID)
- Changed `storage_url` to `file_path`
- Sets `processed=False` and `chunk_count=0` by default

#### `update_document_status()` - [utils/database.py](utils/database.py#L632)
**Before:**
```python
def update_document_status(self, doc_id: str, status: str, 
                          num_chunks: int = 0, error_message: str = None)
```
**After:**
```python
def update_document_status(self, document_id: str, processed: bool = False, 
                          chunk_count: int = 0, metadata: str = None)
```
- Changed `doc_id` to `document_id` (UUID)
- Changed `status` (string) to `processed` (boolean)
- Changed `num_chunks` to `chunk_count`
- Changed `error_message` to `metadata` (JSON string)

#### `delete_document()` - [utils/database.py](utils/database.py#L664)
**Before:**
```python
def delete_document(self, doc_id: str)
# Used: Document.doc_id == doc_id
```
**After:**
```python
def delete_document(self, document_id: str)
# Uses: Document.id == document_id
```
- Changed parameter from `doc_id` to `document_id`
- Queries by UUID `id` column instead of non-existent `doc_id`

### 3. Updated Pages

#### [pages/2_📁_Documents.py](pages/2_📁_Documents.py#L324)
**`render_document_card()` function:**
- Changed from `doc.status` (string) to `doc.processed` (boolean)
- Changed from `doc.num_chunks` to `doc.chunk_count`
- Changed from `doc.doc_id` to `str(doc.id)` (UUID to string)
- Removed error message display (was using `doc.error_message`)
- Simplified status display to "Completed" vs "Processing"

#### [pages/3_⚙️_Settings.py](pages/3_⚙️_Settings.py#L607)
**Popular documents display:**
- Changed from `d.doc_id == doc_id` to `str(d.id) == doc_id`

## Database Schema Comparison

### Supabase Schema (CORRECT)
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    file_path TEXT,                    -- ✅ Used
    upload_date TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,    -- ✅ Used
    chunk_count INTEGER DEFAULT 0,      -- ✅ Used
    metadata JSONB                      -- ✅ Used
);
```

### Old SQLAlchemy Model (INCORRECT)
```python
class Document:
    id = Integer PRIMARY KEY           # ❌ Wrong type
    doc_id = String(100) UNIQUE        # ❌ Doesn't exist in Supabase
    storage_url = String(1000)         # ❌ Should be file_path
    num_chunks = Integer               # ❌ Should be chunk_count
    status = String(50)                # ❌ Should be processed (boolean)
    error_message = Text               # ❌ Should be metadata (JSON)
```

### New SQLAlchemy Model (CORRECT)
```python
class Document:
    id = UUID PRIMARY KEY              # ✅ Matches Supabase
    # No doc_id column                 # ✅ Correct
    file_path = Text                   # ✅ Matches Supabase
    chunk_count = Integer              # ✅ Matches Supabase
    processed = Boolean                # ✅ Matches Supabase
    metadata = Text                    # ✅ Matches Supabase (JSONB as text)
```

## Files Modified
1. `utils/database.py` - Document model and methods
2. `pages/2_📁_Documents.py` - Document card rendering
3. `pages/3_⚙️_Settings.py` - Popular documents display

## Testing Checklist

After deploying, verify:
- [ ] App starts without `doc_id does not exist` error
- [ ] User can log in successfully
- [ ] Documents page loads without errors
- [ ] Settings page loads without errors
- [ ] Document statistics display correctly
- [ ] Document cards show proper status (Completed/Processing)
- [ ] Chunk count displays correctly

## Next Steps

You still need to update:
1. **`utils/rag_engine.py`** - Uses `doc_id`, `storage_url`, and `update_document_status()`
2. **File upload handlers** - Need to use `file_path` instead of `storage_url`
3. **Any code that calls `add_document()` with `doc_id` parameter**

## Deployment

```bash
git add .
git commit -m "Fix: Align Document model with Supabase schema"
git push origin feature/supabase
```

Then **reboot your Streamlit Cloud app**.

---

✅ **This fixes the immediate error** of `column documents.doc_id does not exist`

The app will now successfully query the documents table!
