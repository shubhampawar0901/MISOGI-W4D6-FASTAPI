# 📝 Task Manager API

A production-grade task management system built with FastAPI, featuring both REST API endpoints and a modern web interface.

## 🎯 Features

- **✅ Complete CRUD Operations**: Create, read, update, and delete tasks
- **🎨 Modern Web Interface**: Beautiful, responsive UI with smooth animations
- **📚 Auto-Generated Documentation**: Interactive API docs with Swagger UI
- **🔍 Input Validation**: Comprehensive validation using Pydantic schemas
- **⚡ Fast Performance**: Built on FastAPI for high performance
- **🏗️ Production-Ready Structure**: Organized codebase following best practices
- **🧪 Error Handling**: Proper HTTP status codes and error responses

## 🏗️ Project Structure

```
task-manager/
├── app/                          # Main application package
│   ├── core/                     # Core configuration
│   │   └── config.py            # Settings management
│   ├── models/                   # Data models
│   │   └── task.py              # Task data model
│   ├── schemas/                  # Pydantic schemas
│   │   └── task.py              # Request/response schemas
│   ├── services/                 # Business logic
│   │   └── task_service.py      # Task management service
│   ├── routers/                  # API routes
│   │   ├── tasks.py             # Task API endpoints
│   │   └── ui.py                # Web UI endpoints
│   ├── templates/                # HTML templates
│   │   ├── base.html            # Base template
│   │   └── tasks.html           # Tasks page
│   └── main.py                  # FastAPI application
├── tests/                        # Test files
├── venv/                         # Virtual environment
├── .env                          # Environment variables
├── .gitignore                    # Git ignore file
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
cd "Basic Task Management API"
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/Scripts/activate  # Windows Git Bash
# or
source venv/bin/activate       # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
# Method 1: Using the main script
python main.py

# Method 2: Using uvicorn directly
uvicorn app.main:app --reload
```

### 5. Access the Application
- **🎨 Web Interface**: http://localhost:8000/ui/tasks
- **📚 API Documentation**: http://localhost:8000/docs
- **📖 Alternative Docs**: http://localhost:8000/redoc
- **🔍 Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Task Management
- `GET /api/tasks` - Get all tasks (with optional filtering)
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get a specific task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task

### Web Interface
- `GET /ui/tasks` - Main tasks page
- `POST /ui/tasks` - Create task from web form
- `POST /ui/tasks/{task_id}/edit` - Update task from web form
- `POST /ui/tasks/{task_id}/complete` - Mark task as complete
- `POST /ui/tasks/{task_id}/incomplete` - Mark task as incomplete
- `POST /ui/tasks/{task_id}/delete` - Delete task from web interface

## 🧪 Testing the API

### Using curl
```bash
# Get all tasks
curl http://localhost:8000/api/tasks

# Create a new task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Complete the FastAPI tutorial"}'

# Update a task
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete a task
curl -X DELETE http://localhost:8000/api/tasks/1
```

### Using the Web Interface
1. Open http://localhost:8000/ui/tasks
2. Use the form to create new tasks
3. Click buttons to mark tasks complete/incomplete
4. Use edit and delete buttons for task management

## 🔧 Configuration

Environment variables can be set in the `.env` file:

```env
# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
PROJECT_NAME=Task Manager API
PROJECT_DESCRIPTION=A simple task management system with FastAPI
VERSION=1.0.0

# Server Configuration
HOST=127.0.0.1
PORT=8000
```

## 🏗️ Architecture Overview

### **FastAPI vs Express.js Comparison**

| **Concept** | **Express.js** | **FastAPI** |
|-------------|----------------|-------------|
| **App Creation** | `const app = express()` | `app = FastAPI()` |
| **Routing** | `app.get('/path', handler)` | `@app.get('/path')` |
| **Middleware** | `app.use(middleware)` | `app.add_middleware()` |
| **Validation** | Manual/Joi | Automatic with Pydantic |
| **Documentation** | Manual/Swagger setup | Auto-generated |
| **Async Support** | `async/await` | `async def` |

### **Key Components**

1. **Models** (`app/models/`): Data structures (like TypeScript interfaces)
2. **Schemas** (`app/schemas/`): Input/output validation (like Joi schemas)
3. **Services** (`app/services/`): Business logic layer
4. **Routers** (`app/routers/`): API endpoint definitions
5. **Templates** (`app/templates/`): HTML templates for web UI

## 🧪 Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## 🚀 Production Deployment

For production deployment, consider:

1. **Use a production ASGI server**:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set environment variables**:
   ```env
   DEBUG=False
   LOG_LEVEL=WARNING
   ```

3. **Add database persistence** (replace in-memory storage)
4. **Implement authentication and authorization**
5. **Add rate limiting and security headers**
6. **Set up monitoring and logging**

## 📚 Learning Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Documentation**: https://pydantic-docs.helpmanual.io/
- **Uvicorn Documentation**: https://www.uvicorn.org/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Built with ❤️ using FastAPI and modern Python practices**
