# Module 4: Web Development with Flask & FastAPI

## 🎯 Goals
- Build REST APIs with Flask and FastAPI
- Understand request/response handling
- Learn routing, middleware, and validation
- Handle JSON data and HTTP methods
- Build the foundation to understand the main codebase

## 📋 Prerequisites
Completed Modules 1-3: Python Basics, OOP, File I/O

## 1. Flask Fundamentals

### Basic Flask Application
```python
from flask import Flask, request, jsonify, render_template
from flask import abort, make_response
import json

# Create Flask app
app = Flask(__name__)
app.config['DEBUG'] = True

# Basic route
@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api/status')
def status():
    return {"status": "healthy", "version": "1.0.0"}

# Route with parameters
@app.route('/users/<int:user_id>')
def get_user(user_id):
    # Simulate user data
    users = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@example.com"}
    }
    
    user = users.get(user_id)
    if not user:
        abort(404)
    
    return jsonify(user)

# Multiple HTTP methods
@app.route('/api/data', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_data():
    if request.method == 'GET':
        return {"message": "Getting data"}
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return {"error": "No JSON data provided"}, 400
        
        # Process data here
        return {"message": "Data created", "data": data}, 201
    
    elif request.method == 'PUT':
        data = request.get_json()
        return {"message": "Data updated", "data": data}
    
    elif request.method == 'DELETE':
        return {"message": "Data deleted"}, 204

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Flask with Classes and Database Simulation
```python
from flask import Flask, request, jsonify
from dataclasses import dataclass
from typing import List, Optional
import uuid
from datetime import datetime

app = Flask(__name__)

@dataclass
class Task:
    id: str
    title: str
    description: str
    completed: bool
    created_at: datetime
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }

class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []
    
    def create_task(self, title: str, description: str) -> Task:
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            completed=False,
            created_at=datetime.now()
        )
        self.tasks.append(task)
        return task
    
    def get_all_tasks(self) -> List[Task]:
        return self.tasks
    
    def get_task(self, task_id: str) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
        return task
    
    def delete_task(self, task_id: str) -> bool:
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

# Global task manager
task_manager = TaskManager()

# API Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = task_manager.get_all_tasks()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    # Validation
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    task = task_manager.create_task(
        title=data['title'],
        description=data.get('description', '')
    )
    
    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    task = task_manager.update_task(task_id, **data)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    deleted = task_manager.delete_task(task_id)
    if not deleted:
        return jsonify({"error": "Task not found"}), 404
    
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
```

## 2. FastAPI Fundamentals

### Basic FastAPI Application
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Task Manager API",
    description="A simple task management API",
    version="1.0.0"
)

# Pydantic models for request/response validation
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Data models
class Task:
    def __init__(self, title: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.completed = False
        self.created_at = datetime.now()

# In-memory storage
tasks_db: List[Task] = []

# Dependency functions
def get_task_by_id(task_id: str) -> Task:
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

# API Routes
@app.get("/")
async def root():
    return {"message": "Task Manager API", "docs": "/docs"}

@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks():
    """Get all tasks"""
    return tasks_db

@app.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate):
    """Create a new task"""
    task = Task(title=task_data.title, description=task_data.description or "")
    tasks_db.append(task)
    return task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task: Task = Depends(get_task_by_id)):
    """Get a specific task by ID"""
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_update: TaskUpdate, task: Task = Depends(get_task_by_id)):
    """Update a task"""
    update_data = task_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task: Task = Depends(get_task_by_id)):
    """Delete a task"""
    tasks_db.remove(task)
    return {"message": "Task deleted successfully"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "tasks_count": len(tasks_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Advanced FastAPI Features
```python
from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Advanced Task API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums for validation
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Advanced Pydantic models
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Priority = Priority.MEDIUM
    tags: List[str] = Field(default_factory=list)
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 5:
            raise ValueError('Maximum 5 tags allowed')
        return [tag.strip().lower() for tag in v if tag.strip()]

class TaskFilter(BaseModel):
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class TaskStats(BaseModel):
    total_tasks: int
    by_status: Dict[TaskStatus, int]
    by_priority: Dict[Priority, int]

# Enhanced data model
class Task:
    def __init__(self, title: str, description: str = "", priority: Priority = Priority.MEDIUM):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = TaskStatus.PENDING
        self.priority = priority
        self.tags = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

# In-memory database
tasks_db: List[Task] = []

# Dependency for filtering
def get_task_filter(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    tags: Optional[str] = Query(None, description="Comma-separated tags")
) -> TaskFilter:
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
    
    return TaskFilter(
        status=status,
        priority=priority,
        search=search,
        tags=tag_list
    )

# Service layer
class TaskService:
    @staticmethod
    def filter_tasks(tasks: List[Task], filters: TaskFilter) -> List[Task]:
        filtered = tasks
        
        if filters.status:
            filtered = [t for t in filtered if t.status == filters.status]
        
        if filters.priority:
            filtered = [t for t in filtered if t.priority == filters.priority]
        
        if filters.search:
            search_lower = filters.search.lower()
            filtered = [
                t for t in filtered 
                if search_lower in t.title.lower() or search_lower in t.description.lower()
            ]
        
        if filters.tags:
            filtered = [
                t for t in filtered 
                if any(tag in t.tags for tag in filters.tags)
            ]
        
        return filtered

# Advanced routes
@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    filters: TaskFilter = Depends(get_task_filter),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Skip number of results")
):
    """Get tasks with filtering and pagination"""
    filtered_tasks = TaskService.filter_tasks(tasks_db, filters)
    paginated = filtered_tasks[offset:offset + limit]
    
    return paginated

@app.get("/tasks/stats", response_model=TaskStats)
async def get_task_stats():
    """Get task statistics"""
    total = len(tasks_db)
    
    status_counts = {status: 0 for status in TaskStatus}
    priority_counts = {priority: 0 for priority in Priority}
    
    for task in tasks_db:
        status_counts[task.status] += 1
        priority_counts[task.priority] += 1
    
    return TaskStats(
        total_tasks=total,
        by_status=status_counts,
        by_priority=priority_counts
    )

@app.post("/tasks/bulk", response_model=List[TaskResponse])
async def create_bulk_tasks(tasks_data: List[TaskCreate]):
    """Create multiple tasks at once"""
    if len(tasks_data) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 tasks can be created at once")
    
    created_tasks = []
    for task_data in tasks_data:
        task = Task(
            title=task_data.title,
            description=task_data.description or "",
            priority=task_data.priority
        )
        task.tags = task_data.tags
        tasks_db.append(task)
        created_tasks.append(task)
        
        logger.info(f"Created task: {task.title}")
    
    return created_tasks

# Exception handling
@app.exception_handler(ValueError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Validation error", "detail": str(exc)}
    )

# Middleware for logging
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

## 3. Understanding the Main Codebase

### Analyzing the LangChain Semantic Search API
Looking at `main.py`, you can now understand:

```python
# FastAPI application setup
app = FastAPI(
    title="LangChain Semantic Search Engine",
    description="A semantic search engine for PDF documents...",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models for validation
class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.7

# Startup event for initialization
@app.on_event("startup")
async def startup_event():
    # Initialize all components
    global document_processor, search_engine, rag_engine
    # ... initialization code

# Route with dependency injection pattern
@app.post("/search", response_model=List[SearchResult])
async def semantic_search(query: SearchQuery):
    try:
        results = search_engine.search(
            query=query.query,
            top_k=query.top_k,
            similarity_threshold=query.similarity_threshold
        )
        # Format and return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### Key Patterns in the Codebase:
1. **Dependency injection** - Components are initialized globally and shared
2. **Pydantic models** - Request/response validation
3. **Error handling** - Comprehensive try/catch with HTTP exceptions
4. **Documentation** - Automatic API docs with detailed docstrings
5. **Startup hooks** - Initialize resources when app starts

## 🏃‍♂️ Practical Exercises

### Exercise 1: Build a File Upload API
```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil
from pathlib import Path

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file"""
    
    # Validate file type
    if file.content_type not in ["text/plain", "application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Save file
    file_path = UPLOAD_DIR / file.filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_path.stat().st_size,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/files/")
async def list_files():
    """List uploaded files"""
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    return {"files": files}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a file"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename)
```

### Exercise 2: API with Authentication
```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import hashlib

app = FastAPI()
security = HTTPBearer()

# Fake user database
users_db = {
    "admin": {
        "username": "admin",
        "password_hash": hashlib.sha256("secret123".encode()).hexdigest(),
        "role": "admin"
    }
}

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    role: str

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(username: str = Depends(verify_token)):
    user = users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/login")
async def login(login_request: LoginRequest):
    user = users_db.get(login_request.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    password_hash = hashlib.sha256(login_request.password.encode()).hexdigest()
    if user["password_hash"] != password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    expire = datetime.utcnow() + timedelta(hours=1)
    token_data = {"sub": user["username"], "exp": expire}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected", response_model=UserResponse)
async def protected_route(current_user = Depends(get_current_user)):
    return UserResponse(username=current_user["username"], role=current_user["role"])
```

## 🔍 Key Web Development Concepts

| Concept | Flask | FastAPI | Main Codebase |
|---------|-------|---------|---------------|
| **Routing** | `@app.route()` | `@app.get/post()` | `@app.post("/search")` |
| **Validation** | Manual | Pydantic models | `SearchQuery` class |
| **Error Handling** | `@app.errorhandler` | `HTTPException` | Try/catch with HTTP errors |
| **Documentation** | Manual | Automatic | Swagger UI at `/docs` |
| **Async Support** | Flask-Async | Native | `async def` functions |

## ⚡ Best Practices

1. **Use Pydantic models** for request/response validation
2. **Handle errors gracefully** with proper HTTP status codes
3. **Document your APIs** with docstrings and examples
4. **Use dependency injection** for shared resources
5. **Validate inputs** early and provide clear error messages
6. **Use async/await** for I/O operations
7. **Implement proper logging** for debugging

## 🚀 Understanding the Main Codebase
Now you can understand:
- How FastAPI routes work (`@app.post("/search")`)
- Pydantic model validation (`SearchQuery`, `RAGQuery`)
- Error handling with HTTP exceptions
- Startup event initialization
- Dependency injection patterns

## 🎯 Next Steps
- Practice building APIs with both Flask and FastAPI
- Understand request/response patterns
- Learn about async programming
- Move to Module 5: Data Processing

**Time to spend:** 4-6 hours

Ready to process data like a pro? → `05_DATA_PROCESSING.md`