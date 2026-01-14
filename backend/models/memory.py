"""Modelos de memória do sistema."""
from pydantic import BaseModel, Field
from typing import List, Any, Optional
from datetime import datetime, timezone
import uuid


class MemoryHot(BaseModel):
    """Memória de curto prazo (TTL: 7 dias)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    key: str
    value: Any  # JSON
    tags: List[str] = Field(default_factory=list)
    expires_at: datetime
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "key": "preferred_language",
                "value": "português",
                "tags": ["preference", "language"],
            }
        }


class MemoryCold(BaseModel):
    """Memória de longo prazo (permanente)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    key: str
    value: Any  # JSON
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "key": "work_schedule",
                "value": {"start": "09:00", "end": "18:00"},
                "tags": ["work", "schedule"],
            }
        }


class MemoryArchive(BaseModel):
    """Memória arquivada (histórico)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    key: str
    value: Any  # JSON
    tags: List[str] = Field(default_factory=list)
    archived_reason: str
    created_at: datetime
    archived_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "key": "old_preference",
                "value": "some_value",
                "archived_reason": "Substituído por nova preferência",
            }
        }


class MemoryProcessRequest(BaseModel):
    """Request para processar memória."""
    user_id: str
    conversation_chunk: str
    context: Optional[dict] = None


class MemoryProcessResponse(BaseModel):
    """Response do processamento de memória."""
    hot_created: List[MemoryHot] = Field(default_factory=list)
    cold_created: List[MemoryCold] = Field(default_factory=list)
    archived: List[MemoryArchive] = Field(default_factory=list)
    skills_created: List[str] = Field(default_factory=list)  # IDs
    summary: str
