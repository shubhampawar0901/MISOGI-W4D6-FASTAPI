# 04 - Models and Database Relationships

## 🎯 Learning Objectives

By the end of this section, you will:
- Create SQLAlchemy database models
- Understand foreign keys and relationships
- Implement One-to-Many and Many-to-One relationships
- Design a complete database schema with proper constraints

## 🏗️ Database Schema Design

### **Our Ticket Booking System Schema**

```
Venues (1) ←→ (Many) Events (1) ←→ (Many) Bookings (Many) ←→ (1) TicketTypes

Example:
Madison Square Garden (Venue)
├── Rock Concert (Event) - Jan 15
│   ├── John's Booking - 2 VIP tickets
│   └── Mary's Booking - 1 Standard ticket  
└── Basketball Game (Event) - Jan 20
    └── Bob's Booking - 3 Economy tickets
```

### **Relationship Types**
- **Venues → Events**: One-to-Many (one venue hosts many events)
- **Events → Bookings**: One-to-Many (one event has many bookings)
- **TicketTypes → Bookings**: One-to-Many (one ticket type used in many bookings)

## 📝 Creating Your First Model

### **Step 1: Create models.py**

Create a new file called `models.py`:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
```

### **Understanding the Imports**

| **Import** | **Purpose** | **Node.js Equivalent** |
|------------|-------------|------------------------|
| `Column` | Define table columns | Sequelize DataTypes |
| `Integer, String, Float` | Data types | `DataTypes.INTEGER` |
| `DateTime` | Date/time fields | `DataTypes.DATE` |
| `ForeignKey` | Link tables | `references: { model: 'User' }` |
| `relationship` | Object relationships | `User.hasMany(Post)` |

## 🏢 Creating the Venue Model

### **Step 2: Add Venue Model**

```python
class Venue(Base):
    __tablename__ = 'venues'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    
    # Relationship: One venue can have many events
    events = relationship("Event", back_populates="venue")
```

### **Understanding the Venue Model**

#### **Class Declaration**
```python
class Venue(Base):
```
- **Inherits from `Base`** - Makes it a SQLAlchemy model
- **Python class** - Represents the `venues` table

#### **Table Name**
```python
__tablename__ = 'venues'
```
- **Sets actual table name** in database
- **Without this**: SQLAlchemy uses lowercase class name (`venue`)
- **With this**: You control the exact name (`venues`)

#### **Column Definitions**
```python
id = Column(Integer, primary_key=True, index=True)
```

**Breaking down each parameter:**
- **`Integer`** - Data type (whole numbers)
- **`primary_key=True`** - Unique identifier for each row
- **`index=True`** - Creates database index for faster searches

```python
name = Column(String, nullable=False)
```
- **`String`** - Text data type (VARCHAR in SQL)
- **`nullable=False`** - Field is required (NOT NULL constraint)

#### **Relationship Definition**
```python
events = relationship("Event", back_populates="venue")
```

**What this creates:**
- **Python attribute** `venue.events` - NOT a database column
- **Lazy loading** - Events loaded when accessed
- **Bidirectional** - Event model will have `venue` attribute

**Node.js equivalent:**
```javascript
// Sequelize
Venue.hasMany(Event, { foreignKey: 'venue_id' });
```

## 🎪 Creating the Event Model

### **Step 3: Add Event Model**

```python
class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)
    
    # Relationships
    venue = relationship("Venue", back_populates="events")
    bookings = relationship("Booking", back_populates="event")
```

### **Understanding Foreign Keys**

#### **Foreign Key Column**
```python
venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)
```

**What this does:**
- **Creates `venue_id` column** in events table
- **Links to `venues.id`** - References the venue's primary key
- **Enforces referential integrity** - Can't reference non-existent venue
- **Database constraint** - Prevents orphaned events

**SQL equivalent:**
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    event_date DATETIME NOT NULL,
    venue_id INTEGER NOT NULL,
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);
```

#### **Relationship vs Foreign Key**

```python
venue_id = Column(Integer, ForeignKey('venues.id'))  # Database column
venue = relationship("Venue", back_populates="events")  # Python helper
```

**Key differences:**
- **`venue_id`** - Stores the actual ID number (1, 2, 3...)
- **`venue`** - Gives you the full Venue object

**Usage example:**
```python
event = session.query(Event).first()
print(event.venue_id)    # Prints: 1 (just the ID)
print(event.venue.name)  # Prints: "Madison Square Garden" (full object)
```

## 🎫 Creating the TicketType Model

### **Step 4: Add TicketType Model**

```python
class TicketType(Base):
    __tablename__ = 'ticket_types'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # VIP, Standard, Economy
    price = Column(Float, nullable=False)
    
    # Relationship: One ticket type can have many bookings
    bookings = relationship("Booking", back_populates="ticket_type")
```

### **Understanding Data Types**

| **SQLAlchemy Type** | **Python Type** | **SQL Type** | **Use Case** |
|---------------------|------------------|--------------|--------------|
| `Integer` | `int` | INTEGER | IDs, counts, quantities |
| `String` | `str` | VARCHAR | Names, emails, text |
| `Float` | `float` | REAL | Prices, ratings, percentages |
| `DateTime` | `datetime` | DATETIME | Timestamps, dates |
| `Boolean` | `bool` | BOOLEAN | True/false flags |

## 📋 Creating the Booking Model

### **Step 5: Add Booking Model**

```python
class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, confirmed, cancelled
    
    # Foreign Keys
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey('ticket_types.id'), nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="bookings")
    ticket_type = relationship("TicketType", back_populates="bookings")
```

### **Understanding Default Values**

#### **Static Defaults**
```python
quantity = Column(Integer, nullable=False, default=1)
status = Column(String, default="pending")
```
- **`default=1`** - New bookings start with quantity 1
- **`default="pending"`** - New bookings need confirmation

#### **Dynamic Defaults**
```python
booking_date = Column(DateTime, default=datetime.utcnow)
```
- **`datetime.utcnow`** - Function reference (no parentheses!)
- **Called when row created** - Gets current timestamp
- **UTC timezone** - Best practice for databases

### **Multiple Foreign Keys**

```python
# Booking belongs to both Event and TicketType
event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
ticket_type_id = Column(Integer, ForeignKey('ticket_types.id'), nullable=False)
```

**Why two foreign keys?**
- **Each booking is for one specific event** (which concert?)
- **Each booking has one ticket type** (VIP, Standard, or Economy?)
- **Creates junction table** - Links events and ticket types through bookings

## 🔗 Understanding Relationships

### **One-to-Many Relationships**

#### **From the "One" Side (Venue)**
```python
# In Venue model
events = relationship("Event", back_populates="venue")
```
- **Returns list** of Event objects
- **Plural name** (`events`) indicates multiple items

#### **From the "Many" Side (Event)**
```python
# In Event model  
venue = relationship("Venue", back_populates="events")
```
- **Returns single** Venue object
- **Singular name** (`venue`) indicates one item

### **Bidirectional Relationships**

```python
# Venue side
events = relationship("Event", back_populates="venue")

# Event side
venue = relationship("Venue", back_populates="events")
```

**`back_populates` creates two-way access:**
```python
# From venue to events
venue = session.query(Venue).first()
venue_events = venue.events  # List of events at this venue

# From event to venue
event = session.query(Event).first()
event_venue = event.venue    # The venue hosting this event
```

## 🧪 Testing Your Models

### **Step 6: Test Model Creation**

```bash
# Test if all models can be imported
python -c "from models import Venue, Event, TicketType, Booking; print('All models imported successfully!')"
```

**Expected output:**
```
All models imported successfully!
```

### **Step 7: Create Database Tables**

Create a file called `create_tables.py`:

```python
from database import engine, Base
from models import Venue, Event, TicketType, Booking

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")

# Show what tables were created
print("\nTables created:")
for table_name in Base.metadata.tables.keys():
    print(f"  - {table_name}")
```

Run it:
```bash
python create_tables.py
```

**Expected output:**
```
Creating database tables...
✅ All tables created successfully!

Tables created:
  - venues
  - events
  - ticket_types
  - bookings
```

## 🔍 What Happens Behind the Scenes

### **SQL Table Creation**

When you run `Base.metadata.create_all()`, SQLAlchemy generates:

```sql
-- Venues table (no foreign keys)
CREATE TABLE venues (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    capacity INTEGER NOT NULL,
    address VARCHAR NOT NULL
);

-- Events table (references venues)
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    event_date DATETIME NOT NULL,
    venue_id INTEGER NOT NULL,
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);

-- Ticket types table (no foreign keys)
CREATE TABLE ticket_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    price REAL NOT NULL
);

-- Bookings table (references events and ticket_types)
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    customer_email VARCHAR NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    total_price REAL NOT NULL,
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR DEFAULT 'pending',
    event_id INTEGER NOT NULL,
    ticket_type_id INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (ticket_type_id) REFERENCES ticket_types(id)
);
```

### **Dependency Order**

SQLAlchemy creates tables in the correct order:
1. **First**: `venues` and `ticket_types` (no dependencies)
2. **Second**: `events` (depends on venues)
3. **Third**: `bookings` (depends on events and ticket_types)

## 🚨 Common Issues and Solutions

### **Issue 1: Circular Import Error**

**Problem:**
```python
ImportError: cannot import name 'Event' from partially initialized module 'models'
```

**Solution:**
```python
# Use string references in relationships
events = relationship("Event", back_populates="venue")  # ✅ Good
events = relationship(Event, back_populates="venue")    # ❌ Causes circular import
```

### **Issue 2: Foreign Key Reference Error**

**Problem:**
```python
sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'events.venue_id' could not find table 'venues'
```

**Solution:**
```python
# Ensure you import ALL models before creating tables
from models import Venue, Event, TicketType, Booking  # Import all models
Base.metadata.create_all(bind=engine)
```

### **Issue 3: Relationship Back-Reference Mismatch**

**Problem:**
```python
sqlalchemy.exc.ArgumentError: Error creating backref 'venue' on relationship 'Event.venue': property of that name exists on mapper 'Venue'
```

**Solution:**
```python
# Ensure back_populates names match exactly
# In Venue model:
events = relationship("Event", back_populates="venue")

# In Event model:
venue = relationship("Venue", back_populates="events")  # Must match "events" above
```

## 📚 Key Takeaways

### **Model Design Principles**
1. **One class per table** - Clear separation of concerns
2. **Descriptive names** - `customer_email` not just `email`
3. **Proper constraints** - `nullable=False` for required fields
4. **Sensible defaults** - `status="pending"` for new bookings

### **Relationship Patterns**
1. **Foreign key + relationship** - Always use both together
2. **String references** - Avoid circular imports
3. **Bidirectional relationships** - Use `back_populates`
4. **Plural vs singular** - `events` (many) vs `venue` (one)

### **SQLAlchemy vs Node.js ORMs**

| **Feature** | **SQLAlchemy** | **Sequelize** |
|-------------|----------------|---------------|
| **Model definition** | Python class | JavaScript class |
| **Foreign keys** | `ForeignKey('table.id')` | `references: { model: 'Table' }` |
| **Relationships** | `relationship("Model")` | `hasMany()` / `belongsTo()` |
| **Data types** | `String`, `Integer` | `DataTypes.STRING` |

## 🚀 Next Steps

Your database models are now complete:

1. ✅ **Four models created** (Venue, Event, TicketType, Booking)
2. ✅ **Relationships established** (One-to-Many, Many-to-One)
3. ✅ **Foreign keys configured** (Proper referential integrity)
4. ✅ **Database tables created** (Ready for data)

**Next: [05 - Pydantic Schemas →](05-pydantic-schemas.md)**

---

**Previous: [← 03 - Database Fundamentals](03-database-fundamentals.md) | Next: [05 - Pydantic Schemas →](05-pydantic-schemas.md)**
