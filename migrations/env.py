from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.database import Base
from app.models import User, UserSession, EmailVerificationToken, PasswordResetToken

target_metadata = Base.metadata

def get_url():
    url = os.getenv("DATABASE_URL")
    if url and url.startswith("postgresql+psycopg://"):
        return url
    elif url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://")
    return url

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    if "sqlalchemy.url" in configuration:
        url = configuration["sqlalchemy.url"]
        if url and not url.startswith("postgresql+psycopg://"):
            configuration["sqlalchemy.url"] = url.replace("postgresql://", "postgresql+psycopg://")
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 