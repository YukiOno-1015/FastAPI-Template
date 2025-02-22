import firebase_admin
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

# Firebaseの初期化
cred = credentials.Certificate("./utils/firebase_service_account.json")
firebase_admin.initialize_app(cred)

# Bearer トークンの取得用
security = HTTPBearer()


def verify_firebase_token(auth_credentials: HTTPAuthorizationCredentials = Security(security)):
    """FirebaseのJWTトークンを検証し、ユーザー情報を取得する"""
    token = auth_credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # Firebaseユーザー情報（uid, email など）
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
