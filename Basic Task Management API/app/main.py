from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .core.config import settings
from .routers import tasks_router, ui_router


# Create FastAPI application
# Similar to: const app = express(); in Node.js
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# Add CORS middleware (similar to cors package in Express)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (similar to express.static in Node.js)
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routers
# Similar to: app.use('/api/tasks', taskRouter); in Express.js
app.include_router(tasks_router, prefix="/api")
app.include_router(ui_router)

# Initialize templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint - redirect to UI
    Similar to Express.js:
    app.get('/', (req, res) => {
        res.redirect('/ui/tasks');
    });
    """
    return RedirectResponse(url="/ui/tasks")


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Similar to Express.js:
    app.get('/health', (req, res) => {
        res.json({ status: 'healthy', timestamp: new Date().toISOString() });
    });
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Note: Custom error handlers removed for API compatibility
# In production, you might want to add custom error handlers
# that check the request type (API vs UI) and respond accordingly


# Development server runner
if __name__ == "__main__":
    """
    Run the development server
    Similar to: app.listen(port, () => console.log(`Server running on port ${port}`));
    """
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
