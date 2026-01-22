"""Gerenciador de System Prompts."""
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class SystemPromptManager:
    """Gerencia carregamento de prompts do sistema."""
    
    _cache: Dict[str, str] = {}
    
    @classmethod
    def load_prompt(cls, prompt_name: str) -> str:
        """Carrega prompt do disco (com cache).
        
        Args:
            prompt_name: Nome do prompt (sem .txt)
        
        Returns:
            Conteúdo do prompt
        """
        if prompt_name in cls._cache:
            return cls._cache[prompt_name]
        
        prompt_path = PROMPTS_DIR / f"{prompt_name}.txt"
        
        if not prompt_path.exists():
            logger.error(f"Prompt não encontrado: {prompt_path}")
            return ""
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read()
                cls._cache[prompt_name] = content
                logger.info(f"Prompt carregado: {prompt_name}")
                return content
        except Exception as e:
            logger.error(f"Erro ao carregar prompt {prompt_name}: {e}")
            return ""
    
    @classmethod
    def get_security_prompt(cls) -> str:
        """Retorna o prompt de segurança (imutável)."""
        return cls.load_prompt("system_prompt_security")
    
    @classmethod
    def get_memory_manager_prompt(cls) -> str:
        """Retorna o prompt do memory manager."""
        return cls.load_prompt("memory_manager_prompt")
    
    @classmethod
    def get_skill_retriever_prompt(cls) -> str:
        """Retorna o prompt do skill retriever."""
        return cls.load_prompt("skill_retriever_prompt")
