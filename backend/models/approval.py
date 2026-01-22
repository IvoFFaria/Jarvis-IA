"""Modelo de aprovações."""
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone
import uuid
import hashlib
import json


class Approval(BaseModel):
    """Registro de aprovação de ação."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action_type: str
    payload: dict
    payload_hash: str
    approved: bool
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @staticmethod
    def create_hash(payload: dict) -> str:
        """Cria hash do payload."""
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "action_type": "create_note",
                "payload": {"title": "Nova nota", "content": "Conteúdo"},
                "approved": True,
            }
        }


class ApprovalRequest(BaseModel):
    """Request para criar aprovação."""
    user_id: str
    action_type: str
    payload: dict
    approved: bool
