import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# 環境変数からデータベースURLを取得
database_url = os.getenv("DATABASE_URL")

# データベースエンジンの作成
engine = create_engine(database_url, echo=True)
