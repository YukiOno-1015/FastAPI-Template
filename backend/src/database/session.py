from sqlalchemy.orm import sessionmaker
from .connection import engine

# SQLAlchemyのセッション作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DBセッションをリクエストごとに管理
def get_session():
    """
    データベースセッションを取得するジェネレータ関数。
    リクエストごとにセッションを生成し、終了時に閉じる。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
