# FastAPI Learning Guide - Part 2: Pydantic Models & Validation

## 🎯 Learning Objectives
After this guide, you'll master:
- Pydantic models for request/response validation
- Field validation and constraints
- Custom validators
- Enums for restricted choices
- Model configuration and serialization

---

## 📚 1. What is Pydantic?

Pydantic is a data validation library that uses Python type hints. FastAPI uses Pydantic for:
- **Request validation**: Ensure incoming data is correct
- **Response serialization**: Convert Python objects to JSON
- **Documentation**: Auto-generate API schema
- **IDE support**: Get autocomplete and type checking

---

## 🏗️ 2. Basic Model Structure

### Example from Your Project: [api/models.py](api/models.py#L41-L53)

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserSignup(BaseModel):
    """User signup request"""
    email: EmailStr                                    # Special type for emails
    username: str = Field(..., min_length=3, max_length=50)  # Constrained string
    password: str = Field(..., min_length=8)          # Minimum 8 characters
    full_name: Optional[str] = None                   # Optional field
```

### 🔍 Breaking It Down:

1. **`BaseModel`**: All Pydantic models inherit from this
2. **`EmailStr`**: Validates email format (requires `email-validator` package)
3. **`Field(...)`**: Add constraints and metadata
   - `...` (Ellipsis) means required field
   - `min_length`, `max_length`: Validation constraints
4. **`Optional[str]`**: Field can be string or None

### How FastAPI Uses This:

```python
@router.post("/signup")
async def signup(user_data: UserSignup):
    """FastAPI automatically:
    1. Parses request JSON
    2. Validates against UserSignup model
    3. Returns 422 error if validation fails
    4. Passes validated data to function
    """
    print(user_data.email)      # Validated email
    print(user_data.username)   # Validated username
    return {"message": "User created"}
```

---

## ✅ 3. Field Validation

### Common Field Constraints:

```python
from pydantic import BaseModel, Field, conint, constr
from typing import List

class Product(BaseModel):
    # String constraints
    name: str = Field(..., min_length=1, max_length=100)
    sku: constr(regex=r'^[A-Z]{3}-\d{4}$')  # Pattern: ABC-1234
    
    # Number constraints
    price: float = Field(..., gt=0, le=10000)  # Greater than 0, Less or equal 10000
    quantity: conint(ge=0, le=1000)            # Between 0 and 1000
    discount: float = Field(0.0, ge=0, le=1)   # Between 0 and 1 (percentage)
    
    # List constraints
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    # Description for documentation
    description: str = Field(
        ..., 
        description="Product description", 
        example="High-quality wireless headphones"
    )
```

### Field Constraints Reference:

| Constraint | Type | Description | Example |
|------------|------|-------------|---------|
| `gt` | Number | Greater than | `gt=0` |
| `ge` | Number | Greater or equal | `ge=0` |
| `lt` | Number | Less than | `lt=100` |
| `le` | Number | Less or equal | `le=100` |
| `min_length` | String/List | Minimum length | `min_length=3` |
| `max_length` | String/List | Maximum length | `max_length=50` |
| `regex` | String | Match pattern | `regex=r'^\d{3}-\d{4}$'` |
| `min_items` | List | Minimum items | `min_items=1` |
| `max_items` | List | Maximum items | `max_items=10` |

---

## 🎨 4. Enums for Restricted Choices

### Example from Your Project: [api/models.py](api/models.py#L12-L25)

```python
from enum import Enum

class AIProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

# Usage in models
class UserSettings(BaseModel):
    ai_provider: AIProvider  # Must be "openai" or "gemini"
    subscription: SubscriptionTier  # Must be "free", "premium", or "enterprise"
```

### 🔍 Why Use Enums?

1. **Type Safety**: Prevents typos and invalid values
2. **Documentation**: Shows available choices in API docs
3. **Validation**: Automatic validation by FastAPI
4. **IDE Support**: Autocomplete for enum values

### Using Enums in Endpoints:

```python
@router.post("/settings")
async def update_settings(provider: AIProvider):
    """
    API will only accept:
    - "openai"
    - "gemini"
    
    Any other value returns 422 Validation Error
    """
    if provider == AIProvider.OPENAI:
        # Use OpenAI
        pass
    elif provider == AIProvider.GEMINI:
        # Use Gemini
        pass
```

---

## 🛡️ 5. Custom Validators

### Example from Your Project: [api/models.py](api/models.py#L47-L51)

```python
from pydantic import BaseModel, validator

class UserSignup(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Ensure username is alphanumeric (underscores allowed)"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores allowed)')
        return v
```

### 🔍 How Validators Work:

1. **Decorator**: `@validator('field_name')` runs after basic type validation
2. **Parameters**: 
   - `cls`: The model class
   - `v`: The field value to validate
3. **Return**: Return the value (can transform it)
4. **Raise**: Raise `ValueError` for validation failure

### More Validator Examples:

```python
class UserProfile(BaseModel):
    email: str
    age: int
    website: Optional[str] = None
    password: str
    confirm_password: str
    
    @validator('age')
    def validate_age(cls, v):
        """Age must be between 18 and 120"""
        if v < 18:
            raise ValueError('Must be at least 18 years old')
        if v > 120:
            raise ValueError('Invalid age')
        return v
    
    @validator('website')
    def validate_website(cls, v):
        """Transform and validate URL"""
        if v is None:
            return v
        
        # Add https:// if missing
        if not v.startswith(('http://', 'https://')):
            v = f'https://{v}'
        
        # Validate URL format
        if not v.startswith('https://'):
            raise ValueError('Website must use HTTPS')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Check passwords match using 'values' dict"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
```

### Validator with Multiple Fields:

```python
from pydantic import root_validator

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime
    
    @root_validator
    def validate_date_range(cls, values):
        """Validate start_date is before end_date"""
        start = values.get('start_date')
        end = values.get('end_date')
        
        if start and end and start >= end:
            raise ValueError('start_date must be before end_date')
        
        return values
```

---

## 🔄 6. Model Configuration

### Example from Your Project: [api/models.py](api/models.py#L87-L89)

```python
class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows creating from ORM objects
```

### 🔍 Common Config Options:

```python
class MyModel(BaseModel):
    field1: str
    field2: int
    
    class Config:
        # Allow creating from ORM objects (SQLAlchemy, etc.)
        from_attributes = True  # Previously orm_mode
        
        # Allow extra fields in input
        extra = "allow"  # or "forbid" (default) or "ignore"
        
        # Custom JSON encoder
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        # Field aliases
        fields = {
            'field1': {'alias': 'field_one'}
        }
        
        # Validate on assignment
        validate_assignment = True
        
        # Schema example values
        schema_extra = {
            "example": {
                "field1": "example value",
                "field2": 42
            }
        }
```

### Why `from_attributes = True`?

```python
# Without from_attributes, this fails:
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String)

# Query database
db_user = session.query(UserDB).first()

# Convert to Pydantic model
class UserResponse(BaseModel):
    id: int
    email: str
    
    class Config:
        from_attributes = True  # Required to work with ORM objects!

# Now this works:
response = UserResponse.from_orm(db_user)  # Or UserResponse.model_validate(db_user)
```

---

## 📦 7. Nested Models

### Example from Your Project: [api/models.py](api/models.py#L168-L180)

```python
class SourceInfo(BaseModel):
    """Nested model for source citations"""
    filename: str
    page: Optional[int]
    chunk_index: Optional[int]
    relevance_score: Optional[float]

class ChatResponse(BaseModel):
    """Parent model with nested list"""
    success: bool
    response: str
    sources: List[SourceInfo]  # List of nested models
    conversation_id: str
    tokens_used: Optional[int]
```

### Using Nested Models:

```python
@router.post("/query", response_model=ChatResponse)
async def query_documents(query: ChatQuery):
    """FastAPI validates nested structure automatically"""
    return ChatResponse(
        success=True,
        response="Answer to your question",
        sources=[
            SourceInfo(
                filename="document1.pdf",
                page=5,
                relevance_score=0.95
            ),
            SourceInfo(
                filename="document2.pdf",
                page=12,
                relevance_score=0.87
            )
        ],
        conversation_id="abc-123",
        tokens_used=150
    )
```

### Complex Nesting Example:

```python
class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str

class Contact(BaseModel):
    email: EmailStr
    phone: Optional[str]

class Company(BaseModel):
    name: str
    address: Address
    contact: Contact

class Employee(BaseModel):
    name: str
    employee_id: str
    company: Company  # Nested company info
    skills: List[str]

# Request body example:
{
    "name": "John Doe",
    "employee_id": "EMP-001",
    "company": {
        "name": "TechCorp",
        "address": {
            "street": "123 Tech Street",
            "city": "San Francisco",
            "country": "USA",
            "zip_code": "94105"
        },
        "contact": {
            "email": "info@techcorp.com",
            "phone": "+1-555-0123"
        }
    },
    "skills": ["Python", "FastAPI", "Docker"]
}
```

---

## 🎭 8. Model Inheritance

### Example from Your Project: [api/models.py](api/models.py#L105-L132)

```python
class TodoCreate(BaseModel):
    """Base model for creating todos"""
    title: str
    description: Optional[str] = None
    completed: bool = False

class Todo(TodoCreate):
    """Extends TodoCreate with ID"""
    id: int
    created_at: datetime
    
    # Inherits: title, description, completed
    # Adds: id, created_at

class TodoUpdate(BaseModel):
    """Partial update - all fields optional"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
```

### 🔍 Why Inheritance?

1. **DRY Principle**: Don't repeat field definitions
2. **Request/Response Separation**: Different models for input/output
3. **Partial Updates**: Create update models with optional fields

---

## 📅 9. Working with Dates and Times

```python
from datetime import datetime, date
from pydantic import BaseModel, Field

class Event(BaseModel):
    name: str
    start_time: datetime  # ISO 8601 format: "2024-01-15T14:30:00"
    end_time: datetime
    date: date  # ISO date: "2024-01-15"
    
    @validator('end_time')
    def end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

# API accepts these formats:
{
    "name": "Conference",
    "start_time": "2024-01-15T09:00:00",
    "end_time": "2024-01-15T17:00:00",
    "date": "2024-01-15"
}

# Or with timezone:
{
    "name": "Webinar",
    "start_time": "2024-01-15T09:00:00+00:00",  # UTC
    "end_time": "2024-01-15T17:00:00+00:00"
}
```

---

## 🔢 10. Advanced Field Types

```python
from pydantic import BaseModel, HttpUrl, FilePath, DirectoryPath, Json
from typing import Dict, Any, Union
from decimal import Decimal
from uuid import UUID

class AdvancedModel(BaseModel):
    # URL validation
    website: HttpUrl  # Must be valid URL
    
    # File system paths
    config_file: FilePath  # Must exist
    data_dir: DirectoryPath  # Must exist
    
    # UUID
    user_id: UUID  # Auto-validates UUID format
    
    # Decimal for precise numbers (money, etc.)
    price: Decimal
    
    # JSON field (any valid JSON)
    metadata: Json
    
    # Union types (multiple allowed types)
    value: Union[int, str, float]
    
    # Dict with typed values
    settings: Dict[str, Any]
    
    # Literal (exact values only)
    from typing import Literal
    status: Literal["active", "inactive", "pending"]
```

---

## 🧪 11. Practical Exercise

### Build a Blog API with Proper Validation:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

app = FastAPI()

# Enums
class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Category(str, Enum):
    TECH = "tech"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"

# Models
class Author(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    bio: Optional[str] = Field(None, max_length=500)

class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=50)
    category: Category
    tags: List[str] = Field(default_factory=list, max_items=5)
    
    @validator('title')
    def title_must_be_capitalized(cls, v):
        if not v[0].isupper():
            raise ValueError('Title must start with capital letter')
        return v
    
    @validator('tags')
    def tags_must_be_lowercase(cls, v):
        return [tag.lower() for tag in v]

class PostCreate(PostBase):
    author: Author

class Post(PostBase):
    id: int
    status: PostStatus = PostStatus.DRAFT
    author: Author
    created_at: datetime
    updated_at: datetime
    views: int = 0
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Getting Started with FastAPI",
                "content": "FastAPI is a modern web framework...",
                "category": "tech",
                "tags": ["python", "fastapi", "tutorial"],
                "status": "published",
                "author": {
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "views": 1500
            }
        }

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=50)
    category: Optional[Category] = None
    tags: Optional[List[str]] = Field(None, max_items=5)
    status: Optional[PostStatus] = None

# In-memory storage
posts = []

@app.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate):
    """Create new blog post"""
    new_post = Post(
        id=len(posts) + 1,
        **post.dict(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    posts.append(new_post)
    return new_post

@app.get("/posts", response_model=List[Post])
async def list_posts(
    category: Optional[Category] = None,
    status: Optional[PostStatus] = None
):
    """List all posts with optional filters"""
    filtered_posts = posts
    
    if category:
        filtered_posts = [p for p in filtered_posts if p.category == category]
    if status:
        filtered_posts = [p for p in filtered_posts if p.status == status]
    
    return filtered_posts

@app.patch("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, post_update: PostUpdate):
    """Partial update of post"""
    for post in posts:
        if post.id == post_id:
            update_data = post_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(post, field, value)
            post.updated_at = datetime.now()
            return post
    
    raise HTTPException(status_code=404, detail="Post not found")

# Run with: uvicorn filename:app --reload
```

---

## 🎓 Key Takeaways

1. **Pydantic = Data Validation**: Ensures data integrity at API boundaries
2. **Field Constraints**: Use `Field()` for validation rules
3. **Enums for Choices**: Restrict values to predefined options
4. **Custom Validators**: Add business logic validation
5. **Model Inheritance**: Reuse field definitions across models
6. **Nested Models**: Handle complex data structures
7. **Config Class**: Control model behavior

---

## 📖 What's Next?

In **Part 3: Authentication & Security**, you'll learn:
- JWT token authentication
- Password hashing with bcrypt
- Dependency injection
- Security schemes
- Protected endpoints
- Real authentication system from your project

---

## 🔗 Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Field Types Reference](https://docs.pydantic.dev/latest/usage/types/)
