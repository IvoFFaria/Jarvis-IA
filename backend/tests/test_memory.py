"""Testes para sistema de memória."""
import pytest
from datetime import datetime, timedelta, timezone
from models.memory import MemoryHot, MemoryCold, MemoryArchive
from core.security_config import HOT_MEMORY_TTL_DAYS


class TestMemoryModels:
    """Testes dos modelos de memória."""
    
    def test_hot_memory_creation(self):
        """Testa criação de memória HOT."""
        expires_at = datetime.now(timezone.utc) + timedelta(days=HOT_MEMORY_TTL_DAYS)
        
        memory = MemoryHot(
            user_id="test_user",
            key="test_key",
            value="test_value",
            tags=["test"],
            expires_at=expires_at,
        )
        
        assert memory.user_id == "test_user"
        assert memory.key == "test_key"
        assert memory.value == "test_value"
        assert "test" in memory.tags
        assert memory.expires_at == expires_at
        assert memory.id is not None
    
    def test_cold_memory_creation(self):
        """Testa criação de memória COLD."""
        memory = MemoryCold(
            user_id="test_user",
            key="test_key",
            value={"data": "test"},
            tags=["test", "permanent"],
        )
        
        assert memory.user_id == "test_user"
        assert memory.key == "test_key"
        assert memory.value == {"data": "test"}
        assert "permanent" in memory.tags
        assert memory.id is not None
    
    def test_archive_memory_creation(self):
        """Testa criação de memória ARCHIVE."""
        memory = MemoryArchive(
            user_id="test_user",
            key="old_key",
            value="old_value",
            tags=["archived"],
            archived_reason="Substituído por nova versão",
            created_at=datetime.now(timezone.utc),
        )
        
        assert memory.user_id == "test_user"
        assert memory.archived_reason == "Substituído por nova versão"
        assert memory.id is not None
    
    def test_hot_memory_ttl_default(self):
        """Testa que HOT memory tem TTL de 7 dias por padrão."""
        assert HOT_MEMORY_TTL_DAYS == 7, "HOT_MEMORY_TTL_DAYS deveria ser 7"
    
    def test_hot_memory_expiry_logic(self):
        """Testa lógica de expiração de HOT memory."""
        now = datetime.now(timezone.utc)
        
        # Memória que expira no futuro (válida)
        future_expires = now + timedelta(days=5)
        valid_memory = MemoryHot(
            user_id="test_user",
            key="valid",
            value="valid",
            tags=[],
            expires_at=future_expires,
        )
        assert valid_memory.expires_at > now, "Memória deveria estar válida"
        
        # Memória que expirou (inválida)
        past_expires = now - timedelta(days=1)
        expired_memory = MemoryHot(
            user_id="test_user",
            key="expired",
            value="expired",
            tags=[],
            expires_at=past_expires,
        )
        assert expired_memory.expires_at < now, "Memória deveria estar expirada"
    
    def test_memory_supports_json_values(self):
        """Testa que memórias suportam valores JSON complexos."""
        complex_value = {
            "nested": {
                "data": [1, 2, 3],
                "info": "test"
            },
            "list": ["a", "b", "c"]
        }
        
        memory = MemoryCold(
            user_id="test_user",
            key="complex",
            value=complex_value,
            tags=["json"],
        )
        
        assert memory.value == complex_value
        assert memory.value["nested"]["data"] == [1, 2, 3]
    
    def test_memory_tags_are_list(self):
        """Testa que tags são sempre lista."""
        memory = MemoryHot(
            user_id="test_user",
            key="test",
            value="test",
            tags=["tag1", "tag2"],
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        
        assert isinstance(memory.tags, list)
        assert len(memory.tags) == 2
    
    def test_memory_default_tags_empty(self):
        """Testa que tags padrão são lista vazia."""
        memory = MemoryCold(
            user_id="test_user",
            key="test",
            value="test",
        )
        
        assert isinstance(memory.tags, list)
        assert len(memory.tags) == 0


class TestMemoryCleanup:
    """Testes de cleanup de memória (inline, sem background)."""
    
    def test_no_background_cleanup_exists(self):
        """Verifica que NÃO existe cleanup em background."""
        import inspect
        from modules import memory
        
        # Buscar por funções que sugerem background processing
        forbidden_patterns = [
            "Thread",
            "Process",
            "cron",
            "schedule",
            "Timer",
            "asyncio.create_task",
            "background",
            "celery",
        ]
        
        source = inspect.getsource(memory)
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"Detectado padrão proibido: {pattern} (background processing não permitido)"
    
    def test_cleanup_is_inline(self):
        """Verifica que cleanup é inline (chamado durante requests)."""
        import inspect
        from modules.memory import MemoryManager
        
        # Verificar que _cleanup_expired_hot_memories é async e não cria tasks
        source = inspect.getsource(MemoryManager._cleanup_expired_hot_memories)
        
        # Não deve criar tasks ou threads
        assert "create_task" not in source
        assert "Thread(" not in source
        assert "Process(" not in source
        
        # Deve ser chamado inline (await)
        assert "async def" in source or "await" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
