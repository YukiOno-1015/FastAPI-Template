import os
import sys
import importlib
import pkgutil
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

# モジュール検索パスにアプリケーションディレクトリを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Alembic Configオブジェクトを取得
config = context.config

# 環境変数から接続URLを取得し、alembic.iniの設定を上書き
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# ログ設定
fileConfig(config.config_file_name)

# モデルのインポートを遅延させて循環インポートを回避
def import_all_models(directory: str, package: str) -> None:
    """
    指定されたディレクトリ内のすべてのモジュールを動的にインポートする。

    Args:
        directory (str): モジュールが存在するディレクトリパス
        package (str): ベースとなるパッケージ名
    """
    for _, module_name, _ in pkgutil.iter_modules([directory]):
        importlib.import_module(f"{package}.{module_name}")

# モデルの動的インポート
models_directory = os.path.join(os.path.dirname(__file__), '..', 'models')
import_all_models(models_directory, 'models')

# SQLModelのメタデータを使用
target_metadata = SQLModel.metadata

# オフラインマイグレーションの実行
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# オンラインマイグレーションの実行
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
