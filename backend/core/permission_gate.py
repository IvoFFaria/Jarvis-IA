"""Permission Gate - Núcleo de controle de segurança.

REGRAS:
- Validar todas as ações contra ALLOWED_ACTIONS
- Mascarar PII antes de persistir
- Fail-safe: bloquear por padrão
- Log de todas as decisões
"""
from typing import Dict, Any, Optional
from enum import Enum
import logging
from .security_config import (
    is_action_allowed,
    is_action_blocked,
    contains_sensitive_data,
    mask_pii,
)

logger = logging.getLogger(__name__)


class PermissionLevel(str, Enum):
    """Níveis de permissão do sistema."""
    READ_ONLY = "READ_ONLY"
    DRAFT_ONLY = "DRAFT_ONLY"
    EXECUTE_APPROVED = "EXECUTE_APPROVED"


class ActionValidationResult:
    """Resultado da validação de ação."""
    
    def __init__(
        self,
        allowed: bool,
        reason: str,
        sanitized_data: Optional[Dict[str, Any]] = None,
    ):
        self.allowed = allowed
        self.reason = reason
        self.sanitized_data = sanitized_data


class PermissionGate:
    """Gateway de permissões e validação."""
    
    @staticmethod
    def validate_action(
        action: str,
        permission_level: PermissionLevel,
        data: Optional[Dict[str, Any]] = None,
    ) -> ActionValidationResult:
        """Valida se ação pode ser executada.
        
        Args:
            action: Nome da ação
            permission_level: Nível de permissão atual
            data: Dados da ação (opcional)
        
        Returns:
            ActionValidationResult com decisão
        """
        # 1. Verificar se ação está explicitamente bloqueada
        if is_action_blocked(action):
            logger.warning(f"Ação bloqueada: {action}")
            return ActionValidationResult(
                allowed=False,
                reason=f"Ação '{action}' está na lista de bloqueio (SO/rede/deploy)",
            )
        
        # 2. Verificar se ação está na allowlist
        if not is_action_allowed(action):
            logger.warning(f"Ação não permitida: {action}")
            return ActionValidationResult(
                allowed=False,
                reason=f"Ação '{action}' não está na lista de ações permitidas",
            )
        
        # 3. Verificar nível de permissão
        if permission_level == PermissionLevel.READ_ONLY:
            if action not in ["read_memory", "search_memory", "search_skills", "read_notes", "read_tasks", "search_database"]:
                return ActionValidationResult(
                    allowed=False,
                    reason=f"Permissão READ_ONLY não permite ação '{action}'",
                )
        
        # 4. Sanitizar dados se fornecidos
        sanitized_data = None
        if data:
            sanitized_data = PermissionGate.sanitize_data(data)
        
        logger.info(f"Ação aprovada: {action} (nível: {permission_level})")
        return ActionValidationResult(
            allowed=True,
            reason="Ação validada com sucesso",
            sanitized_data=sanitized_data,
        )
    
    @staticmethod
    def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza dados mascarando PII.
        
        Args:
            data: Dados a sanitizar
        
        Returns:
            Dados sanitizados
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Verificar se contém dados sensíveis
                if contains_sensitive_data(value):
                    logger.warning(f"Dados sensíveis detectados no campo '{key}'")
                
                # Mascarar PII
                sanitized[key] = mask_pii(value)
            elif isinstance(value, dict):
                sanitized[key] = PermissionGate.sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    PermissionGate.sanitize_data(item) if isinstance(item, dict)
                    else mask_pii(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def requires_approval(action: str, permission_level: PermissionLevel) -> bool:
        """Verifica se ação requer aprovação explícita.
        
        Args:
            action: Nome da ação
            permission_level: Nível de permissão
        
        Returns:
            True se requer aprovação
        """
        # Ações de escrita sempre requerem aprovação em EXECUTE_APPROVED
        write_actions = [
            "write_memory",
            "create_skill",
            "update_skill",
            "create_note",
            "update_note",
            "delete_note",
            "create_task",
            "update_task",
            "complete_task",
            "query_database",
        ]
        
        if permission_level == PermissionLevel.EXECUTE_APPROVED:
            return action in write_actions
        
        # DRAFT_ONLY nunca executa, apenas propõe
        if permission_level == PermissionLevel.DRAFT_ONLY:
            return True
        
        return False
