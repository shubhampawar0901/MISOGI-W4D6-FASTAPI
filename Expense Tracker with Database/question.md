Q: 2
Expense Tracker with Database
Requirements
Create a new FastAPI application for expense tracking with SQLite database integration.

API Endpoints to Implement
GET /expenses - Fetch all expenses
POST /expenses - Create a new expense
PUT /expenses/{expense_id} - Update an existing expense
DELETE /expenses/{expense_id} - Delete an expense
GET /expenses/category/{category} - Filter expenses by category
GET /expenses/total - Get total expenses and breakdown by category
Database Setup
Use SQLite database with SQLAlchemy ORM
Create database tables automatically on startup
Implement proper session management
Add sample data for testing
UI Features
Form to add new expenses with amount validation
Display expenses in a table with date formatting
Filter expenses by category dropdown
Show total spending and category breakdown
Delete functionality for each expense
Advanced Requirements
Data Validation: Ensure amount is positive, category is from predefined list
Query Parameters: Support date range filtering (?start_date=2025-07-01&end_date=2025-07-31)
Database Operations: Use proper CRUD operations with error handling
Response Formatting: Format currency amounts properly in UI