import os
import logging

logger = logging.getLogger(__name__)

async def create_llm_provider():
    """
    - LLM_MODE=mock -> MockLLMInterface
    - LLM_MODE=real -> Provider definido por LLM_PROVIDER (ollama)
    """
    llm_mode = os.environ.get("LLM_MODE", "mock").strip().lower()
    provider = os.environ.get("LLM_PROVIDER", "ollama").strip().lower()

    logger.info(f"LLM factory: mode={llm_mode} provider={provider}")

    if llm_mode not in ("mock", "real"):
        raise ValueError(f"LLM_MODE inválido: {llm_mode}. Use 'mock' ou 'real'.")

    if llm_mode == "mock":
        from modules.llm_interface_mock import MockLLMInterface
        return MockLLMInterface()

    # llm_mode == "real"
    if provider == "ollama":
        from modules.llm_interface_ollama import OllamaLLMInterface
        return OllamaLLMInterface()

    raise ValueError(f"LLM_PROVIDER inválido: {provider}. Use 'ollama'.")
