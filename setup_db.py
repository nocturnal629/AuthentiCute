#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🚀 Setting up AuthentiCute database...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    print(f"✅ Database URL found: {database_url[:20]}...")
    
    try:
        from app.database import engine, create_tables
        from app.models import User
        from sqlalchemy import text
        
        print("📊 Creating database tables...")
        create_tables()
        print("✅ Database tables created successfully!")
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection test successful!")
        
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Run 'alembic revision --autogenerate -m \"Initial migration\"'")
        print("2. Run 'alembic upgrade head'")
        print("3. Start the application with 'python run.py'")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
