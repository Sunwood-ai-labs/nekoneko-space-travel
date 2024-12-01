from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# このファイルはAlembicのマイグレーション環境設定を含みます
config = context.config

# Alembicでのロギング設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# モデルのメタデータをインポート
# from myapp.models import Base
target_metadata = None

def get_url():
    """データベースURLを環境変数から取得"""
    return "postgresql://{user}:{password}@{host}/{db}".format(
        user=os.getenv("POSTGRES_USER", "nekoneko"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        db=os.getenv("POSTGRES_DB", "space_travel")
    )

def run_migrations_offline() -> None:
    """
    SQLマイグレーションスクリプトを生成するための
    「オフライン」マイグレーションを実行します。
    """
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
    """
    データベースへの接続を使用してマイグレーションを実行します。
    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is not None:
        configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
