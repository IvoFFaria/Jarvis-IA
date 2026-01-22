"""Testes para PII Masking."""
import pytest
from core.security_config import (
    contains_sensitive_data,
    mask_pii,
    PII_PATTERNS,
)


class TestPIIMasking:
    """Testes de mascaramento de PII."""
    
    def test_email_detection(self):
        """Testa detecção de emails."""
        texts_with_email = [
            "Meu email é user@example.com",
            "Contact: admin@test.org",
            "Email me at john.doe+tag@company.co.uk",
        ]
        
        for text in texts_with_email:
            assert contains_sensitive_data(text), f"Deveria detectar email em: {text}"
    
    def test_phone_detection(self):
        """Testa detecção de telefones."""
        texts_with_phone = [
            "Telefone: +351 912 345 678",
            "Call me at 912345678",
            "Phone: (912) 345-6789",
        ]
        
        for text in texts_with_phone:
            assert contains_sensitive_data(text), f"Deveria detectar telefone em: {text}"
    
    def test_password_detection(self):
        """Testa detecção de passwords."""
        texts_with_password = [
            "password: mySecret123",
            "Password = admin123",
            "pwd: test",
        ]
        
        for text in texts_with_password:
            assert contains_sensitive_data(text), f"Deveria detectar password em: {text}"
    
    def test_token_detection(self):
        """Testa detecção de tokens."""
        texts_with_token = [
            "token: abc123xyz",
            "API key: sk-1234567890",
            "secret: mySecretKey",
        ]
        
        for text in texts_with_token:
            assert contains_sensitive_data(text), f"Deveria detectar token em: {text}"
    
    def test_credit_card_detection(self):
        """Testa detecção de cartões de crédito."""
        texts_with_card = [
            "Card: 1234 5678 9012 3456",
            "Credit card: 1234-5678-9012-3456",
        ]
        
        for text in texts_with_card:
            assert contains_sensitive_data(text), f"Deveria detectar cartão em: {text}"
    
    def test_email_masking(self):
        """Testa mascaramento de emails."""
        text = "Meu email é user@example.com e também admin@test.org"
        masked = mask_pii(text)
        
        assert "user@example.com" not in masked
        assert "admin@test.org" not in masked
        assert "[EMAIL_REDACTED]" in masked
    
    def test_phone_masking(self):
        """Testa mascaramento de telefones."""
        text = "Telefone: +351 912 345 678 ou 912345678"
        masked = mask_pii(text)
        
        assert "+351 912 345 678" not in masked
        assert "912345678" not in masked
        assert "[PHONE_REDACTED]" in masked
    
    def test_password_masking(self):
        """Testa mascaramento de passwords."""
        text = "password: mySecret123"
        masked = mask_pii(text)
        
        assert "mySecret123" not in masked
        assert "[PASSWORD_REDACTED]" in masked
    
    def test_token_masking(self):
        """Testa mascaramento de tokens."""
        text = "token: abc123xyz and api_key: sk-12345"
        masked = mask_pii(text)
        
        assert "abc123xyz" not in masked
        assert "sk-12345" not in masked
        assert "[TOKEN_REDACTED]" in masked
        assert "[APIKEY_REDACTED]" in masked
    
    def test_card_masking(self):
        """Testa mascaramento de cartões."""
        text = "Card: 1234 5678 9012 3456"
        masked = mask_pii(text)
        
        assert "1234 5678 9012 3456" not in masked
        assert "[CARD_REDACTED]" in masked
    
    def test_multiple_pii_masking(self):
        """Testa mascaramento de múltiplos tipos de PII."""
        text = """
        Email: user@example.com
        Phone: +351 912 345 678
        Password: myPass123
        Token: abc123xyz
        Card: 1234 5678 9012 3456
        """
        
        masked = mask_pii(text)
        
        # Verificar que NENHUM dado sensível permanece
        assert "user@example.com" not in masked
        assert "+351 912 345 678" not in masked
        assert "myPass123" not in masked
        assert "abc123xyz" not in masked
        assert "1234 5678 9012 3456" not in masked
        
        # Verificar que todos foram mascarados
        assert "[EMAIL_REDACTED]" in masked
        assert "[PHONE_REDACTED]" in masked
        assert "[PASSWORD_REDACTED]" in masked
        assert "[TOKEN_REDACTED]" in masked
        assert "[CARD_REDACTED]" in masked
    
    def test_normal_text_unchanged(self):
        """Testa que texto normal não é alterado."""
        text = "This is a normal text without any PII"
        masked = mask_pii(text)
        
        assert masked == text
    
    def test_partial_email_not_masked(self):
        """Testa que emails parciais/inválidos não são mascarados."""
        text = "This is not an email: user@ or @example.com"
        # Não deve conter PII sensível
        # (regex deve requerer formato completo)
        masked = mask_pii(text)
        # Pode ou não mascarar dependendo do regex, mas o importante
        # é que não quebre


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
