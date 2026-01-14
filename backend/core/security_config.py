"""Configurações de segurança do sistema Jarvis.

REGRAS INVIOLÁVEIS:
- Apenas ações allowlisted
- Mascaramento de PII antes de persistir
- Fail-safe: bloquear por padrão
"""
import re
from typing import List, Dict, Any

# ALLOWED ACTIONS: Apenas ações dentro do sistema
ALLOWED_ACTIONS = [
    "read_memory",
    "write_memory",
    "search_memory",
    "create_skill",
    "update_skill",
    "search_skills",
    "create_note",
    "read_notes",
    "update_note",
    "delete_note",
    "create_task",
    "read_tasks",
    "update_task",
    "complete_task",
    "search_database",
    "query_database",
]

# BLOCKED ACTIONS: Tudo relacionado com SO, rede, deploy
BLOCKED_ACTIONS = [
    "execute_command",
    "run_shell",
    "system_call",
    "network_request",
    "http_request",
    "api_call_external",
    "deploy",
    "install_package",
    "modify_files",
    "read_credentials",
    "write_credentials",
    "spawn_process",
    "create_thread",
    "schedule_task",
    "cron_job",
    "background_worker",
]

# PII PATTERNS: Detectar dados sensíveis
PII_PATTERNS = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "phone": re.compile(r'\b(?:\+?[\d\s()-]{9,})\b'),  # Mais flexível para telefones
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "credit_card": re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'),
    "password": re.compile(r'(?i)password[\s:=]+[\S]+'),
    "token": re.compile(r'(?i)(?:token|key|secret)[\s:=]+[\S]+'),
    "api_key": re.compile(r'(?i)(?:api[_-]?key|apikey)[\s:=]+[\S]+'),
}

# SENSITIVE KEYWORDS
SENSITIVE_KEYWORDS = [
    "password",
    "secret",
    "token",
    "api_key",
    "private_key",
    "credential",
    "auth_token",
]

# MEMORY CONFIG
HOT_MEMORY_TTL_DAYS = 7
MAX_SKILLS_PER_USER = 50
MAX_MEMORIES_PER_REQUEST = 10


def is_action_allowed(action: str) -> bool:
    """Verifica se ação é permitida."""
    return action in ALLOWED_ACTIONS


def is_action_blocked(action: str) -> bool:
    """Verifica se ação é explicitamente bloqueada."""
    return action in BLOCKED_ACTIONS


def contains_sensitive_data(text: str) -> bool:
    """Detecta se texto contém dados sensíveis."""
    text_lower = text.lower()
    
    # Check keywords
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check patterns (exceto email - permitido no chat)
    for pattern_name, pattern in PII_PATTERNS.items():
        if pattern_name == "email":
            continue  # Email permitido no chat
        if pattern.search(text):
            return True
    
    return False


def mask_pii(text: str) -> str:
    """Mascara PII antes de persistir."""
    masked_text = text
    
    # Mask email
    masked_text = PII_PATTERNS["email"].sub("[EMAIL_REDACTED]", masked_text)
    
    # Mask phone
    masked_text = PII_PATTERNS["phone"].sub("[PHONE_REDACTED]", masked_text)
    
    # Mask SSN
    masked_text = PII_PATTERNS["ssn"].sub("[SSN_REDACTED]", masked_text)
    
    # Mask credit card
    masked_text = PII_PATTERNS["credit_card"].sub("[CARD_REDACTED]", masked_text)
    
    # Mask passwords
    masked_text = PII_PATTERNS["password"].sub("[PASSWORD_REDACTED]", masked_text)
    
    # Mask tokens
    masked_text = PII_PATTERNS["token"].sub("[TOKEN_REDACTED]", masked_text)
    
    # Mask API keys
    masked_text = PII_PATTERNS["api_key"].sub("[APIKEY_REDACTED]", masked_text)
    
    return masked_text
