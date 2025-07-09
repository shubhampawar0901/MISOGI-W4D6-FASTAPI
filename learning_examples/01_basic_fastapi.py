# 🚀 LEARNING EXAMPLE 1: Basic FastAPI Application
# This is your first FastAPI app - let's understand each part!

# Step 1: Import FastAPI
from fastapi import FastAPI

# Step 2: Create an "instance" of FastAPI
# Think of this as creating your web application
app = FastAPI(
    title="My First FastAPI App",  # This will show in the documentation
    description="Learning FastAPI step by step",
    version="1.0.0"
)

# Step 3: Create your first "route" (endpoint)
# A route is like a door - when someone knocks on this door (makes a request),
# your function runs and gives them a response

@app.get("/")  # This decorator says "when someone visits the root URL, run this function"
def read_root():
    """
    This is your first API endpoint!
    When someone goes to http://localhost:8000/ they'll get this response
    """
    return {"message": "Hello World! This is my first FastAPI app!"}

# Step 4: Let's create another route with a parameter
@app.get("/hello/{name}")  # {name} is a "path parameter" - it's dynamic!
def say_hello(name: str):  # Notice the type hint: name: str
    """
    This endpoint takes a name and says hello to that person
    Try: http://localhost:8000/hello/John
    """
    return {"message": f"Hello {name}! Welcome to FastAPI!"}

# Step 5: A route that returns different types of data
@app.get("/info")
def get_info():
    """
    APIs can return different types of data - lists, dictionaries, etc.
    """
    return {
        "app_name": "Learning FastAPI",
        "version": "1.0.0",
        "features": ["Fast", "Easy", "Modern"],
        "is_learning": True,
        "student_count": 1
    }

# 🎯 KEY CONCEPTS YOU JUST LEARNED:
# 1. FastAPI() - creates your web application
# 2. @app.get() - decorator that creates a GET endpoint
# 3. Path parameters - {name} in the URL
# 4. Type hints - name: str helps with validation
# 5. Return values - FastAPI automatically converts to JSON

# 🚀 TO RUN THIS:
# 1. Save this file
# 2. In terminal: pip install fastapi uvicorn
# 3. Run: uvicorn 01_basic_fastapi:app --reload
# 4. Visit: http://localhost:8000/docs (automatic documentation!)
