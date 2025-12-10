"""
HuggingFace Provider - HuggingFace Inference API implementation.
"""

from typing import List, Dict, Iterator, Union
from sources.providers.base_provider import BaseProvider, ProviderConfig

class HuggingFaceProvider(BaseProvider):
    """HuggingFace Inference API provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not self.api_key:
            import os
            self.api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "huggingface"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """Generate chat completion using HuggingFace service."""
        from services.huggingface_service import get_huggingface_service
        
        hf_service = get_huggingface_service()
        
        if stream:
            return hf_service.chat_completion_stream(
                model=self.model,
                messages=messages,
                **kwargs
            )
        else:
            return hf_service.chat_completion(
                model=self.model,
                messages=messages,
                **kwargs
            )
    
    def get_langchain_llm(self):
        """Get LangChain LLM for HuggingFace."""
        from langchain_community.llms import HuggingFaceHub
        
        return HuggingFaceHub(
            repo_id=self.model,
            huggingfacehub_api_token=self.api_key
        )
    
    def list_models(self) -> List[str]:
        """List popular HuggingFace models."""
        return [
            "meta-llama/Llama-3.3-70B-Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "google/gemma-2-9b-it",
            "Qwen/Qwen2.5-72B-Instruct",
        ]
    
    def supports_streaming(self) -> bool:
        return True
