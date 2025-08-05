from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from app.database import get_db, create_tables

app = FastAPI(
    title="AuthentiCute",
    description="User Authentication and Management System",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    create_tables()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with login/signup options"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AuthentiCute is running!"}

@app.get("/api/db-health")
async def database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        result = db.execute(text("SELECT 1"))
        return {
            "status": "healthy", 
            "message": "Database connection is working!",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": "Database connection failed",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
