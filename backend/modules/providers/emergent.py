"""Emergent Provider - Placeholder para futuro."""
import os
import logging
from typing import List, Dict
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class EmergentProvider(BaseLLMProvider):
    """Provider para Emergent Universal Key (futuro)."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get('EMERGENT_LLM_KEY', '')
        self.model = os.environ.get('EMERGENT_MODEL', 'gpt-5.2')
        
        if not self.api_key:
            logger.warning("⚠️ EMERGENT_LLM_KEY não configurada")
        else:
            logger.info(f"Emergent configurado: {self.model}")
    
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """Chat completion via Emergent."""
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY não configurada. Configure no .env")
        
        # TODO: Implementar quando necessário
        # from emergentintegrations.llm.chat import LlmChat, UserMessage
        raise NotImplementedError("EmergentProvider ainda não implementado. Use 'ollama' ou 'mock'")
    
    async def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
    ) -> str:
        """Gera com system prompt."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        return await self.chat_completion_async(messages, temperature)
