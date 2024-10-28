import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.exc import ArgumentError

# .envファイルの読み込み
load_dotenv()

# 環境変数からデータベースURLを取得
database_url = os.getenv("DATABASE_URL")

# データベースエンジンの作成
if not database_url:
    raise ValueError("環境変数 'DATABASE_URL' が設定されていません。")

try:
    engine = create_engine(database_url, echo=True)
    print("データベースエンジンが正常に作成されました。")
except ArgumentError as e:
    raise ValueError(f"データベースエンジンの作成中にエラーが発生しました: {e}")
