"""Factory para criar provider correto baseado em env."""
import os
import logging
from .mock import MockProvider
from .ollama import OllamaProvider
from .emergent import EmergentProvider

logger = logging.getLogger(__name__)


async def create_llm_provider():
    """Cria provider baseado em LLM_MODE e LLM_PROVIDER.
    
    Returns:
        Provider configurado (com fallback para mock se necessário)
    """
    llm_mode = os.environ.get('LLM_MODE', 'mock')
    llm_provider = os.environ.get('LLM_PROVIDER', 'ollama')
    
    logger.info(f"🔧 LLM_MODE={llm_mode}, LLM_PROVIDER={llm_provider}")
    
    # Modo mock sempre retorna MockProvider
    if llm_mode == 'mock':
        logger.info("✅ Usando MockProvider (modo de testes)")
        return MockProvider()
    
    # Modo real: escolher provider
    if llm_mode == 'real':
        if llm_provider == 'ollama':
            provider = OllamaProvider()
            # Verificar se Ollama está disponível
            if await provider.check_availability():
                logger.info("✅ Usando OllamaProvider (local, gratuito)")
                return provider
            else:
                logger.warning("⚠️ Ollama indisponível. Fallback para MockProvider")
                logger.warning("💡 Instale Ollama: curl -fsSL https://ollama.com/install.sh | sh")
                return MockProvider()
        
        elif llm_provider == 'emergent':
            logger.info("✅ Usando EmergentProvider (placeholder)")
            return EmergentProvider()
        
        elif llm_provider in ['openai', 'gemini', 'anthropic']:
            logger.warning(f"⚠️ {llm_provider} ainda não implementado. Fallback para MockProvider")
            return MockProvider()
        
        else:
            logger.warning(f"⚠️ Provider desconhecido: {llm_provider}. Fallback para MockProvider")
            return MockProvider()
    
    # Fallback final
    logger.warning("⚠️ Configuração inválida. Fallback para MockProvider")
    return MockProvider()
