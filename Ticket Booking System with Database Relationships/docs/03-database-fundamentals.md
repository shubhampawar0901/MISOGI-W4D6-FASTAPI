# 03 - Database Fundamentals with SQLAlchemy

## 🎯 Learning Objectives

By the end of this section, you will:
- Understand SQLAlchemy ORM concepts
- Configure database connections properly
- Create your first database configuration
- Understand the difference between engines, sessions, and models

## 🤔 What is SQLAlchemy?

### **ORM Concept**
**ORM (Object-Relational Mapping)** translates between Python objects and database tables.

**Without ORM (Raw SQL):**
```python
# Raw SQL - error-prone, database-specific
cursor.execute("SELECT * FROM users WHERE age > %s", (18,))
results = cursor.fetchall()
```

**With ORM (SQLAlchemy):**
```python
# SQLAlchemy - type-safe, database-agnostic
users = session.query(User).filter(User.age > 18).all()
```

### **Node.js Comparison**

| **Node.js** | **Python** | **Purpose** |
|-------------|------------|-------------|
| Sequelize | SQLAlchemy | Full-featured ORM |
| Prisma | SQLAlchemy | Modern ORM with migrations |
| TypeORM | SQLAlchemy | TypeScript-first ORM |
| Knex.js | SQLAlchemy Core | Query builder |

## 🏗️ SQLAlchemy Architecture

### **Core Components**

```python
# 1. Engine - Database connection manager
engine = create_engine("sqlite:///./database.db")

# 2. Session - Transaction manager  
SessionLocal = sessionmaker(bind=engine)

# 3. Base - Parent class for models
Base = declarative_base()

# 4. Model - Python class representing table
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
```

### **Data Flow**
```
Python Objects ←→ SQLAlchemy ORM ←→ SQL Database
     ↑                ↑                    ↑
   Models         Sessions/Engine      Tables
```

## 📁 Creating Database Configuration

### **Step 1: Create database.py**

Create a new file called `database.py` in your project root:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL - SQLite file will be created in your project folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./ticket_booking.db"

# Create database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 🔧 Understanding Each Component

### **1. Database Engine**

```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
```

**What the engine does:**
- **Connection management** - Handles database connections
- **SQL translation** - Converts Python to SQL
- **Connection pooling** - Reuses connections efficiently
- **Database dialect** - Knows how to speak SQLite/PostgreSQL/MySQL

**Node.js equivalent:**
```javascript
// Sequelize connection
const sequelize = new Sequelize('database', 'username', 'password', {
  host: 'localhost',
  dialect: 'sqlite',
  storage: './database.sqlite'
});
```

**SQLite-specific settings:**
- **`check_same_thread: False`** - Allows SQLite to work with FastAPI's async nature
- **`sqlite:///./ticket_booking.db`** - Creates file in current directory

### **2. Session Factory**

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Session parameters explained:**

#### **`autocommit=False`**
```python
# With autocommit=False (recommended)
session.add(User(name="John"))     # Change staged in memory
session.add(User(name="Jane"))     # Another change staged
session.commit()                   # Both changes saved together

# With autocommit=True (not recommended)
session.add(User(name="John"))     # Immediately saved to database
session.add(User(name="Jane"))     # Immediately saved to database
```

**Why False is better:** You control when changes become permanent (like manual `git commit`)

#### **`autoflush=False`**
```python
# With autoflush=False (more control)
session.add(User(name="John"))
user = session.query(User).filter(User.name == "John").first()  # Might not find John
session.flush()                    # Send to database but don't commit
user = session.query(User).filter(User.name == "John").first()  # Now finds John
session.commit()                   # Make permanent

# With autoflush=True (automatic)
session.add(User(name="John"))
user = session.query(User).filter(User.name == "John").first()  # Automatically finds John
```

#### **`bind=engine`**
Connects the session factory to your database engine.

### **3. Base Class**

```python
Base = declarative_base()
```

**What Base provides:**
- **Metadata collection** - Tracks all your models
- **Table creation** - Generates CREATE TABLE statements
- **Relationship mapping** - Handles foreign keys

**How you'll use it:**
```python
class Venue(Base):        # Inherits from Base
    __tablename__ = 'venues'
    id = Column(Integer, primary_key=True)

class Event(Base):        # Also inherits from Base  
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
```

### **4. Database Dependency**

```python
def get_db():
    db = SessionLocal()    # Create new session
    try:
        yield db           # Give session to FastAPI endpoint
    finally:
        db.close()         # Always close session
```

**Why `yield` instead of `return`?**
- **Generator function** - FastAPI's dependency system uses generators
- **Automatic cleanup** - `finally` block always runs
- **Resource management** - Prevents database connection leaks

**How you'll use it:**
```python
@app.get("/users")
def get_users(db: Session = Depends(get_db)):  # get_db() provides session
    users = db.query(User).all()               # Use session for queries
    return users                               # Session auto-closes
```

## 🧪 Testing Your Database Configuration

### **Step 2: Test Database Setup**

```bash
# Test if your database configuration works
python -c "from database import engine; print('Database engine created successfully!'); print('Database URL:', engine.url)"
```

**Expected output:**
```
Database engine created successfully!
Database URL: sqlite:///./ticket_booking.db
```

### **Step 3: Test Session Factory**

```bash
# Test session creation
python -c "from database import SessionLocal; session = SessionLocal(); print('Session created:', session); session.close()"
```

**Expected output:**
```
Session created: <sqlalchemy.orm.session.Session object at 0x...>
```

### **Step 4: Test Complete Setup**

```bash
# Test all components
python -c "import database; print('SessionLocal:', database.SessionLocal); print('Base:', database.Base); print('get_db function:', database.get_db)"
```

**Expected output:**
```
SessionLocal: <sqlalchemy.orm.session.sessionmaker object at 0x...>
Base: <sqlalchemy.ext.declarative.api.DeclarativeMeta object at 0x...>
get_db function: <function get_db at 0x...>
```

## 🔍 Database URL Formats

### **SQLite (Development)**
```python
# File-based database
"sqlite:///./database.db"          # Relative path
"sqlite:////absolute/path/db.db"   # Absolute path
"sqlite:///:memory:"               # In-memory (testing)
```

### **PostgreSQL (Production)**
```python
# Network database
"postgresql://user:password@localhost/dbname"
"postgresql://user:password@localhost:5432/dbname"
```

### **MySQL (Alternative)**
```python
# MySQL database
"mysql://user:password@localhost/dbname"
"mysql+pymysql://user:password@localhost/dbname"
```

## 🚨 Common Issues and Solutions

### **Issue 1: Import Error**

**Problem:**
```bash
ImportError: cannot import name 'engine' from 'database'
```

**Solution:**
```bash
# Check for syntax errors
python -c "import database; print('Import successful')"

# If this fails, check your database.py file for:
# - Missing closing parentheses
# - Indentation errors  
# - Missing imports
```

### **Issue 2: SQLite Threading Error**

**Problem:**
```
sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread
```

**Solution:**
```python
# Ensure you have this in create_engine()
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # This line is crucial
)
```

### **Issue 3: Database File Permissions**

**Problem:**
```
PermissionError: [Errno 13] Permission denied: './ticket_booking.db'
```

**Solution:**
```bash
# Check folder permissions
ls -la

# Ensure you have write access to the directory
# Or use a different location:
SQLALCHEMY_DATABASE_URL = "sqlite:///~/ticket_booking.db"
```

## 🎯 Best Practices

### **Database Configuration**
```python
# Good - Environment-based configuration
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ticket_booking.db")

# Good - Connection pooling for production
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)

# Good - Separate settings for testing
if os.getenv("TESTING"):
    DATABASE_URL = "sqlite:///:memory:"
```

### **Session Management**
```python
# Good - Use dependency injection
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Avoid - Manual session management
def get_users():
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()
```

## 📚 Key Takeaways

### **SQLAlchemy vs Node.js ORMs**

| **Feature** | **SQLAlchemy** | **Sequelize** | **Prisma** |
|-------------|----------------|---------------|------------|
| **Models** | Python classes | JavaScript classes | Schema file |
| **Queries** | `session.query(User)` | `User.findAll()` | `prisma.user.findMany()` |
| **Relations** | `relationship()` | `hasMany()/belongsTo()` | Auto-generated |
| **Migrations** | Alembic | Built-in | Built-in |
| **Type Safety** | Python types | TypeScript | Full TypeScript |

### **Core Concepts**
1. **Engine** - Database connection manager
2. **Session** - Transaction and query interface  
3. **Base** - Parent class for all models
4. **Dependency** - FastAPI integration pattern

## 🚀 Next Steps

Your database foundation is now ready:

1. ✅ **Database engine configured**
2. ✅ **Session factory created**
3. ✅ **Base class ready for models**
4. ✅ **FastAPI dependency function prepared**

**Next: [04 - Models and Relationships →](04-models-and-relationships.md)**

---

**Previous: [← 02 - Virtual Environments](02-virtual-environments.md) | Next: [04 - Models and Relationships →](04-models-and-relationships.md)**
