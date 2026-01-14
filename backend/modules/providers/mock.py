"""Mock LLM Provider para testes sem saldo."""
import logging
from typing import Dict, Any, Optional, List
import json
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class MockProvider(BaseLLMProvider):
    """Provider mock para testes sem chamar LLM real."""
    
    def __init__(self):
        """Inicializa mock interface."""
        logger.info("MockLLMInterface inicializada (modo de testes)")
    
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """Mock de chat completion.
        
        Returns:
            Resposta mock previsível
        """
        # Extrair última mensagem do usuário
        user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        last_message = user_messages[-1] if user_messages else ""
        
        logger.info(f"Mock LLM recebeu: {last_message[:100]}")
        
        # Resposta mock baseada em palavras-chave
        if "nome" in last_message.lower() or "quem" in last_message.lower():
            return "Olá! Eu sou o Jarvis, seu assistente de IA em modo de testes (mock). Como posso ajudá-lo?"
        elif "tarefa" in last_message.lower() or "task" in last_message.lower():
            return json.dumps({
                "response": "Posso ajudá-lo a gerenciar tarefas. Gostaria de criar uma nova tarefa?",
                "action": "read_tasks",
                "payload": {"filter": "today"}
            })
        elif "memória" in last_message.lower() or "lembrar" in last_message.lower():
            return json.dumps({
                "response": "Vou guardar essa informação na memória.",
                "action": "write_memory",
                "payload": {"key": "test_memory", "value": "test_value"}
            })
        else:
            return "Entendi. Estou em modo mock, então esta é uma resposta de teste. Como posso ajudá-lo?"
    
    async def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
    ) -> str:
        """Mock de generate_with_system_prompt.
        
        Returns:
            Resposta JSON mock para memory processing
        """
        logger.info(f"Mock recebeu - System: {system_prompt[:100]}... User: {user_message[:100]}...")
        
        # Detectar se é memory manager ou skill retriever
        if "Analise esta conversação" in user_message:
            # Mock response para memory processing
            logger.info("Mock: Gerando resposta de memory processing")
            return self._mock_memory_response(user_message)
        elif "Selecione até" in user_message or "skill" in user_message.lower():
            # Mock response para skill retrieval
            logger.info("Mock: Gerando resposta de skill retrieval")
            return self._mock_skill_retrieval()
        else:
            # Generic response
            logger.info("Mock: Gerando resposta genérica de chat")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]
            return await self.chat_completion_async(messages, temperature)
    
    def _mock_memory_response(self, user_message: str) -> str:
        """Gera resposta mock para memory processing."""
        # Analisar mensagem para criar memórias mock
        response = {
            "memories": {
                "hot": [],
                "cold": [],
                "archive": []
            },
            "skills": [],
            "summary": "Mock: Processamento de memória concluído"
        }
        
        # SEMPRE criar pelo menos 1 HOT e 1 COLD para testes
        response["memories"]["hot"].append({
            "key": "mock_hot_context",
            "value": f"Contexto: {user_message[:50]}...",
            "tags": ["mock", "test", "context"],
            "expires_in_days": 7
        })
        
        response["memories"]["cold"].append({
            "key": "mock_cold_preference",
            "value": "Modo mock ativo",
            "tags": ["mock", "preference", "system"]
        })
        
        # Se contém palavra "procedimento" ou "sempre", criar skill mock
        if "procedimento" in user_message.lower() or "sempre" in user_message.lower():
            response["skills"].append({
                "name": "mock_skill",
                "description": "Skill de teste mock",
                "when_to_use": "Quando em modo de teste",
                "steps": [
                    {"order": 1, "description": "Passo 1 mock", "action": "read_memory"},
                    {"order": 2, "description": "Passo 2 mock", "action": "create_note"}
                ],
                "tags": ["mock", "test"]
            })
            response["summary"] = "Mock: Criadas 1 HOT, 1 COLD e 1 skill"
        else:
            response["summary"] = "Mock: Criadas 1 HOT e 1 COLD"
        
        return json.dumps(response)
    
    def _mock_skill_retrieval(self) -> str:
        """Gera resposta mock para skill retrieval."""
        response = {
            "selected_skills": [],
            "reasoning": "Mock: Nenhuma skill selecionada em modo de teste"
        }
        return json.dumps(response)
    
    def extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrai JSON da resposta mock.
        
        Args:
            response: Resposta mock
        
        Returns:
            Dict com JSON extraído ou None
        """
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
