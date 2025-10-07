from logging.config import fileConfig
import os, sys, pathlib
from alembic import context
from sqlalchemy import engine_from_config, pool

WHITELIST_SCHEMAS = {"form"}

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from app.db.base import Base 

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def include_name(name, type_, parent_names):
    """
    Only include objects that belong to schemas we manage.
    This keeps Supabase's auth/storage/realtime/vault/public objects out of diffs.
    """
    schema = parent_names.get("schema_name")
    if type_ == "schema":
        return name in WHITELIST_SCHEMAS
    return schema in WHITELIST_SCHEMAS

def get_url():
    return os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

def run_migrations_offline():
    context.configure(
        url=get_url(),                 # or url=... in offline
        target_metadata=target_metadata,
        include_schemas=True,
        include_name=include_name,             # <-- add this
        version_table_schema="public",         # or "form" if you prefer
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {**config.get_section(config.config_ini_section), "sqlalchemy.url": get_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,                 # or url=... in offline
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,             # <-- add this
            version_table_schema="public",         # or "form" if you prefer
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
