from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional

# Import models
from models.memory import (
    MemoryHot,
    MemoryCold,
    MemoryArchive,
    MemoryProcessRequest,
    MemoryProcessResponse,
)
from models.skill import (
    Skill,
    SkillCreateRequest,
    SkillUpdateRequest,
)
from models.approval import Approval, ApprovalRequest

# Import modules
from modules.providers.factory import create_llm_provider
from modules.memory import MemoryManager
from modules.skills import SkillManager

# Import core
from core.permission_gate import PermissionGate, PermissionLevel, ActionValidationResult


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize LLM provider (será criado na primeira request)
llm_interface = None
memory_manager = None
skill_manager = None


async def get_llm_interface():
    """Get or create LLM interface (lazy initialization)."""
    global llm_interface, memory_manager, skill_manager
    
    if llm_interface is None:
        llm_interface = await create_llm_provider()
        memory_manager = MemoryManager(db, llm_interface)
        skill_manager = SkillManager(db, llm_interface)
    
    return llm_interface

# Create the main app
app = FastAPI(title="Jarvis AI System", version="1.0.0")

# Create API router
api_router = APIRouter(prefix="/api")


# ============================================
# MEMORY ENDPOINTS
# ============================================

@api_router.post("/memory/process", response_model=MemoryProcessResponse)
async def process_memory(request: MemoryProcessRequest):
    """Processa conversação e extrai memórias."""
    try:
        await get_llm_interface()  # Ensure initialized
        response = await memory_manager.process_conversation(request)
        return response
    except Exception as e:
        logging.error(f"Erro ao processar memória: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/memory/hot", response_model=List[MemoryHot])
async def get_hot_memories(user_id: str = "default_user"):
    """Lista memórias HOT."""
    try:
        memories = await memory_manager.get_hot_memories(user_id)
        return memories
    except Exception as e:
        logging.error(f"Erro ao buscar memórias HOT: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/memory/cold", response_model=List[MemoryCold])
async def get_cold_memories(user_id: str = "default_user"):
    """Lista memórias COLD."""
    try:
        memories = await memory_manager.get_cold_memories(user_id)
        return memories
    except Exception as e:
        logging.error(f"Erro ao buscar memórias COLD: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/memory/archive", response_model=List[MemoryArchive])
async def get_archive_memories(user_id: str = "default_user"):
    """Lista memórias ARCHIVE."""
    try:
        memories = await memory_manager.get_archive_memories(user_id)
        return memories
    except Exception as e:
        logging.error(f"Erro ao buscar memórias ARCHIVE: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SKILLS ENDPOINTS
# ============================================

@api_router.post("/skills", response_model=Skill)
async def create_skill(request: SkillCreateRequest):
    """Cria nova skill."""
    try:
        skill = await skill_manager.create_skill(request)
        return skill
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Erro ao criar skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/skills", response_model=List[Skill])
async def list_skills(enabled_only: bool = True, limit: int = 50):
    """Lista skills."""
    try:
        skills = await skill_manager.list_skills(enabled_only, limit)
        return skills
    except Exception as e:
        logging.error(f"Erro ao listar skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/skills/search", response_model=List[Skill])
async def search_skills(q: str, limit: int = 5):
    """Pesquisa skills por texto."""
    try:
        skills = await skill_manager.search_skills(q, limit)
        return skills
    except Exception as e:
        logging.error(f"Erro ao pesquisar skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/skills/{skill_id}", response_model=Skill)
async def get_skill(skill_id: str):
    """Busca skill por ID."""
    skill = await skill_manager.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill não encontrada")
    return skill


@api_router.put("/skills/{skill_id}", response_model=Skill)
async def update_skill(skill_id: str, request: SkillUpdateRequest):
    """Atualiza skill (incrementa versão)."""
    try:
        skill = await skill_manager.update_skill(skill_id, request)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill não encontrada")
        return skill
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Erro ao atualizar skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/skills/{skill_id}")
async def disable_skill(skill_id: str):
    """Desativa skill."""
    success = await skill_manager.disable_skill(skill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Skill não encontrada")
    return {"message": "Skill desativada com sucesso"}


# ============================================
# CHAT ENDPOINT
# ============================================

@api_router.post("/chat")
async def chat(
    message: str,
    user_id: str = "default_user",
    permission_level: str = "EXECUTE_APPROVED",
):
    """
    Chat com IA usando skills e memórias.
    
    Args:
        message: Mensagem do utilizador
        user_id: ID do utilizador
        permission_level: READ_ONLY, DRAFT_ONLY, EXECUTE_APPROVED
    """
    try:
        # 1. Converter permission level
        perm_level = PermissionLevel(permission_level)
        
        # 2. Recuperar skills relevantes (max 2)
        relevant_skills = await skill_manager.retrieve_relevant_skills(message, limit=2)
        
        # 3. Buscar memórias relevantes
        hot_memories = await memory_manager.get_hot_memories(user_id)
        cold_memories = await memory_manager.get_cold_memories(user_id)
        
        # 4. Preparar contexto
        skills_context = "\n\n".join([
            f"Skill: {skill.name}\nDescrição: {skill.description}\nQuando usar: {skill.when_to_use}"
            for skill in relevant_skills
        ]) if relevant_skills else "Nenhuma skill relevante"
        
        memories_context = f"Memórias HOT: {len(hot_memories)} | Memórias COLD: {len(cold_memories)}"
        
        # 5. Preparar mensagem para LLM
        from core.system_prompt import SystemPromptManager
        security_prompt = SystemPromptManager.get_security_prompt()
        
        system_prompt = f"""{security_prompt}

Contexto de Skills:
{skills_context}

Contexto de Memórias:
{memories_context}

Nível de Permissão: {perm_level.value}

Lembre-se:
- Se READ_ONLY: apenas fornecer informação
- Se DRAFT_ONLY: propor ações, não executar
- Se EXECUTE_APPROVED: propor ações e aguardar aprovação
"""
        
        user_message = f"Utilizador: {message}"
        
        # 6. Chamar LLM
        response = await llm_interface.generate_with_system_prompt(
            system_prompt, user_message, temperature=0.7
        )
        
        # 7. Verificar se requer aprovação
        requires_approval = False
        proposed_action = None
        
        # Tentar extrair ação proposta
        action_data = llm_interface.extract_json_from_response(response)
        if action_data and "action" in action_data:
            action_type = action_data["action"]
            
            # Validar ação
            validation = PermissionGate.validate_action(
                action_type, perm_level, action_data.get("payload")
            )
            
            if not validation.allowed:
                return {
                    "response": response,
                    "error": validation.reason,
                    "requires_approval": False,
                }
            
            requires_approval = PermissionGate.requires_approval(action_type, perm_level)
            if requires_approval:
                proposed_action = {
                    "action_type": action_type,
                    "payload": validation.sanitized_data or action_data.get("payload"),
                }
        
        return {
            "response": response,
            "skills_used": [skill.name for skill in relevant_skills],
            "requires_approval": requires_approval,
            "proposed_action": proposed_action,
        }
    
    except Exception as e:
        logging.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# APPROVAL ENDPOINTS
# ============================================

@api_router.post("/approvals", response_model=Approval)
async def create_approval(request: ApprovalRequest):
    """Registra aprovação de ação."""
    try:
        approval = Approval(
            user_id=request.user_id,
            action_type=request.action_type,
            payload=request.payload,
            payload_hash=Approval.create_hash(request.payload),
            approved=request.approved,
        )
        
        if request.approved:
            from datetime import datetime, timezone
            approval.approved_at = datetime.now(timezone.utc)
        
        await db.approvals.insert_one(approval.model_dump())
        logging.info(f"Aprovação registrada: {approval.action_type} (aprovado: {approval.approved})")
        return approval
    except Exception as e:
        logging.error(f"Erro ao criar aprovação: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/approvals", response_model=List[Approval])
async def list_approvals(user_id: str = "default_user", limit: int = 50):
    """Lista aprovações."""
    try:
        approvals_data = await db.approvals.find(
            {"user_id": user_id}, {"_id": 0}
        ).limit(limit).to_list(limit)
        return [Approval(**approval) for approval in approvals_data]
    except Exception as e:
        logging.error(f"Erro ao listar aprovações: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEALTH CHECK
# ============================================

@api_router.get("/")
async def root():
    return {
        "message": "Jarvis AI System",
        "version": "1.0.0",
        "status": "operational",
    }


@api_router.get("/health")
async def health_check():
    """Health check do sistema."""
    try:
        # Verificar MongoDB
        await db.command("ping")
        
        return {
            "status": "healthy",
            "database": "connected",
            "llm": "ready",
        }
    except Exception as e:
        logging.error(f"Health check falhou: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@api_router.get("/debug/mode")
async def debug_mode():
    """Debug: mostra modo LLM e configurações (READ ONLY)."""
    return {
        "llm_mode": os.environ.get('LLM_MODE', 'mock'),
        "default_permission_level": "EXECUTE_APPROVED",
        "allowed_actions_count": len(__import__('core.security_config', fromlist=['ALLOWED_ACTIONS']).ALLOWED_ACTIONS),
        "blocked_actions_count": len(__import__('core.security_config', fromlist=['BLOCKED_ACTIONS']).BLOCKED_ACTIONS),
        "background_workers": "DISABLED",
        "auto_replication": "DISABLED",
        "network_egress": "RESTRICTED",
    }


# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
