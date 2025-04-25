# routers/router.py
# APIRouterを生成する共通ユーティリティを使用し、環境情報リロードとヘルスチェックを提供するエンドポイント定義
import logging

from fastapi.responses import HTMLResponse

from commons.environment_master_key import EnvironmentMasterKey
from database.session import get_session
from repositories.environment_repository import EnvironmentRepository
from services.environment_service import EnvironmentService
from utils.protocol import Depends, Session, create_router, get_environment_info_static, version

# Uvicornロガーを使用
LOGGER = logging.getLogger("uvicorn.routers")

# ルーターの生成: ベースパス ''、タグ 'index'
router = create_router(prefix="", tags=["index"])

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/")
@version(0, 1)
async def get():
    return HTMLResponse(html)


@router.get("/reload")
@version(0, 1)
async def memory_reload(db: Session = Depends(get_session)):
    """
    環境情報キャッシュをDBから再読み込みします。

    Args:
        db (Session): データベースセッション (依存注入)

    Returns:
        dict: 実行結果メッセージ
    """
    # リポジトリとサービスを生成し、キャッシュを更新
    repo = EnvironmentRepository(db=db)
    service = EnvironmentService(repository=repo)
    service.refresh_cache()

    LOGGER.info("[Router] Environment cache reloaded")
    return {"message": "Environment cache reloaded successfully"}


@router.get("/healthcheck")
@version(0, 1)
async def healthcheck():
    """
    サービスの健康状態を確認し、バージョン情報を返します。

    Returns:
        dict: キー 'version' に環境設定のバージョン値を含む
    """
    # プロトコルユーティリティ経由で環境情報を取得
    version_value = get_environment_info_static(EnvironmentMasterKey.VERSION)
    LOGGER.info(f"[Router] Healthcheck version: {version_value}")
    return {"version": version_value}
