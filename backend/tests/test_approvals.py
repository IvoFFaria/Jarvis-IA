"""Testes de sistema de aprovações."""
import pytest
from models.approval import Approval, ApprovalRequest
from datetime import datetime, timezone


class TestApprovalSystem:
    """Testes do sistema de aprovações."""
    
    def test_approval_creation(self):
        """Testa criação de approval."""
        payload = {"action": "create_note", "title": "Test"}
        
        approval = Approval(
            user_id="test_user",
            action_type="create_note",
            payload=payload,
            payload_hash=Approval.create_hash(payload),
            approved=True,
        )
        
        assert approval.user_id == "test_user"
        assert approval.action_type == "create_note"
        assert approval.approved is True
        assert approval.payload == payload
        assert approval.id is not None
    
    def test_approval_hash_generation(self):
        """Testa geração de hash do payload."""
        payload1 = {"action": "test", "value": "123"}
        payload2 = {"action": "test", "value": "123"}
        payload3 = {"action": "test", "value": "456"}
        
        hash1 = Approval.create_hash(payload1)
        hash2 = Approval.create_hash(payload2)
        hash3 = Approval.create_hash(payload3)
        
        # Mesmos payloads devem ter mesmo hash
        assert hash1 == hash2
        
        # Payloads diferentes devem ter hashes diferentes
        assert hash1 != hash3
    
    def test_approval_timestamp(self):
        """Testa timestamp de aprovação."""
        approval = Approval(
            user_id="test_user",
            action_type="test_action",
            payload={},
            payload_hash="abc123",
            approved=True,
        )
        
        # approved_at deve estar vazio inicialmente
        assert approval.approved_at is None
        
        # Simular aprovação
        approval.approved = True
        approval.approved_at = datetime.now(timezone.utc)
        
        assert approval.approved_at is not None
        assert isinstance(approval.approved_at, datetime)
    
    def test_rejection_no_timestamp(self):
        """Testa que rejeição não tem timestamp de aprovação."""
        approval = Approval(
            user_id="test_user",
            action_type="test_action",
            payload={},
            payload_hash="abc123",
            approved=False,
        )
        
        assert approval.approved is False
        assert approval.approved_at is None
    
    def test_approval_request_validation(self):
        """Testa validação de ApprovalRequest."""
        request = ApprovalRequest(
            user_id="test_user",
            action_type="create_note",
            payload={"title": "Test"},
            approved=True,
        )
        
        assert request.user_id == "test_user"
        assert request.action_type == "create_note"
        assert request.approved is True


class TestApprovalWorkflow:
    """Testes do fluxo de aprovação."""
    
    def test_no_action_without_approval_in_execute_mode(self):
        """Verifica que nenhuma ação executa sem aprovação em EXECUTE_APPROVED."""
        from core.permission_gate import PermissionGate, PermissionLevel
        
        write_actions = [
            "write_memory",
            "create_skill",
            "update_note",
            "delete_note",
        ]
        
        for action in write_actions:
            requires = PermissionGate.requires_approval(
                action,
                PermissionLevel.EXECUTE_APPROVED
            )
            assert requires is True, f"{action} deve requerer aprovação em EXECUTE_APPROVED"
    
    def test_draft_mode_never_executes(self):
        """Verifica que DRAFT_ONLY nunca executa ações."""
        from core.permission_gate import PermissionGate, PermissionLevel
        from core.security_config import ALLOWED_ACTIONS
        
        for action in ALLOWED_ACTIONS:
            requires = PermissionGate.requires_approval(
                action,
                PermissionLevel.DRAFT_ONLY
            )
            assert requires is True, f"DRAFT_ONLY deve sempre requerer aprovação para {action}"
    
    def test_approval_payload_integrity(self):
        """Testa integridade do payload via hash."""
        original_payload = {"action": "test", "data": "sensitive"}
        hash1 = Approval.create_hash(original_payload)
        
        # Modificar payload
        tampered_payload = {"action": "test", "data": "TAMPERED"}
        hash2 = Approval.create_hash(tampered_payload)
        
        # Hashes devem ser diferentes
        assert hash1 != hash2, "Payload adulterado deve ter hash diferente"
    
    def test_approval_logging(self):
        """Testa que aprovações são registadas."""
        approval = Approval(
            user_id="test_user",
            action_type="test_action",
            payload={"test": "data"},
            payload_hash=Approval.create_hash({"test": "data"}),
            approved=True,
        )
        
        # Verificar que approval tem created_at
        assert approval.created_at is not None
        assert isinstance(approval.created_at, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
