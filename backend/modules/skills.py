"""Módulo de gerenciamento de skills."""
import logging
from typing import List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.skill import (
    Skill,
    SkillCreateRequest,
    SkillUpdateRequest,
)
from core.security_config import MAX_SKILLS_PER_USER, is_action_allowed
from core.system_prompt import SystemPromptManager
from modules.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class SkillManager:
    """Gerencia skills (procedimentos reutilizáveis)."""
    
    def __init__(self, db: AsyncIOMotorDatabase, llm: LLMInterface):
        self.db = db
        self.llm = llm
    
    async def create_skill(self, request: SkillCreateRequest) -> Skill:
        """Cria nova skill.
        
        Args:
            request: Dados da skill
        
        Returns:
            Skill criada
        """
        # Validar ações nos steps
        for step in request.steps:
            if not is_action_allowed(step.action):
                raise ValueError(f"Ação não permitida: {step.action}")
        
        skill = Skill(
            name=request.name,
            description=request.description,
            when_to_use=request.when_to_use,
            inputs=request.inputs,
            outputs=request.outputs,
            steps=request.steps,
            code_snippet=request.code_snippet,
            tests=request.tests,
            risks=request.risks,
            tags=request.tags,
        )
        
        await self.db.skills.insert_one(skill.model_dump())
        logger.info(f"Skill criada: {skill.name} (ID: {skill.id})")
        return skill
    
    async def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Busca skill por ID."""
        skill_data = await self.db.skills.find_one({"id": skill_id}, {"_id": 0})
        return Skill(**skill_data) if skill_data else None
    
    async def list_skills(
        self, enabled_only: bool = True, limit: int = 50
    ) -> List[Skill]:
        """Lista skills."""
        query = {"is_enabled": True} if enabled_only else {}
        skills_data = await self.db.skills.find(query, {"_id": 0}).limit(limit).to_list(limit)
        return [Skill(**skill) for skill in skills_data]
    
    async def search_skills(self, query: str, limit: int = 5) -> List[Skill]:
        """Pesquisa skills por texto.
        
        Args:
            query: Texto de pesquisa
            limit: Máximo de resultados
        
        Returns:
            Lista de skills relevantes
        """
        # Pesquisa simples por tags e nome
        skills_data = await self.db.skills.find(
            {
                "is_enabled": True,
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"tags": {"$in": [query.lower()]}},
                ]
            },
            {"_id": 0}
        ).limit(limit).to_list(limit)
        
        return [Skill(**skill) for skill in skills_data]
    
    async def retrieve_relevant_skills(
        self, user_query: str, limit: int = 2
    ) -> List[Skill]:
        """Recupera skills relevantes usando LLM.
        
        Args:
            user_query: Query do utilizador
            limit: Máximo de skills (default: 2)
        
        Returns:
            Lista de skills relevantes
        """
        # 1. Obter todas as skills ativas
        all_skills = await self.list_skills(enabled_only=True)
        
        if not all_skills:
            return []
        
        # 2. Preparar contexto para LLM
        skills_context = "\n\n".join([
            f"ID: {skill.id}\nNome: {skill.name}\nQuando usar: {skill.when_to_use}\nTags: {', '.join(skill.tags)}"
            for skill in all_skills
        ])
        
        # 3. Obter prompts
        security_prompt = SystemPromptManager.get_security_prompt()
        retriever_prompt = SystemPromptManager.get_skill_retriever_prompt()
        
        system_prompt = f"{security_prompt}\n\n{retriever_prompt}"
        user_message = f"""Pedido do utilizador: {user_query}

Skills disponíveis:
{skills_context}

Selecione até {limit} skills mais relevantes."""
        
        try:
            response = await self.llm.generate_with_system_prompt(
                system_prompt, user_message, temperature=0.3
            )
            
            # 4. Extrair JSON
            data = self.llm.extract_json_from_response(response)
            if not data or "selected_skills" not in data:
                logger.warning("LLM não retornou skills válidas")
                return []
            
            # 5. Buscar skills selecionadas
            selected_ids = [s["skill_id"] for s in data["selected_skills"][:limit]]
            selected_skills = [s for s in all_skills if s.id in selected_ids]
            
            logger.info(f"Skills recuperadas: {[s.name for s in selected_skills]}")
            return selected_skills
        
        except Exception as e:
            logger.error(f"Erro ao recuperar skills: {e}")
            return []
    
    async def update_skill(
        self, skill_id: str, request: SkillUpdateRequest
    ) -> Optional[Skill]:
        """Atualiza skill (incrementa versão)."""
        skill = await self.get_skill(skill_id)
        if not skill:
            return None
        
        # Atualizar campos
        update_data = request.model_dump(exclude_unset=True)
        
        # Validar ações se steps foram atualizados
        if "steps" in update_data:
            for step in update_data["steps"]:
                if not is_action_allowed(step["action"]):
                    raise ValueError(f"Ação não permitida: {step['action']}")
        
        # Incrementar versão
        update_data["version"] = skill.version + 1
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await self.db.skills.update_one(
            {"id": skill_id},
            {"$set": update_data}
        )
        
        logger.info(f"Skill atualizada: {skill_id} (versão {update_data['version']})")
        return await self.get_skill(skill_id)
    
    async def disable_skill(self, skill_id: str) -> bool:
        """Desativa skill."""
        result = await self.db.skills.update_one(
            {"id": skill_id},
            {"$set": {"is_enabled": False, "updated_at": datetime.now(timezone.utc)}}
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"Skill desativada: {skill_id}")
        return success
