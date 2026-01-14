"""Módulo de gerenciamento de memória."""
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.memory import (
    MemoryHot,
    MemoryCold,
    MemoryArchive,
    MemoryProcessRequest,
    MemoryProcessResponse,
)
from models.skill import Skill, SkillStep, SkillInput, SkillOutput
from core.system_prompt import SystemPromptManager
from core.security_config import HOT_MEMORY_TTL_DAYS
from modules.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class MemoryManager:
    """Gerencia memórias HOT, COLD e ARCHIVE."""
    
    def __init__(self, db: AsyncIOMotorDatabase, llm: LLMInterface):
        self.db = db
        self.llm = llm
    
    async def process_conversation(
        self, request: MemoryProcessRequest
    ) -> MemoryProcessResponse:
        """Processa conversação e extrai memórias.
        
        Args:
            request: Request com conversação
        
        Returns:
            Response com memórias criadas
        """
        # 1. Cleanup inline de memórias expiradas
        await self._cleanup_expired_hot_memories(request.user_id)
        
        # 2. Obter prompts
        security_prompt = SystemPromptManager.get_security_prompt()
        memory_prompt = SystemPromptManager.get_memory_manager_prompt()
        
        # 3. Chamar LLM
        system_prompt = f"{security_prompt}\n\n{memory_prompt}"
        user_message = f"""Analise esta conversação e extraia informações relevantes:

{request.conversation_chunk}

Retorne JSON com memories (hot/cold/archive) e skills."""
        
        try:
            response = self.llm.generate_with_system_prompt(
                system_prompt, user_message, temperature=0.3
            )
            
            # 4. Extrair JSON
            data = self.llm.extract_json_from_response(response)
            if not data:
                logger.warning("Não foi possível extrair JSON da resposta do LLM")
                return MemoryProcessResponse(summary="Nenhuma memória extraída")
            
            # 5. Persistir memórias
            hot_created = await self._persist_hot_memories(
                request.user_id, data.get("memories", {}).get("hot", [])
            )
            
            cold_created = await self._persist_cold_memories(
                request.user_id, data.get("memories", {}).get("cold", [])
            )
            
            archived = await self._persist_archive_memories(
                request.user_id, data.get("memories", {}).get("archive", [])
            )
            
            # 6. Criar skills se aplicável
            skills_created = await self._create_skills_from_data(
                data.get("skills", [])
            )
            
            return MemoryProcessResponse(
                hot_created=hot_created,
                cold_created=cold_created,
                archived=archived,
                skills_created=skills_created,
                summary=data.get("summary", "Processamento concluído"),
            )
        
        except Exception as e:
            logger.error(f"Erro ao processar conversação: {e}")
            return MemoryProcessResponse(summary=f"Erro: {str(e)}")
    
    async def _cleanup_expired_hot_memories(self, user_id: str):
        """Limpa memórias HOT expiradas (inline, sem background)."""
        now = datetime.now(timezone.utc)
        
        # Buscar expiradas
        expired = await self.db.memory_hot.find({
            "user_id": user_id,
            "expires_at": {"$lt": now}
        }).to_list(None)
        
        # Arquivar
        for mem in expired:
            archive = MemoryArchive(
                user_id=user_id,
                key=mem["key"],
                value=mem["value"],
                tags=mem.get("tags", []),
                archived_reason="Expirou (HOT memory TTL)",
                created_at=mem["created_at"],
            )
            await self.db.memory_archive.insert_one(archive.model_dump())
        
        # Remover
        if expired:
            await self.db.memory_hot.delete_many({
                "user_id": user_id,
                "expires_at": {"$lt": now}
            })
            logger.info(f"Arquivadas {len(expired)} memórias HOT expiradas")
    
    async def _persist_hot_memories(
        self, user_id: str, memories: List[Dict[str, Any]]
    ) -> List[MemoryHot]:
        """Persiste memórias HOT."""
        created = []
        
        for mem_data in memories:
            expires_at = datetime.now(timezone.utc) + timedelta(
                days=mem_data.get("expires_in_days", HOT_MEMORY_TTL_DAYS)
            )
            
            memory = MemoryHot(
                user_id=user_id,
                key=mem_data["key"],
                value=mem_data["value"],
                tags=mem_data.get("tags", []),
                expires_at=expires_at,
            )
            
            await self.db.memory_hot.insert_one(memory.model_dump())
            created.append(memory)
            logger.info(f"Memória HOT criada: {memory.key}")
        
        return created
    
    async def _persist_cold_memories(
        self, user_id: str, memories: List[Dict[str, Any]]
    ) -> List[MemoryCold]:
        """Persiste memórias COLD."""
        created = []
        
        for mem_data in memories:
            memory = MemoryCold(
                user_id=user_id,
                key=mem_data["key"],
                value=mem_data["value"],
                tags=mem_data.get("tags", []),
            )
            
            await self.db.memory_cold.insert_one(memory.model_dump())
            created.append(memory)
            logger.info(f"Memória COLD criada: {memory.key}")
        
        return created
    
    async def _persist_archive_memories(
        self, user_id: str, memories: List[Dict[str, Any]]
    ) -> List[MemoryArchive]:
        """Persiste memórias ARCHIVE."""
        created = []
        
        for mem_data in memories:
            memory = MemoryArchive(
                user_id=user_id,
                key=mem_data["key"],
                value=mem_data["value"],
                tags=mem_data.get("tags", []),
                archived_reason=mem_data.get("reason", "Arquivado automaticamente"),
                created_at=datetime.now(timezone.utc),
            )
            
            await self.db.memory_archive.insert_one(memory.model_dump())
            created.append(memory)
            logger.info(f"Memória ARCHIVE criada: {memory.key}")
        
        return created
    
    async def _create_skills_from_data(self, skills_data: List[Dict[str, Any]]) -> List[str]:
        """Cria skills a partir dos dados do LLM."""
        created_ids = []
        
        for skill_data in skills_data:
            try:
                # Converter steps
                steps = [
                    SkillStep(**step) for step in skill_data.get("steps", [])
                ]
                
                # Converter inputs/outputs se existirem
                inputs = [
                    SkillInput(**inp) for inp in skill_data.get("inputs", [])
                ]
                outputs = [
                    SkillOutput(**out) for out in skill_data.get("outputs", [])
                ]
                
                skill = Skill(
                    name=skill_data["name"],
                    description=skill_data["description"],
                    when_to_use=skill_data["when_to_use"],
                    inputs=inputs,
                    outputs=outputs,
                    steps=steps,
                    tags=skill_data.get("tags", []),
                )
                
                await self.db.skills.insert_one(skill.model_dump())
                created_ids.append(skill.id)
                logger.info(f"Skill criada: {skill.name}")
            
            except Exception as e:
                logger.error(f"Erro ao criar skill: {e}")
                continue
        
        return created_ids
    
    async def get_hot_memories(self, user_id: str) -> List[MemoryHot]:
        """Retorna memórias HOT do utilizador."""
        # Cleanup inline
        await self._cleanup_expired_hot_memories(user_id)
        
        memories = await self.db.memory_hot.find(
            {"user_id": user_id}, {"_id": 0}
        ).to_list(None)
        
        return [MemoryHot(**mem) for mem in memories]
    
    async def get_cold_memories(self, user_id: str) -> List[MemoryCold]:
        """Retorna memórias COLD do utilizador."""
        memories = await self.db.memory_cold.find(
            {"user_id": user_id}, {"_id": 0}
        ).to_list(None)
        
        return [MemoryCold(**mem) for mem in memories]
    
    async def get_archive_memories(self, user_id: str) -> List[MemoryArchive]:
        """Retorna memórias ARCHIVE do utilizador."""
        memories = await self.db.memory_archive.find(
            {"user_id": user_id}, {"_id": 0}
        ).to_list(None)
        
        return [MemoryArchive(**mem) for mem in memories]
