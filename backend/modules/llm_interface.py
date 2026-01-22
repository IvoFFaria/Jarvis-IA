"""Interface com LLM (GPT-5.2 via Emergent Universal Key)."""
import os
import logging
from typing import Dict, Any, Optional, List
import asyncio
import uuid

logger = logging.getLogger(__name__)

def _load_emergent():
    """
    Importa Emergent apenas quando necessário (modo real).
    Assim o backend arranca em mock sem depender de emergentintegrations.
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        return LlmChat, UserMessage
    except ImportError as e:
        raise RuntimeError(
            "Emergent selecionado, mas a lib 'emergentintegrations' não está instalada. "
            "Em modo mock isto nunca devia ser chamado."
        ) from e


class LLMInterface:
    """Interface para comunicação com LLM."""
    
    def __init__(self):
        """Inicializa cliente LLM com Emergent Universal Key."""
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY não encontrada nas variáveis de ambiente")
        
        self.provider = "openai"
        self.model = "gpt-5.2"
        logger.info(f"LLM Interface inicializada com {self.provider}/{self.model}")
    
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """Envia mensagens para o LLM e retorna resposta (async).
        
        Args:
            messages: Lista de mensagens [{"role": "user", "content": "..."}]
            temperature: Criatividade (0.0 a 1.0)
        
        Returns:
            Resposta do LLM
        """
        try:
            # Extrair system message e user messages
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                elif msg["role"] == "user":
                    user_messages.append(msg["content"])
            
            # Criar session única
            session_id = str(uuid.uuid4())
            
            # Inicializar chat
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_message or "You are a helpful assistant.",
            ).with_model(self.provider, self.model)
            
            # Enviar última mensagem do usuário
            user_msg = UserMessage(text=user_messages[-1] if user_messages else "")
            response = await chat.send_message(user_msg)
            
            logger.info(f"LLM response received ({len(response)} chars)")
            return response
        
        except Exception as e:
            logger.error(f"Erro ao chamar LLM: {e}")
            raise
    
    async def generate_with_system_prompt(
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
        
        return await self.chat_completion_async(messages, temperature=temperature)
    
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
