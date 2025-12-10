"""
Sandbox Executor - Execute code in isolated containers for security.
"""

import subprocess
import tempfile
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum

class SandboxType(str, Enum):
    """Sandbox implementation types."""
    DOCKER = "docker"
    PROCESS = "process"  # Basic subprocess isolation

class SandboxExecutor:
    """
    Execute code in sandboxed environments.
    
    For production: Use Docker, Firecracker, or gVisor.
    Current: Basic subprocess with restrictions.
    """
    
    def __init__(self, sandbox_type: SandboxType = SandboxType.PROCESS):
        self.sandbox_type = sandbox_type
        self.allowed_networks: List[str] = []  # Allowlist
        self.blocked_networks: List[str] = []   # Blocklist
    
    def execute_code(self, code: str, language: str = "python",
                    timeout: int = 30,
                    max_memory_mb: int = 512,
                    allow_network: bool = False) -> Dict[str, Any]:
        """
        Execute code in sandbox.
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout in seconds
            max_memory_mb: Memory limit
            allow_network: Allow network access
        
        Returns:
            Execution result
        """
        if self.sandbox_type == SandboxType.DOCKER:
            return self._execute_docker(code, language, timeout, max_memory_mb, allow_network)
        else:
            return self._execute_process(code, language, timeout)
    
    def _execute_process(self, code: str, language: str, timeout: int) -> Dict[str, Any]:
        """Execute in subprocess (basic isolation)."""
        if language != "python":
            return {"error": "Only Python supported in process mode"}
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute with timeout
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        
        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out", "success": False}
        
        except Exception as e:
            return {"error": str(e), "success": False}
        
        finally:
            # Cleanup
            Path(temp_file).unlink(missing_ok=True)
    
    def _execute_docker(self, code: str, language: str, timeout: int,
                       max_memory_mb: int, allow_network: bool) -> Dict[str, Any]:
        """Execute in Docker container (production isolation)."""
        # Docker command template
        docker_image = f"{language}:latest"
        
        # Network mode
        network_mode = "none" if not allow_network else "bridge"
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Docker run command
            cmd = [
                'docker', 'run',
                '--rm',
                f'--memory={max_memory_mb}m',
                f'--network={network_mode}',
                '--cpus=1',
                f'--timeout={timeout}',
                '-v', f'{temp_file}:/code/script.{language}',
                docker_image,
                language, f'/code/script.{language}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5  # Extra buffer
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0,
                "sandbox": "docker"
            }
        
        except Exception as e:
            return {"error": str(e), "success": False}
        
        finally:
            Path(temp_file).unlink(missing_ok=True)

# Create singleton instance
_sandbox_executor: Optional[SandboxExecutor] = None

def get_sandbox_executor(sandbox_type: SandboxType = SandboxType.PROCESS) -> SandboxExecutor:
    """Get or create SandboxExecutor instance."""
    global _sandbox_executor
    if _sandbox_executor is None:
        _sandbox_executor = SandboxExecutor(sandbox_type=sandbox_type)
    return _sandbox_executor

# Example Docker setup
"""
# Dockerfile for sandboxed Python execution
FROM python:3.11-slim

RUN useradd -m -u 1000 sandbox
USER sandbox
WORKDIR /code

# No network, limited resources
CMD ["python3"]
"""
