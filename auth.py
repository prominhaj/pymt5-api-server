import uuid
from typing import Dict, Optional
from pydantic import BaseModel

class UserSession(BaseModel):
    token: str
    login: int
    password: str
    server: str
    path: Optional[str] = None

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}

    def create_session(self, login: int, password: str, server: str, path: str = None) -> str:
        # Check if session already exists for this login (optional optimization)
        # For now, always create a new token
        token = str(uuid.uuid4())
        session = UserSession(
            token=token,
            login=login,
            password=password,
            server=server,
            path=path
        )
        self.sessions[token] = session
        return token

    def get_session(self, token: str) -> Optional[UserSession]:
        return self.sessions.get(token)

session_manager = SessionManager()
