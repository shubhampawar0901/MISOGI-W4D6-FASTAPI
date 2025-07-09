from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from ..schemas.task import TaskCreate, TaskUpdate
from ..services.task_service import task_service, TaskNotFoundError


# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Create UI router
router = APIRouter(
    prefix="/ui",
    tags=["ui"],
    responses={404: {"description": "Page not found"}},
)


@router.get("/", response_class=HTMLResponse)
async def redirect_to_tasks():
    """Redirect root UI to tasks page"""
    return RedirectResponse(url="/ui/tasks", status_code=status.HTTP_302_FOUND)


@router.get("/tasks", response_class=HTMLResponse)
async def get_tasks_page(request: Request):
    """
    Display the main tasks page with all tasks
    Similar to Express.js:
    app.get('/tasks', (req, res) => {
        const tasks = taskService.getAllTasks();
        res.render('tasks', { tasks });
    });
    """
    try:
        tasks = task_service.get_all_tasks()
        return templates.TemplateResponse(
            "tasks.html", 
            {"request": request, "tasks": tasks}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load tasks: {str(e)}"
        )


@router.post("/tasks", response_class=HTMLResponse)
async def create_task_ui(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None)
):
    """
    Create a new task from the web form
    Similar to Express.js:
    app.post('/tasks', (req, res) => {
        const task = taskService.createTask(req.body);
        res.redirect('/tasks');
    });
    """
    try:
        # Create task data
        task_data = TaskCreate(title=title.strip(), description=description.strip() if description else None)
        
        # Create the task
        task_service.create_task(task_data)
        
        # Redirect back to tasks page
        return RedirectResponse(url="/ui/tasks", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        # In a real app, you'd show this error on the form
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.post("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_ui(
    task_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Update a task from the edit form"""
    try:
        task_update = TaskUpdate(
            title=title.strip(),
            description=description.strip() if description else None
        )
        
        task_service.update_task(task_id, task_update)
        return RedirectResponse(url="/ui/tasks", status_code=status.HTTP_302_FOUND)
        
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


@router.post("/tasks/{task_id}/complete", response_class=HTMLResponse)
async def mark_task_complete(task_id: int):
    """Mark a task as completed"""
    try:
        task_update = TaskUpdate(completed=True)
        task_service.update_task(task_id, task_update)
        return RedirectResponse(url="/ui/tasks", status_code=status.HTTP_302_FOUND)
        
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


@router.post("/tasks/{task_id}/incomplete", response_class=HTMLResponse)
async def mark_task_incomplete(task_id: int):
    """Mark a task as incomplete"""
    try:
        task_update = TaskUpdate(completed=False)
        task_service.update_task(task_id, task_update)
        return RedirectResponse(url="/ui/tasks", status_code=status.HTTP_302_FOUND)
        
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


@router.post("/tasks/{task_id}/delete", response_class=HTMLResponse)
async def delete_task_ui(task_id: int):
    """Delete a task"""
    try:
        task_service.delete_task(task_id)
        return RedirectResponse(url="/ui/tasks", status_code=status.HTTP_302_FOUND)
        
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
