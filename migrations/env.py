"""Alembic configuration"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from app import create_app

# this is the Alembic Config object, which provides
# the values of the [alembic] section of the .ini file
# as Python attributes for use in application/module code
# that may change with the engine or repository settings
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
app = create_app()
from app.extensions import db
target_metadata = db.metadata

# other values from the config, defined by the [alembic] section
# can be accessed here by direct indexing, such as:
# my_ident = config.get_main_option("sqlalchemy.ident")

# set sqlalchemy.url from environment variable if present
sqlalchemy_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
if sqlalchemy_url.startswith("postgres://"):
    sqlalchemy_url = sqlalchemy_url.replace("postgres://", "postgresql://", 1)
config.set_main_option("sqlalchemy.url", sqlalchemy_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    engine = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
