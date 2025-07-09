Requirements
Create a simple FastAPI application with in-memory storage for task management.

API Endpoints to Implement
GET /tasks - Fetch all tasks
POST /tasks - Create a new task
PUT /tasks/{task_id} - Update an existing task
DELETE /tasks/{task_id} - Delete a task
Basic UI
Create a simple web UI:

Display all tasks in a list
Form to create new tasks
Buttons to mark tasks as complete/incomplete
Delete buttons for each task
Implementation Notes
Use a simple Python list to store tasks in memory
Generate task IDs using a counter or len() function
Include proper HTTP status codes (200, 201, 404)
Add basic error handling for invalid task IDs