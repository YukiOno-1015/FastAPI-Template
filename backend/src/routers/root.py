from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_session
from services.environment_service import EnvironmentService

router = APIRouter(
    prefix="", tags=["index"]  # URLのプレフィックスを追加  # タグを設定
)

@router.get("/healthcheck")
async def healthcheck(db: Session = Depends(get_session)):
    # データベースセッションを使用して EnvironmentService を初期化
    environment_service = EnvironmentService(db=db)
    
    # 環境情報を取得（key_codeは例として"10000002"を指定）
    environment_info = environment_service.get_environment_info_static(key_code="10000002")

    # 取得した環境情報からversionを返す
    return {"version": environment_info.get("values", "unknown")}
