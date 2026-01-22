import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class MockLLMInterface:
    """LLM mock para testes locais sem chamadas externas."""

    def __init__(self):
        logger.info("MockLLMInterface inicializada (sem rede).")

    async def chat_completion_async(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        last_user = ""
        for m in messages[::-1]:
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break
        # resposta previsível
        return f"MOCK: Recebido -> {last_user}"

    async def generate_with_system_prompt(self, system_prompt: str, user_message: str, temperature: float = 0.7) -> str:
        return await self.chat_completion_async(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            temperature=temperature,
        )

    def extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        return None
