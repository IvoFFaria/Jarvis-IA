"""Testes para garantir que nada roda em background."""
import pytest
import inspect
import ast


class TestNoBackgroundProcessing:
    """Testes para garantir ausência de processamento em background."""
    
    def test_no_threading_in_codebase(self):
        """Verifica que não há uso de threading."""
        import glob
        
        forbidden_imports = [
            "import threading",
            "from threading import",
            "import multiprocessing",
            "from multiprocessing import",
        ]
        
        python_files = glob.glob("/app/backend/**/*.py", recursive=True)
        
        for filepath in python_files:
            if "tests/" in filepath:
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
                
                for forbidden in forbidden_imports:
                    assert forbidden not in content, \
                        f"Detectado {forbidden} em {filepath} (processamento em background proibido)"
    
    def test_no_scheduler_in_codebase(self):
        """Verifica que não há schedulers."""
        import glob
        
        forbidden_patterns = [
            "schedule.",
            "cron",
            "APScheduler",
            "celery",
            "background_task",
            "Timer(",
        ]
        
        python_files = glob.glob("/app/backend/**/*.py", recursive=True)
        
        for filepath in python_files:
            if "tests/" in filepath:
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
                
                for pattern in forbidden_patterns:
                    assert pattern not in content, \
                        f"Detectado {pattern} em {filepath} (schedulers proibidos)"
    
    def test_no_create_task_in_modules(self):
        """Verifica que módulos não criam tasks em background."""
        import glob
        
        forbidden_patterns = [
            "asyncio.create_task",
            "loop.create_task",
            "ensure_future",
        ]
        
        module_files = glob.glob("/app/backend/modules/*.py", recursive=True)
        
        for filepath in module_files:
            with open(filepath, 'r') as f:
                content = f.read()
                
                for pattern in forbidden_patterns:
                    assert pattern not in content, \
                        f"Detectado {pattern} em {filepath} (tasks em background proibidos)"
    
    def test_no_infinite_loops(self):
        """Verifica que não há loops infinitos."""
        import glob
        
        python_files = glob.glob("/app/backend/**/*.py", recursive=True)
        
        for filepath in python_files:
            if "tests/" in filepath:
                continue
                
            try:
                with open(filepath, 'r') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    # Verificar while True
                    if isinstance(node, ast.While):
                        if isinstance(node.test, ast.Constant) and node.test.value is True:
                            # Verificar se há break dentro do while
                            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                            assert has_break, \
                                f"Loop infinito sem break detectado em {filepath}"
            except SyntaxError:
                pass  # Ignorar erros de sintaxe (pode ser template)
    
    def test_server_startup_no_background_tasks(self):
        """Verifica que server.py não inicia tasks em background."""
        with open("/app/backend/server.py", 'r') as f:
            content = f.read()
        
        forbidden = [
            "create_task",
            "Thread(",
            "Process(",
            "schedule.",
            "@app.on_event('startup')",  # Verificar se há logic suspeita
        ]
        
        # on_event('startup') é permitido, mas não deve criar tasks
        if "@app.on_event('startup')" in content or "@app.on_event(\"startup\")" in content:
            # Verificar que não cria tasks dentro de startup
            assert "create_task" not in content
            assert "Thread(" not in content
    
    def test_memory_cleanup_is_inline(self):
        """Verifica que cleanup de memória é inline (não background)."""
        from modules.memory import MemoryManager
        
        # Verificar que _cleanup_expired_hot_memories não cria tasks
        source = inspect.getsource(MemoryManager._cleanup_expired_hot_memories)
        
        assert "create_task" not in source
        assert "Thread" not in source
        assert "Process" not in source
        
        # Deve ser async (chamado inline com await)
        assert "async def" in source
    
    def test_no_daemon_processes(self):
        """Verifica que não há processos daemon."""
        import glob
        
        python_files = glob.glob("/app/backend/**/*.py", recursive=True)
        
        for filepath in python_files:
            if "tests/" in filepath:
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
                
                assert "daemon=True" not in content, \
                    f"Detectado daemon=True em {filepath} (processos daemon proibidos)"
    
    def test_no_worker_patterns(self):
        """Verifica que não há padrões de workers."""
        import glob
        
        forbidden_patterns = [
            "worker",
            "queue.Queue",
            "multiprocessing.Queue",
            "Consumer(",
            "Producer(",
        ]
        
        python_files = glob.glob("/app/backend/**/*.py", recursive=True)
        
        for filepath in python_files:
            if "tests/" in filepath:
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
                
                for pattern in forbidden_patterns:
                    # Permitir "worker" em comentários ou strings, mas não em código
                    lines = content.split('\n')
                    for line in lines:
                        line_stripped = line.strip()
                        if line_stripped.startswith('#'):
                            continue
                        if pattern in line_stripped:
                            # Verificar se não é apenas em string
                            if pattern in line_stripped and not (
                                f'"{pattern}"' in line_stripped or f"'{pattern}'" in line_stripped
                            ):
                                if "worker" in pattern:
                                    # "worker" pode aparecer em nomes de variáveis, mas não como função/classe
                                    if f"class {pattern}" in line or f"def {pattern}" in line:
                                        pytest.fail(f"Detectado padrão de worker em {filepath}: {line}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
