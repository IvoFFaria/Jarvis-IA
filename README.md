# 🤖 Jarvis AI System - Sistema de IA com Segurança Máxima

Sistema de IA estilo "Jarvis" com **regras de segurança invioláveis** e **controle total do utilizador**.

## 📋 Visão Geral

Este é um sistema de IA fundacional que implementa:
- **Memória estruturada** (HOT/COLD/ARCHIVE)
- **Skills reutilizáveis** com versionamento
- **Sistema de permissões** robusto
- **Segurança máxima** (fail-safe por padrão)
- **Sem execuções em background**

## 🏗️ Arquitetura

```
Frontend (React)
    ↓
Backend (FastAPI)
    ├── Permission Gate (核心 de segurança)
    ├── Memory Manager (HOT/COLD/ARCHIVE)
    ├── Skills Manager (procedimentos)
    └── LLM Interface (GPT-5.2)
    ↓
MongoDB (memórias + skills + aprovações)
```

## 🔒 Regras de Segurança (INVIOLÁVEIS)

### 1. **Sem Auto-Replicação**
- ❌ IA não pode criar cópias de si mesma
- ❌ Sem instâncias paralelas
- ❌ Sem agentes filhos

### 2. **Sem Comunicação Externa**
- ❌ Sem chamadas de rede não autorizadas
- ❌ Network egress desativado por padrão

### 3. **Sem Execução de Sistema**
- ❌ Sem comandos OS
- ❌ Sem acesso a credenciais
- ❌ Sem instalação de software

### 4. **Sem Automações Background**
- ❌ Sem loops, schedulers, timers
- ❌ Sem cron jobs ou workers
- ✅ Apenas ações sob demanda

### 5. **Controle do Utilizador**
- ✅ Apenas ações sob ordem direta
- ✅ Sempre aguarda aprovação explícita
- ✅ Fail-safe: bloqueia por padrão

## 🧠 Sistema de Memória

### **HOT Memory** (Curto Prazo)
- TTL: 7 dias (renova se usada)
- Preferências temporárias
- Contexto de conversa atual
- Expiry inline (sem background)

### **COLD Memory** (Longo Prazo)
- Permanente
- Preferências estáveis
- Factos sobre o utilizador
- Workflows estabelecidos

### **ARCHIVE Memory** (Histórico)
- Informações substituídas
- Contexto histórico
- Preferências antigas

## 🛠️ Sistema de Skills

Skills são **procedimentos reutilizáveis** criados automaticamente quando a IA detecta padrões repetíveis.

**Estrutura:**
```json
{
  "name": "daily_task_summary",
  "description": "Cria sumário diário de tarefas",
  "when_to_use": "Fim do dia ou quando pedido",
  "steps": [
    {"order": 1, "action": "read_tasks"},
    {"order": 2, "action": "create_note"}
  ],
  "version": 1
}
```

## 🔑 Níveis de Permissão

### **READ_ONLY** 🔒
- Apenas leitura de dados
- Sem modificações

### **DRAFT_ONLY** 📋
- Gera planos e propostas
- **NÃO executa** nada

### **EXECUTE_APPROVED** ✅
- Propõe ações
- Aguarda aprovação explícita
- Executa se aprovado

## 🚀 Endpoints da API

### **Memória**
```bash
# Processar conversação → HOT/COLD/ARCHIVE
POST /api/memory/process

# Listar memórias
GET /api/memory/hot?user_id=default_user
GET /api/memory/cold?user_id=default_user
GET /api/memory/archive?user_id=default_user
```

### **Skills**
```bash
# Criar skill
POST /api/skills

# Listar skills
GET /api/skills?enabled_only=true&limit=10

# Pesquisar skills
GET /api/skills/search?q=summary

# Atualizar skill (incrementa versão)
PUT /api/skills/{skill_id}

# Desativar skill
DELETE /api/skills/{skill_id}
```

### **Chat**
```bash
# Chat com IA
POST /api/chat?message=ola&user_id=default_user&permission_level=EXECUTE_APPROVED
```

### **Aprovações**
```bash
# Registar aprovação
POST /api/approvals

# Listar aprovações
GET /api/approvals?user_id=default_user
```

### **Health Check**
```bash
GET /api/health
```

## 🧪 Modo Mock (Testes Sem Saldo)

O sistema suporta **modo mock** para testes sem necessidade de saldo LLM.

### Configurar Modo

Editar `/app/backend/.env`:
```bash
LLM_MODE="mock"  # Testes (gratuito)
# OU
LLM_MODE="real"  # Produção (GPT-5.2)
```

Reiniciar:
```bash
sudo supervisorctl restart backend
```

### Verificar Modo Atual
```bash
curl http://localhost:8001/api/debug/mode
```

### Executar Testes
```bash
cd /app/backend
python3 -m pytest tests/ -v
```

**Veja [TESTING.md](TESTING.md) para detalhes completos.**

---

## 🔧 Tecnologias

- **Frontend:** React 19, TailwindCSS, Axios
- **Backend:** FastAPI, Python 3.11
- **Database:** MongoDB
- **LLM:** GPT-5.2 via Emergent Universal Key
- **Library:** emergentintegrations

## 📦 Estrutura de Ficheiros

```
/app/
├── backend/
│   ├── core/                  # Segurança + Permissões
│   │   ├── security_config.py
│   │   ├── permission_gate.py
│   │   └── system_prompt.py
│   ├── models/                # Pydantic models
│   │   ├── memory.py
│   │   ├── skill.py
│   │   └── approval.py
│   ├── modules/               # Lógica de negócio
│   │   ├── llm_interface.py
│   │   ├── memory.py
│   │   └── skills.py
│   ├── prompts/               # System prompts
│   │   ├── system_prompt_security.txt
│   │   ├── memory_manager_prompt.txt
│   │   └── skill_retriever_prompt.txt
│   ├── server.py
│   ├── requirements.txt
│   └── .env
└── frontend/
    └── src/
        ├── pages/
        │   ├── Dashboard.js
        │   └── Chat.js
        ├── components/
        │   ├── MemoryViewer.js
        │   ├── SkillCard.js
        │   └── ApprovalDialog.js
        ├── App.js
        └── App.css
```

## 🔐 Variáveis de Ambiente

### Backend (`/app/backend/.env`)
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="jarvis_db"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY="sk-emergent-XXX"
```

### Frontend (`/app/frontend/.env`)
```bash
REACT_APP_BACKEND_URL=https://your-domain.com
```

## 🧪 Testes

### Testar Backend
```bash
# Health check
curl http://localhost:8001/api/health

# Listar memórias HOT
curl "http://localhost:8001/api/memory/hot?user_id=default_user"

# Listar skills
curl "http://localhost:8001/api/skills?enabled_only=true"
```

### Testar Chat
```bash
curl -X POST "http://localhost:8001/api/chat" \
  -d "message=Olá" \
  -d "user_id=default_user" \
  -d "permission_level=EXECUTE_APPROVED"
```

## 🎯 Próximos Passos (NÃO IMPLEMENTADOS)

- ❌ Automações
- ❌ Background workers
- ❌ Integrações externas
- ❌ Monetização
- ❌ Multi-user authentication

## ⚠️ Limitações Importantes

1. **Single-user** por enquanto
2. **Sem execução de código** arbitrário
3. **Sem acesso a sistema operativo**
4. **Sem network egress** não autorizado
5. **Apenas ações allowlisted**

## 📝 Ações Permitidas

```python
ALLOWED_ACTIONS = [
    "read_memory",
    "write_memory",
    "search_memory",
    "create_skill",
    "update_skill",
    "search_skills",
    "create_note",
    "read_notes",
    "update_note",
    "delete_note",
    "create_task",
    "read_tasks",
    "update_task",
    "complete_task",
    "search_database",
    "query_database",
]
```

**QUALQUER AÇÃO FORA DESTA LISTA É BLOQUEADA.**

## 🛡️ Validação de PII

Antes de persistir em memórias, o sistema mascara:
- ✅ Emails → `[EMAIL_REDACTED]`
- ✅ Telefones → `[PHONE_REDACTED]`
- ✅ Cartões → `[CARD_REDACTED]`
- ✅ Passwords → `[PASSWORD_REDACTED]`
- ✅ Tokens/Keys → `[TOKEN_REDACTED]`

**Nota:** Emails são permitidos no chat e em `users.email`, mas mascarados nas memórias.

## 📖 Como Usar

### 1. **Aceder ao Dashboard**
```
https://your-domain.com/
```
Visualize estatísticas de memórias e skills ativas.

### 2. **Usar o Chat**
```
https://your-domain.com/chat
```
- Escolha nível de permissão
- Converse com Jarvis
- Aprove ações quando solicitado

### 3. **Processar Memórias**
O sistema processa memórias automaticamente durante conversas, mas pode ser chamado manualmente:
```bash
curl -X POST "http://localhost:8001/api/memory/process" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "default_user",
    "conversation_chunk": "Eu trabalho das 9h às 18h todos os dias."
  }'
```

## 🚦 Status do Sistema

✅ **Fundação Implementada**
✅ **Segurança Máxima**
✅ **Memória HOT/COLD/ARCHIVE**
✅ **Skills com Versionamento**
✅ **Sistema de Permissões**
✅ **Dashboard + Chat**
✅ **LLM Integration (GPT-5.2)**

---

## 📧 Suporte

Para questões ou problemas, consulte os logs:
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Frontend
tail -f /var/log/supervisor/frontend.err.log
```

---

**🔒 Este sistema foi projetado com segurança em primeiro lugar. Todas as regras são invioláveis e não podem ser desativadas.**
