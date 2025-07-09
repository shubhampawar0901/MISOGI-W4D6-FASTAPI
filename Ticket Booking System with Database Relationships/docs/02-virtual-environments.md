# 02 - Virtual Environments and Project Setup

## 🎯 Learning Objectives

By the end of this section, you will:
- Understand why virtual environments are essential
- Create and manage Python virtual environments
- Install and manage project dependencies
- Set up your development workspace properly

## 🤔 What Are Virtual Environments?

### **The Problem**
Imagine you're working on multiple Python projects:
- **Project A** needs Django 3.2
- **Project B** needs Django 4.1
- **Project C** needs FastAPI 0.100

Without virtual environments, all packages install globally, causing **dependency conflicts**.

### **Node.js Comparison**
```javascript
// Node.js - Each project has its own node_modules
project-a/
├── package.json          // Django equivalent
├── node_modules/         // Virtual environment equivalent
└── src/

project-b/
├── package.json
├── node_modules/         // Different versions, no conflicts!
└── src/
```

### **Python Solution - Virtual Environments**
```python
# Python - Each project has its own virtual environment
project-a/
├── requirements.txt      // package.json equivalent
├── venv/                 // node_modules equivalent
└── src/

project-b/
├── requirements.txt
├── venv/                 // Different versions, no conflicts!
└── src/
```

## 🛠️ Creating Your Virtual Environment

### **Step 1: Navigate to Your Project Directory**

```bash
# Create project directory
mkdir "Ticket Booking System with Database Relationships"
cd "Ticket Booking System with Database Relationships"
```

**Expected output:**
```bash
# You should now be in your project directory
pwd
# Output: /d/MISOGI/ASSIGNMENT/week4-ragbasic/fastapi-basic/Ticket Booking System with Database Relationships
```

### **Step 2: Create Virtual Environment**

```bash
# Create virtual environment named 'venv'
python -m venv venv
```

**What this does:**
- **Creates `venv/` folder** containing isolated Python installation
- **Copies Python interpreter** to `venv/Scripts/python.exe`
- **Creates pip** for installing packages in isolation
- **Sets up activation scripts** for entering/exiting the environment

**Expected result:**
```
venv/
├── Include/              # Header files
├── Lib/                  # Python libraries
│   └── site-packages/    # Where pip installs packages
├── Scripts/              # Executables and activation scripts
│   ├── activate          # Activation script (Linux/Mac)
│   ├── activate.bat      # Activation script (Windows CMD)
│   ├── Activate.ps1      # Activation script (PowerShell)
│   ├── pip.exe           # Package installer
│   └── python.exe        # Python interpreter
└── pyvenv.cfg            # Configuration file
```

### **Step 3: Activate Virtual Environment**

```bash
# Activate virtual environment (Git Bash on Windows)
source venv/Scripts/activate
```

**Alternative activation commands:**
```bash
# Windows Command Prompt
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

**Success indicators:**
```bash
# Your prompt should change to show (venv)
(venv) user@computer MINGW64 /d/path/to/project
$ 

# Verify Python location
which python
# Output: /d/path/to/project/venv/Scripts/python

# Verify pip location
which pip
# Output: /d/path/to/project/venv/Scripts/pip
```

## 📦 Installing Dependencies

### **Step 4: Install FastAPI and Dependencies**

```bash
# Install FastAPI with all dependencies
pip install fastapi[all]

# Install additional packages we'll need
pip install sqlalchemy
pip install pydantic-settings
pip install python-dotenv
```

**What each package does:**
- **`fastapi[all]`** - FastAPI framework with all optional dependencies
- **`sqlalchemy`** - Database ORM (like Sequelize for Node.js)
- **`pydantic-settings`** - Environment variable management
- **`python-dotenv`** - Load environment variables from .env files

### **Step 5: Verify Installation**

```bash
# Check installed packages
pip list
```

**Expected output:**
```
Package                 Version
----------------------- --------
annotated-types         0.6.0
anyio                   4.6.2
click                   8.1.7
fastapi                 0.116.0
h11                     0.14.0
httptools               0.6.4
idna                    3.10
pydantic                2.11.7
pydantic-core           2.27.1
pydantic-settings       2.7.0
python-dotenv           1.0.1
python-multipart        0.0.19
PyYAML                  6.0.2
sniffio                 1.3.1
sqlalchemy              2.0.41
starlette               0.41.3
typing-extensions       4.12.2
uvicorn                 0.35.0
uvloop                  0.21.0
watchfiles             1.0.3
websockets              14.1
```

### **Step 6: Create Requirements File**

```bash
# Generate requirements.txt (like package.json)
pip freeze > requirements.txt
```

**What this creates:**
```txt
# requirements.txt - exact versions for reproducible builds
annotated-types==0.6.0
anyio==4.6.2
click==8.1.7
fastapi==0.116.0
# ... all dependencies with exact versions
```

## 🔄 Virtual Environment Management

### **Daily Workflow**

```bash
# 1. Navigate to project
cd "Ticket Booking System with Database Relationships"

# 2. Activate virtual environment
source venv/Scripts/activate

# 3. Work on your project
# (venv) $ python main.py
# (venv) $ pip install new-package

# 4. Deactivate when done
deactivate
```

### **Installing from Requirements**

```bash
# On a new machine or fresh clone
pip install -r requirements.txt
```

**Node.js equivalent:**
```bash
npm install  # Installs from package.json
```

## 🚨 Common Issues and Solutions

### **Issue 1: Virtual Environment Not Activating**

**Problem:**
```bash
source venv/Scripts/activate
# No (venv) prefix appears
```

**Solutions:**
```bash
# Try different activation method
venv/Scripts/activate.bat  # Windows CMD
venv/Scripts/Activate.ps1  # PowerShell

# Check if venv was created properly
ls venv/Scripts/
# Should see activate, python.exe, pip.exe
```

### **Issue 2: Permission Denied**

**Problem:**
```bash
python -m venv venv
# Permission denied error
```

**Solutions:**
```bash
# Run as administrator or check folder permissions
# Ensure you have write access to the directory

# Alternative: Use different location
python -m venv ~/venvs/ticket-booking
source ~/venvs/ticket-booking/Scripts/activate
```

### **Issue 3: Wrong Python Version**

**Problem:**
```bash
python --version
# Python 2.7.x (too old)
```

**Solutions:**
```bash
# Use python3 explicitly
python3 -m venv venv
source venv/Scripts/activate

# Or install Python 3.8+ from python.org
```

## 🎯 Best Practices

### **Virtual Environment Naming**
```bash
# Good names
venv/          # Standard name
.venv/         # Hidden folder
env/           # Alternative

# Avoid
myproject-env/ # Too specific
python-env/    # Too generic
```

### **Gitignore Configuration**
```gitignore
# Always ignore virtual environments
venv/
.venv/
env/
.env

# Also ignore
__pycache__/
*.pyc
*.pyo
```

### **Requirements Management**
```bash
# Development dependencies
pip install pytest black flake8
pip freeze > requirements-dev.txt

# Production dependencies only
pip install fastapi sqlalchemy uvicorn
pip freeze > requirements.txt
```

## 🧪 Testing Your Setup

### **Quick Test**

```bash
# Ensure virtual environment is active
(venv) $ python -c "import fastapi; print('FastAPI installed successfully!')"
# Output: FastAPI installed successfully!

# Test uvicorn (development server)
(venv) $ uvicorn --version
# Output: Running uvicorn 0.35.0 with CPython 3.12.x on Windows
```

### **Create Test FastAPI App**

```bash
# Create simple test file
echo 'from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Virtual environment working!"}' > test_app.py

# Run the test app
uvicorn test_app:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1234] using StatReload
INFO:     Started server process [5678]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Visit `http://localhost:8000` to see: `{"message": "Virtual environment working!"}`

## 📚 Key Takeaways

### **Virtual Environments vs Node.js**

| **Concept** | **Node.js** | **Python** |
|-------------|-------------|------------|
| Dependency isolation | `node_modules/` | `venv/` |
| Package file | `package.json` | `requirements.txt` |
| Install command | `npm install` | `pip install` |
| Run script | `npm start` | `python main.py` |
| Global vs local | Local by default | Global by default (need venv) |

### **Why Virtual Environments Matter**
1. **Isolation** - Each project has its own dependencies
2. **Reproducibility** - Same versions across environments
3. **Cleanliness** - No global package pollution
4. **Flexibility** - Test different package versions safely

## 🚀 Next Steps

Now that your virtual environment is set up:

1. ✅ **Virtual environment created and activated**
2. ✅ **FastAPI and dependencies installed**
3. ✅ **Requirements file generated**
4. ✅ **Basic test completed**

**Next: [03 - Database Fundamentals →](03-database-fundamentals.md)**

---

**Previous: [← 01 - Introduction](01-introduction.md) | Next: [03 - Database Fundamentals →](03-database-fundamentals.md)**
