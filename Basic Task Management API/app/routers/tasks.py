from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from ..services.task_service import task_service, TaskNotFoundError


# Create router - similar to Express Router
# const router = express.Router(); in Node.js
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)


@router.get("/", response_model=TaskListResponse, summary="Get all tasks")
async def get_all_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status")
):
    """
    Get all tasks with optional filtering
    
    Similar to Express.js:
    router.get('/', async (req, res) => {
        const { completed } = req.query;
        const tasks = await taskService.getAllTasks(completed);
        res.json({ tasks, total: tasks.length });
    });
    """
    try:
        if completed is not None:
            tasks = task_service.get_tasks_by_status(completed)
        else:
            tasks = task_service.get_all_tasks()
        
        # Convert Task objects to TaskResponse format
        task_responses = [
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ]
        
        return TaskListResponse(tasks=task_responses, total=len(task_responses))
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Create a new task")
async def create_task(task_data: TaskCreate):
    """
    Create a new task
    
    Similar to Express.js:
    router.post('/', async (req, res) => {
        const task = await taskService.createTask(req.body);
        res.status(201).json(task);
    });
    """
    try:
        task = task_service.create_task(task_data)
        
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse, summary="Get a task by ID")
async def get_task(task_id: int):
    """
    Get a specific task by ID
    
    Similar to Express.js:
    router.get('/:taskId', async (req, res) => {
        const task = await taskService.getTaskById(req.params.taskId);
        if (!task) return res.status(404).json({ error: 'Task not found' });
        res.json(task);
    });
    """
    try:
        task = task_service.get_task_by_id(task_id)
        
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskResponse, summary="Update a task")
async def update_task(task_id: int, task_update: TaskUpdate):
    """
    Update an existing task

    Similar to Express.js:
    router.put('/:taskId', async (req, res) => {
        const task = await taskService.updateTask(req.params.taskId, req.body);
        if (!task) return res.status(404).json({ error: 'Task not found' });
        res.json(task);
    });
    """
    try:
        task = task_service.update_task(task_id, task_update)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
async def delete_task(task_id: int):
    """
    Delete a task

    Similar to Express.js:
    router.delete('/:taskId', async (req, res) => {
        const deleted = await taskService.deleteTask(req.params.taskId);
        if (!deleted) return res.status(404).json({ error: 'Task not found' });
        res.status(204).send();
    });
    """
    try:
        task_service.delete_task(task_id)
        # 204 No Content - successful deletion with no response body
        return None

    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )
