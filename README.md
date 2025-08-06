# AuthentiCute

A beautiful and secure User Authentication and Management System built with FastAPI, PostgreSQL, and modern web technologies.

## Features

- 🔐 Secure user authentication with JWT tokens
- 📧 Email verification using Mailgun
- 🎨 Beautiful, responsive UI with Tailwind CSS
- 🚀 FastAPI backend with automatic API documentation
- 🗄️ PostgreSQL database with SQLAlchemy ORM
- 🔒 Password reset functionality
- 👤 User profile management
- 🔑 Google OAuth integration
- 🛡️ Rate limiting and abuse prevention
- 📝 Comprehensive error handling and logging
- 🐳 Docker support for easy deployment

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL database (or Neon cloud database)
- Mailgun account for email verification
- Google Cloud Console account for OAuth

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nocturnal625/AuthentiCute.git
   cd AuthentiCute
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual configuration
   ```

4. **Set up Google OAuth (Optional but Recommended)**
   
   a. Go to [Google Cloud Console](https://console.cloud.google.com/)

   b. Create a new project or select an existing one
   
   c. Enable the Google+ API
   
   d. Go to "Credentials" and create an OAuth 2.0 Client ID
   
   e. Set the authorized redirect URI to: `http://localhost:8000/api/auth/google/callback`
   
   f. Copy the Client ID and Client Secret to your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   ```

5. **Set up the database**
   ```bash
   # Create base tables (users table and other core tables)
   python -c "from app.database import create_tables; create_tables()"
   
   # Apply migrations (creates additional tables and schema changes)
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database Health Check: http://localhost:8000/api/db-health

## Docker Deployment

### Quick Docker Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/nocturnal625/AuthentiCute.git
   cd AuthentiCute
   ```

2. **Set up environment variables (Optional)**
   ```bash
   cp env.example .env
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database Health Check: http://localhost:8000/api/db-health

### Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Stop any running containers
docker-compose down
```

## Project Structure

```
AuthentiCute/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── routes/              # API routes
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS)
├── migrations/              # Database migrations
├── requirements.txt         # Python dependencies
├── run.py                   # Application runner
└── README.md               # This file
```

## License

This project is for educational purposes.
