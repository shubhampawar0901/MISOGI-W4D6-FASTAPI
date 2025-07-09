import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.task_service import task_service


class TestTaskAPI:
    """Test the Task API endpoints"""
    
    def setup_method(self):
        """Set up a fresh test environment for each test"""
        # Clear all tasks before each test
        task_service.clear_all_tasks()
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_get_all_tasks_empty(self):
        """Test getting all tasks when none exist"""
        response = self.client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0
    
    def test_create_task_success(self):
        """Test creating a new task successfully"""
        task_data = {
            "title": "Test Task",
            "description": "Test Description"
        }
        
        response = self.client.post("/api/tasks", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["completed"] is False
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_task_validation_error(self):
        """Test creating a task with invalid data"""
        # Missing required title
        task_data = {"description": "Test Description"}
        
        response = self.client.post("/api/tasks", json=task_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_task_title_too_long(self):
        """Test creating a task with title too long"""
        task_data = {
            "title": "x" * 201,  # Exceeds 200 character limit
            "description": "Test Description"
        }
        
        response = self.client.post("/api/tasks", json=task_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_task_by_id_success(self):
        """Test getting a specific task by ID"""
        # First create a task
        task_data = {"title": "Test Task", "description": "Test Description"}
        create_response = self.client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Then get it by ID
        response = self.client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
    
    def test_get_task_by_id_not_found(self):
        """Test getting a task that doesn't exist"""
        response = self.client.get("/api/tasks/999")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_update_task_success(self):
        """Test updating a task successfully"""
        # First create a task
        task_data = {"title": "Original Title", "description": "Original Description"}
        create_response = self.client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Then update it
        update_data = {
            "title": "Updated Title",
            "completed": True
        }
        
        response = self.client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Updated Title"
        assert data["description"] == "Original Description"  # Unchanged
        assert data["completed"] is True
    
    def test_update_task_partial(self):
        """Test partial update of a task"""
        # First create a task
        task_data = {"title": "Original Title", "description": "Original Description"}
        create_response = self.client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Update only completion status
        update_data = {"completed": True}
        
        response = self.client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Original Title"  # Unchanged
        assert data["completed"] is True  # Changed
    
    def test_update_task_not_found(self):
        """Test updating a task that doesn't exist"""
        update_data = {"title": "Updated Title"}
        
        response = self.client.put("/api/tasks/999", json=update_data)
        assert response.status_code == 404
    
    def test_delete_task_success(self):
        """Test deleting a task successfully"""
        # First create a task
        task_data = {"title": "Task to Delete"}
        create_response = self.client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Then delete it
        response = self.client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = self.client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 404
    
    def test_delete_task_not_found(self):
        """Test deleting a task that doesn't exist"""
        response = self.client.delete("/api/tasks/999")
        assert response.status_code == 404
    
    def test_get_tasks_with_filter(self):
        """Test getting tasks with completion status filter"""
        # Create tasks with different statuses
        task1_data = {"title": "Incomplete Task"}
        task2_data = {"title": "Complete Task"}
        
        # Create tasks
        response1 = self.client.post("/api/tasks", json=task1_data)
        task1_id = response1.json()["id"]
        
        response2 = self.client.post("/api/tasks", json=task2_data)
        task2_id = response2.json()["id"]
        
        # Mark one as complete
        self.client.put(f"/api/tasks/{task2_id}", json={"completed": True})
        
        # Test filtering for incomplete tasks
        response = self.client.get("/api/tasks?completed=false")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["tasks"][0]["title"] == "Incomplete Task"
        
        # Test filtering for complete tasks
        response = self.client.get("/api/tasks?completed=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["tasks"][0]["title"] == "Complete Task"
    
    def test_full_crud_workflow(self):
        """Test a complete CRUD workflow"""
        # 1. Create a task
        task_data = {"title": "CRUD Test Task", "description": "Testing CRUD operations"}
        create_response = self.client.post("/api/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # 2. Read the task
        read_response = self.client.get(f"/api/tasks/{task_id}")
        assert read_response.status_code == 200
        assert read_response.json()["title"] == "CRUD Test Task"
        
        # 3. Update the task
        update_data = {"title": "Updated CRUD Task", "completed": True}
        update_response = self.client.put(f"/api/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated CRUD Task"
        assert update_response.json()["completed"] is True
        
        # 4. Delete the task
        delete_response = self.client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == 204
        
        # 5. Verify deletion
        final_read_response = self.client.get(f"/api/tasks/{task_id}")
        assert final_read_response.status_code == 404
