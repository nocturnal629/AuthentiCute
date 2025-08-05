from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from app.database import get_db, create_tables
from app.routes import auth_router, user_router

app = FastAPI(
    title="AuthentiCute",
    description="User Authentication and Management System",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(user_router)

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

@app.get("/verify-email", response_class=HTMLResponse)
async def verify_email_page(request: Request, token: str = None):
    """Email verification page"""
    return templates.TemplateResponse("verify-email.html", {"request": request, "token": token})

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """Forgot password page"""
    return templates.TemplateResponse("forgot-password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str = None):
    """Reset password page"""
    return templates.TemplateResponse("reset-password.html", {"request": request, "token": token})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """User dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

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
