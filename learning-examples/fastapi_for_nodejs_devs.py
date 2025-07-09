# 🚀 FastAPI for Node.js Developers
# If you know Express.js, this will feel familiar!

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# ===== EXPRESS.JS EQUIVALENT =====
# const express = require('express');
# const app = express();
app = FastAPI(title="FastAPI for Node.js Devs")

# ===== DATA MODELS (like TypeScript interfaces) =====
# In Node.js you might use TypeScript interfaces or Joi schemas
# In FastAPI, we use Pydantic models for validation

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: int

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    message: str

# ===== IN-MEMORY STORAGE (like you'd do in Express) =====
users_db = []
user_counter = 1

# ===== ROUTES (compare to Express routes) =====

# EXPRESS: app.get('/', (req, res) => res.json({message: 'Hello World'}))
@app.get("/")
def root():
    return {"message": "Hello from FastAPI!", "framework": "FastAPI", "similar_to": "Express.js"}

# EXPRESS: app.get('/users', (req, res) => res.json(users))
@app.get("/users", response_model=List[UserResponse])
def get_users():
    return [
        UserResponse(**user, message="User retrieved successfully") 
        for user in users_db
    ]

# EXPRESS: app.get('/users/:id', (req, res) => { ... })
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        # Like throwing an error in Express: res.status(404).json({error: 'Not found'})
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user, message="User found successfully")

# EXPRESS: app.post('/users', (req, res) => { ... })
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: User):
    global user_counter
    
    # Automatic validation happens here (like Joi in Express)
    new_user = {
        "id": user_counter,
        "name": user.name,
        "email": user.email,
        "age": user.age
    }
    
    users_db.append(new_user)
    user_counter += 1
    
    return UserResponse(**new_user, message="User created successfully")

# EXPRESS: app.get('/users?age=25&limit=10', (req, res) => { ... })
@app.get("/users/search")
def search_users(
    age: Optional[int] = Query(None, description="Filter by age"),
    limit: int = Query(10, description="Limit results")
):
    filtered_users = users_db
    
    if age is not None:
        filtered_users = [u for u in filtered_users if u["age"] == age]
    
    return {
        "users": filtered_users[:limit],
        "total": len(filtered_users),
        "limit": limit
    }

# ===== ERROR HANDLING (like Express error middleware) =====
@app.exception_handler(ValueError)
def value_error_handler(request, exc):
    return {"error": "Invalid value provided", "detail": str(exc)}

# ===== MIDDLEWARE EQUIVALENT =====
@app.middleware("http")
async def log_requests(request, call_next):
    # Like Express middleware: app.use((req, res, next) => { ... })
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# ===== ASYNC ROUTES (like async/await in Express) =====
@app.get("/async-example")
async def async_route():
    # You can use async/await just like in Node.js!
    import asyncio
    await asyncio.sleep(0.1)  # Simulate async operation
    return {"message": "This was an async operation!"}

# ===== TO RUN THIS APP =====
if __name__ == "__main__":
    # Like app.listen(3000) in Express
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# 🎯 KEY TAKEAWAYS FOR NODE.JS DEVELOPERS:
# 1. Decorators (@app.get) instead of app.get() method calls
# 2. Pydantic models = TypeScript interfaces + Joi validation combined
# 3. Type hints everywhere = built-in TypeScript-like experience
# 4. HTTPException = throwing errors in Express
# 5. Query parameters work similarly to req.query
# 6. Middleware works almost identically
# 7. Async/await works the same way!
