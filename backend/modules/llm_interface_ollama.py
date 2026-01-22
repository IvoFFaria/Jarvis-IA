import os
import json
import re
import httpx


class OllamaLLMInterface:
    def __init__(self):
        self.base_url = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.environ.get("OLLAMA_MODEL", "llama3.1:latest")

    async def generate_with_system_prompt(self, system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }

        timeout = httpx.Timeout(connect=10.0, read=300.0, write=300.0, pool=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:

            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()

        return (data.get("message") or {}).get("content", "")

    def extract_json_from_response(self, text: str):
        """
        Extrai o primeiro bloco JSON válido encontrado no texto.
        Aceita JSON puro ou JSON dentro de ``` ``` / texto misto.
        """
        if not text:
            return None

        # 1) tentar direto
        try:
            return json.loads(text)
        except Exception:
            pass

        # 2) procurar bloco ```json ... ```
        codeblock = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if codeblock:
            candidate = codeblock.group(1)
            try:
                return json.loads(candidate)
            except Exception:
                pass

        # 3) procurar primeiro {...} grande
        brace = re.search(r"(\{.*\})", text, re.DOTALL)
        if brace:
            candidate = brace.group(1)
            try:
                return json.loads(candidate)
            except Exception:
                return None

        return None

