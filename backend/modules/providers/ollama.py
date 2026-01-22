"""Ollama Provider - Local LLM (FREE, sem internet)."""
import os
import logging
from typing import List, Dict
import aiohttp
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Provider para Ollama (local, gratuito)."""
    
    def __init__(self):
        super().__init__()
        self.base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = os.environ.get('OLLAMA_MODEL', 'llama3.1')
        self.available = False
        logger.info(f"Ollama configurado: {self.base_url} | Modelo: {self.model}")
    
    async def check_availability(self) -> bool:
        """Verifica se Ollama está disponível."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    if resp.status == 200:
                        self.available = True
                        logger.info("✅ Ollama disponível")
                        return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama indisponível: {e}")
            self.available = False
        return False
    
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """Chat completion via Ollama."""
        if not await self.check_availability():
            raise ConnectionError("Ollama não está disponível. Instale via: curl -fsSL https://ollama.com/install.sh | sh")
        
        # Converter mensagens para formato Ollama
        prompt = self._format_messages(messages)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data.get('response', '')
                        logger.info(f"Ollama response: {len(response)} chars")
                        return response
                    else:
                        error = await resp.text()
                        raise Exception(f"Ollama error {resp.status}: {error}")
        
        except Exception as e:
            logger.error(f"Erro Ollama: {e}")
            raise
    
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
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Formata mensagens para Ollama."""
        formatted = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                formatted.append(f"System: {content}")
            elif role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        return "\n\n".join(formatted) + "\n\nAssistant:"
