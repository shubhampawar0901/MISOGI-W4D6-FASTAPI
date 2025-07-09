import pytest
from datetime import datetime

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService, TaskNotFoundError


class TestTaskService:
    """Test the TaskService class"""
    
    def setup_method(self):
        """Set up a fresh TaskService for each test"""
        self.service = TaskService()
    
    def test_create_task(self):
        """Test creating a new task"""
        task_data = TaskCreate(title="Test Task", description="Test Description")
        task = self.service.create_task(task_data)
        
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
    
    def test_get_all_tasks_empty(self):
        """Test getting all tasks when none exist"""
        tasks = self.service.get_all_tasks()
        assert tasks == []
    
    def test_get_all_tasks_with_data(self):
        """Test getting all tasks with data"""
        # Create some tasks
        task1_data = TaskCreate(title="Task 1")
        task2_data = TaskCreate(title="Task 2")
        
        self.service.create_task(task1_data)
        self.service.create_task(task2_data)
        
        tasks = self.service.get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
    
    def test_get_task_by_id_success(self):
        """Test getting a task by ID successfully"""
        task_data = TaskCreate(title="Test Task")
        created_task = self.service.create_task(task_data)
        
        retrieved_task = self.service.get_task_by_id(created_task.id)
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title
    
    def test_get_task_by_id_not_found(self):
        """Test getting a task by ID that doesn't exist"""
        with pytest.raises(TaskNotFoundError):
            self.service.get_task_by_id(999)
    
    def test_update_task_success(self):
        """Test updating a task successfully"""
        # Create a task
        task_data = TaskCreate(title="Original Title", description="Original Description")
        task = self.service.create_task(task_data)
        original_updated_at = task.updated_at
        
        # Update the task
        update_data = TaskUpdate(title="Updated Title", completed=True)
        updated_task = self.service.update_task(task.id, update_data)
        
        assert updated_task.id == task.id
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Original Description"  # Unchanged
        assert updated_task.completed is True
        assert updated_task.updated_at > original_updated_at
    
    def test_update_task_partial(self):
        """Test partial update of a task"""
        # Create a task
        task_data = TaskCreate(title="Original Title", description="Original Description")
        task = self.service.create_task(task_data)
        
        # Update only the completion status
        update_data = TaskUpdate(completed=True)
        updated_task = self.service.update_task(task.id, update_data)
        
        assert updated_task.title == "Original Title"  # Unchanged
        assert updated_task.description == "Original Description"  # Unchanged
        assert updated_task.completed is True  # Changed
    
    def test_update_task_not_found(self):
        """Test updating a task that doesn't exist"""
        update_data = TaskUpdate(title="Updated Title")
        
        with pytest.raises(TaskNotFoundError):
            self.service.update_task(999, update_data)
    
    def test_delete_task_success(self):
        """Test deleting a task successfully"""
        # Create a task
        task_data = TaskCreate(title="Task to Delete")
        task = self.service.create_task(task_data)
        
        # Delete the task
        result = self.service.delete_task(task.id)
        assert result is True
        
        # Verify it's gone
        with pytest.raises(TaskNotFoundError):
            self.service.get_task_by_id(task.id)
    
    def test_delete_task_not_found(self):
        """Test deleting a task that doesn't exist"""
        with pytest.raises(TaskNotFoundError):
            self.service.delete_task(999)
    
    def test_get_tasks_by_status(self):
        """Test filtering tasks by completion status"""
        # Create tasks with different statuses
        task1_data = TaskCreate(title="Incomplete Task")
        task2_data = TaskCreate(title="Complete Task")
        
        task1 = self.service.create_task(task1_data)
        task2 = self.service.create_task(task2_data)
        
        # Mark one as complete
        update_data = TaskUpdate(completed=True)
        self.service.update_task(task2.id, update_data)
        
        # Test filtering
        incomplete_tasks = self.service.get_tasks_by_status(False)
        complete_tasks = self.service.get_tasks_by_status(True)
        
        assert len(incomplete_tasks) == 1
        assert len(complete_tasks) == 1
        assert incomplete_tasks[0].title == "Incomplete Task"
        assert complete_tasks[0].title == "Complete Task"
    
    def test_get_task_count(self):
        """Test getting the total task count"""
        assert self.service.get_task_count() == 0
        
        # Add some tasks
        task1_data = TaskCreate(title="Task 1")
        task2_data = TaskCreate(title="Task 2")
        
        self.service.create_task(task1_data)
        assert self.service.get_task_count() == 1
        
        self.service.create_task(task2_data)
        assert self.service.get_task_count() == 2
    
    def test_clear_all_tasks(self):
        """Test clearing all tasks"""
        # Add some tasks
        task1_data = TaskCreate(title="Task 1")
        task2_data = TaskCreate(title="Task 2")
        
        self.service.create_task(task1_data)
        self.service.create_task(task2_data)
        
        assert self.service.get_task_count() == 2
        
        # Clear all tasks
        self.service.clear_all_tasks()
        
        assert self.service.get_task_count() == 0
        assert self.service.get_all_tasks() == []
