from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

migration = current_app.extensions["migrate"]
engine = migration.db.engine
options = migration.configure_args


def run_migrations():
    if context.is_offline_mode():
        context.configure(
            url=engine.url,
            target_metadata=migration.db.metadata,
            literal_binds=True,
            **options,
        )
        with context.begin_transaction():
            context.run_migrations()
        return

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=migration.db.metadata,
            **options,
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
