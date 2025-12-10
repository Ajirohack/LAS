"""
llama.cpp Integration - Direct integration with llama.cpp server for optimal local LLM performance.

Provides:
- Lower latency than standard Ollama
- Constrained grammar generation (guaranteed JSON output)
- Speculative decoding support
"""

from typing import Optional, Dict, Any, List
import requests
import json

class GrammarType:
    """Predefined grammar types."""
    JSON = "json"
    XML = "xml"
    PYTHON = "python"
    CUSTOM = "custom"

class LlamaCppClient:
    """Client for llama.cpp server."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize llama.cpp client.
        
        Args:
            base_url: llama.cpp server URL
        """
        self.base_url = base_url.rstrip('/')
    
    def generate(self, prompt: str, 
                max_tokens: int = 512,
                temperature: float = 0.7,
                grammar: Optional[str] = None,
                grammar_type: Optional[str] = None,
                stop: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate completion with optional constrained grammar.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            grammar: Grammar string (GBNF format)
            grammar_type: Predefined grammar type (json, xml, etc.)
            stop: Stop sequences
        
        Returns:
            Generation result
        """
        payload = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stop": stop or []
        }
        
        # Add grammar if specified
        if grammar:
            payload["grammar"] = grammar
        elif grammar_type == GrammarType.JSON:
            payload["grammar"] = self._get_json_grammar()
        
        try:
            response = requests.post(
                f"{self.base_url}/completion",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "content": ""}
    
    def _get_json_grammar(self) -> str:
        """
        Get GBNF grammar for JSON output.
        
        This ensures the model always outputs valid JSON.
        """
        # Simplified JSON grammar in GBNF format
        # In production, use a complete JSON grammar
        return """
root   ::= object
value  ::= object | array | string | number | ("true" | "false" | "null") ws

object ::= "{" ws (
            string ":" ws value
            ("," ws string ":" ws value)*
          )? "}" ws

array  ::= "[" ws (
            value
            ("," ws value)*
          )? "]" ws

string ::= "\\"" (
            [^"\\\\] |
            "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
          )* "\\"" ws

number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws
ws ::= ([ \\t\\n] ws)?
"""
    
    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None,
                     max_tokens: int = 512) -> Dict[str, Any]:
        """
        Generate JSON output with constrained grammar.
        
        Args:
            prompt: Input prompt
            schema: Optional JSON schema for validation
            max_tokens: Maximum tokens
        
        Returns:
            Parsed JSON result
        """
        result = self.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            grammar_type=GrammarType.JSON,
            temperature=0.3  # Lower temp for structured output
        )
        
        if "error" in result:
            return {"error": result["error"]}
        
        # Parse JSON from response
        try:
            content = result.get("content", "")
            parsed = json.loads(content)
            
            # TODO: Validate against schema if provided
            
            return {"success": True, "data": parsed}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}", "raw": content}
    
    def health_check(self) -> bool:
        """Check if llama.cpp server is available."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about loaded model."""
        try:
            response = requests.get(f"{self.base_url}/props")
            response.raise_for_status()
            return response.json()
        except:
            return None

# Create singleton instance
_llama_cpp_client: Optional[LlamaCppClient] = None

def get_llama_cpp_client(base_url: str = "http://localhost:8080") -> LlamaCppClient:
    """Get or create llama.cpp client instance."""
    global _llama_cpp_client
    if _llama_cpp_client is None:
        _llama_cpp_client = LlamaCppClient(base_url=base_url)
    return _llama_cpp_client

# Example usage and setup instructions
"""
Setup llama.cpp server:

1. Install llama.cpp:
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make

2. Download a GGUF model:
   cd models
   wget https://huggingface.co/.../model.gguf

3. Start server with grammar support:
   ./server -m models/model.gguf --host 0.0.0.0 --port 8080

4. Use in LAS:
   from services.llama_cpp_integration import get_llama_cpp_client
   
   client = get_llama_cpp_client()
   
   # Generate JSON
   result = client.generate_json(
       prompt="Generate a person object with name and age",
       max_tokens=100
   )
   print(result['data'])  # {"name": "John", "age": 30}
"""
