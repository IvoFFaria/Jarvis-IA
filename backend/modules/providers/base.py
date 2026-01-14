"""Provider base para LLMs."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Classe base para todos os providers de LLM."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        logger.info(f"Provider inicializado: {self.name}")
    
    @abstractmethod
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """Envia mensagens e retorna resposta."""
        pass
    
    @abstractmethod
    async def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
    ) -> str:
        """Gera resposta com system prompt."""
        pass
    
    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extrai JSON da resposta."""
        import json
        import re
        
        # Tentar extrair JSON entre ```json e ```
        json_match = re.search(r'```json\s*(.+?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Tentar parse direto
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Tentar extrair JSON do meio da string
        json_match = re.search(r'\{.+\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
