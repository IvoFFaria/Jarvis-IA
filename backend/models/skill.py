"""Modelo de Skills (procedimentos reutilizáveis)."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


class SkillInput(BaseModel):
    """Input de uma skill."""
    name: str
    type: str  # string, number, boolean, object
    description: str
    required: bool = True


class SkillOutput(BaseModel):
    """Output de uma skill."""
    name: str
    type: str
    description: str


class SkillStep(BaseModel):
    """Passo de execução de uma skill."""
    order: int
    description: str
    action: str  # Ação (deve estar em ALLOWED_ACTIONS)
    params: Dict[str, Any] = Field(default_factory=dict)


class SkillTest(BaseModel):
    """Teste de uma skill."""
    description: str
    input: Dict[str, Any]
    expected_output: Any


class Skill(BaseModel):
    """Skill: procedimento reutilizável."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    when_to_use: str  # Condições para usar esta skill
    inputs: List[SkillInput] = Field(default_factory=list)
    outputs: List[SkillOutput] = Field(default_factory=list)
    steps: List[SkillStep]  # SOP (Standard Operating Procedure)
    code_snippet: Optional[str] = None  # Código opcional (não executável)
    tests: List[SkillTest] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    version: int = 1
    is_enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "create_daily_summary",
                "description": "Cria sumário diário de tarefas",
                "when_to_use": "Quando utilizador pede sumário do dia ou relatório diário",
                "inputs": [
                    {"name": "date", "type": "string", "description": "Data do sumário", "required": True}
                ],
                "outputs": [
                    {"name": "summary", "type": "string", "description": "Sumário formatado"}
                ],
                "steps": [
                    {"order": 1, "description": "Buscar tarefas do dia", "action": "read_tasks", "params": {}},
                    {"order": 2, "description": "Gerar sumário", "action": "create_note", "params": {}},
                ],
                "tags": ["summary", "tasks", "daily"],
            }
        }


class SkillCreateRequest(BaseModel):
    """Request para criar skill."""
    name: str
    description: str
    when_to_use: str
    inputs: List[SkillInput] = Field(default_factory=list)
    outputs: List[SkillOutput] = Field(default_factory=list)
    steps: List[SkillStep]
    code_snippet: Optional[str] = None
    tests: List[SkillTest] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class SkillUpdateRequest(BaseModel):
    """Request para atualizar skill."""
    name: Optional[str] = None
    description: Optional[str] = None
    when_to_use: Optional[str] = None
    steps: Optional[List[SkillStep]] = None
    code_snippet: Optional[str] = None
    tests: Optional[List[SkillTest]] = None
    risks: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_enabled: Optional[bool] = None
