from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session
from database.connection import engine
from models.environment_info import EnvironmentInfo
from app_state import environment_info_static
from services.environment_service import EnvironmentService

app = FastAPI()

# アプリ起動時にDBのテーブルを作成
@app.on_event("startup")
async def on_startup():
    SQLModel.metadata.create_all(bind=engine)
    
    # EnvironmentInfoの情報を取得して静的変数に格納
    with Session(engine) as session:
        infos = session.query(EnvironmentInfo).all()
        service = EnvironmentService(db=session)
        service.update_environment_info_static()
        print(f"Loaded EnvironmentInfo Size: {len(environment_info_static)}")
