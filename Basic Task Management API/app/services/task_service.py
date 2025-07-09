from typing import List, Optional
from datetime import datetime, timezone
import time

from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    """Custom exception for when a task is not found"""
    pass


class TaskService:
    """
    Task service for managing tasks in memory
    Similar to a service class in Node.js applications
    
    In Node.js, you might have:
    class TaskService {
        constructor() {
            this.tasks = [];
            this.nextId = 1;
        }
        
        async createTask(taskData) { ... }
        async getAllTasks() { ... }
        async getTaskById(id) { ... }
        async updateTask(id, updates) { ... }
        async deleteTask(id) { ... }
    }
    """
    
    def __init__(self):
        """Initialize the service with empty task list"""
        self._tasks: List[Task] = []
        self._next_id: int = 1
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """
        Create a new task
        Similar to: tasks.push(newTask) in JavaScript
        """
        task = Task(
            id=self._next_id,
            title=task_data.title,
            description=task_data.description,
            completed=False
        )
        
        self._tasks.append(task)
        self._next_id += 1
        
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks
        Similar to: return [...tasks] in JavaScript
        """
        return self._tasks.copy()  # Return copy to prevent external modification
    
    def get_task_by_id(self, task_id: int) -> Task:
        """
        Get a task by ID
        Similar to: tasks.find(task => task.id === id) in JavaScript
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        
        raise TaskNotFoundError(f"Task with id {task_id} not found")
    
    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task:
        """
        Update an existing task
        Similar to: Object.assign(existingTask, updates) in JavaScript
        """
        task = self.get_task_by_id(task_id)  # This will raise TaskNotFoundError if not found
        
        # Update only provided fields
        if task_update.title is not None:
            task.title = task_update.title
        
        if task_update.description is not None:
            task.description = task_update.description
        
        if task_update.completed is not None:
            task.completed = task_update.completed
        
        # Update timestamp (add small delay to ensure different timestamp)
        time.sleep(0.001)  # 1ms delay
        task.updated_at = datetime.now(timezone.utc)
        
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID
        Similar to: tasks = tasks.filter(task => task.id !== id) in JavaScript
        """
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                del self._tasks[i]
                return True
        
        raise TaskNotFoundError(f"Task with id {task_id} not found")
    
    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """
        Get tasks filtered by completion status
        Similar to: tasks.filter(task => task.completed === completed) in JavaScript
        """
        return [task for task in self._tasks if task.completed == completed]
    
    def get_task_count(self) -> int:
        """Get total number of tasks"""
        return len(self._tasks)
    
    def clear_all_tasks(self) -> None:
        """Clear all tasks (useful for testing)"""
        self._tasks.clear()
        self._next_id = 1


# Create a global instance (singleton pattern)
# Similar to exporting a single instance in Node.js
task_service = TaskService()
