"""Testes para Permission Gate."""
import pytest
from core.permission_gate import PermissionGate, PermissionLevel, ActionValidationResult
from core.security_config import ALLOWED_ACTIONS, BLOCKED_ACTIONS


class TestPermissionGate:
    """Testes do Permission Gate."""
    
    def test_blocked_action_is_rejected(self):
        """Testa que ações bloqueadas são rejeitadas."""
        for blocked_action in BLOCKED_ACTIONS:
            result = PermissionGate.validate_action(
                blocked_action,
                PermissionLevel.EXECUTE_APPROVED
            )
            assert result.allowed is False, f"Ação bloqueada {blocked_action} deveria ser rejeitada"
            assert "bloqueio" in result.reason.lower() or "blocked" in result.reason.lower()
    
    def test_unknown_action_is_rejected(self):
        """Testa que ações desconhecidas são rejeitadas (fail-safe)."""
        unknown_actions = [
            "hack_system",
            "delete_database",
            "spawn_process",
            "create_backdoor",
            "execute_arbitrary_code",
        ]
        
        for unknown_action in unknown_actions:
            result = PermissionGate.validate_action(
                unknown_action,
                PermissionLevel.EXECUTE_APPROVED
            )
            assert result.allowed is False, f"Ação desconhecida {unknown_action} deveria ser rejeitada"
    
    def test_allowed_action_is_accepted(self):
        """Testa que ações permitidas são aceitas."""
        for allowed_action in ALLOWED_ACTIONS:
            result = PermissionGate.validate_action(
                allowed_action,
                PermissionLevel.EXECUTE_APPROVED
            )
            assert result.allowed is True, f"Ação permitida {allowed_action} deveria ser aceita"
    
    def test_read_only_blocks_write_actions(self):
        """Testa que READ_ONLY bloqueia ações de escrita."""
        write_actions = [
            "write_memory",
            "create_skill",
            "update_skill",
            "create_note",
            "delete_note",
        ]
        
        for write_action in write_actions:
            result = PermissionGate.validate_action(
                write_action,
                PermissionLevel.READ_ONLY
            )
            assert result.allowed is False, f"READ_ONLY deveria bloquear {write_action}"
    
    def test_read_only_allows_read_actions(self):
        """Testa que READ_ONLY permite ações de leitura."""
        read_actions = [
            "read_memory",
            "search_memory",
            "read_notes",
            "read_tasks",
            "search_database",
        ]
        
        for read_action in read_actions:
            result = PermissionGate.validate_action(
                read_action,
                PermissionLevel.READ_ONLY
            )
            assert result.allowed is True, f"READ_ONLY deveria permitir {read_action}"
    
    def test_sanitize_data_removes_pii(self):
        """Testa que sanitize_data remove PII."""
        data = {
            "email": "user@example.com",
            "phone": "+351 912 345 678",
            "password": "password: mySecretPass123",
            "token": "token: abc123xyz",
            "normal_text": "This is normal text",
        }
        
        sanitized = PermissionGate.sanitize_data(data)
        
        # Verificar que PII foi mascarado
        assert "[EMAIL_REDACTED]" in sanitized["email"]
        assert "[PHONE_REDACTED]" in sanitized["phone"]
        assert "[PASSWORD_REDACTED]" in sanitized["password"]
        assert "[TOKEN_REDACTED]" in sanitized["token"]
        
        # Verificar que texto normal permanece
        assert sanitized["normal_text"] == "This is normal text"
    
    def test_requires_approval_for_write_actions(self):
        """Testa que ações de escrita requerem aprovação."""
        write_actions = [
            "write_memory",
            "create_skill",
            "update_note",
            "delete_note",
            "query_database",
        ]
        
        for write_action in write_actions:
            requires = PermissionGate.requires_approval(
                write_action,
                PermissionLevel.EXECUTE_APPROVED
            )
            assert requires is True, f"{write_action} deveria requerer aprovação"
    
    def test_draft_only_always_requires_approval(self):
        """Testa que DRAFT_ONLY sempre requer aprovação."""
        for action in ALLOWED_ACTIONS:
            requires = PermissionGate.requires_approval(
                action,
                PermissionLevel.DRAFT_ONLY
            )
            assert requires is True, f"DRAFT_ONLY deveria sempre requerer aprovação para {action}"
    
    def test_nested_pii_is_sanitized(self):
        """Testa que PII em estruturas aninhadas é sanitizado."""
        data = {
            "user": {
                "email": "test@example.com",
                "profile": {
                    "phone": "912345678",
                }
            },
            "credentials": {
                "password": "password: secret123"
            }
        }
        
        sanitized = PermissionGate.sanitize_data(data)
        
        # Verificar sanitização em níveis aninhados
        assert "[EMAIL_REDACTED]" in sanitized["user"]["email"]
        assert "[PHONE_REDACTED]" in sanitized["user"]["profile"]["phone"]
        assert "[PASSWORD_REDACTED]" in sanitized["credentials"]["password"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
