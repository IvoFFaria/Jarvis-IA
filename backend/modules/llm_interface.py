"""Interface com LLM (GPT-5.2 via Emergent Universal Key)."""
import os
import logging
from typing import Dict, Any, Optional, List
from emergentintegrations import OpenAI

logger = logging.getLogger(__name__)


class LLMInterface:
    """Interface para comunicação com LLM."""
    
    def __init__(self):
        """Inicializa cliente OpenAI com Emergent Universal Key."""
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY não encontrada nas variáveis de ambiente")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-5.2"
        logger.info(f"LLM Interface inicializada com modelo {self.model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Envia mensagens para o LLM e retorna resposta.
        
        Args:
            messages: Lista de mensagens [{"role": "user", "content": "..."}]
            temperature: Criatividade (0.0 a 1.0)
            max_tokens: Máximo de tokens na resposta
        
        Returns:
            Resposta do LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content
            logger.info(f"LLM response received ({len(content)} chars)")
            return content
        
        except Exception as e:
            logger.error(f"Erro ao chamar LLM: {e}")
            raise
    
    def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
    ) -> str:
        """Gera resposta com system prompt customizado.
        
        Args:
            system_prompt: Prompt do sistema
            user_message: Mensagem do utilizador
            temperature: Criatividade
        
        Returns:
            Resposta do LLM
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        
        return self.chat_completion(messages, temperature=temperature)
    
    def extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrai JSON da resposta do LLM.
        
        Args:
            response: Resposta do LLM
        
        Returns:
            Dict com JSON extraído ou None
        """
        import json
        import re
        
        # Tentar extrair JSON entre ```json e ```
        json_match = re.search(r'```json\s*(.+?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Tentar extrair JSON direto
        json_match = re.search(r'\{.+\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        logger.warning("Não foi possível extrair JSON da resposta")
        return None
