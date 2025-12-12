from config.settings import settings
from sources.logger import Logger

logger = Logger("llm_service.log")

class LLMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialized = False
            cls._instance.initialize()  # Call initialize immediately
        return cls._instance

    def initialize(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            self.provider = None
            self._initialized = True
            logger.info("LLM Service initialized (lazy provider)")

    def get_provider(self):
        if self.provider is None:
            try:
                from sources.llm_provider import Provider
                self.provider = Provider(
                    provider_name=settings.provider_name,
                    model=settings.provider_model,
                    server_address=settings.provider_server_address,
                    is_local=settings.is_local
                )
                logger.info(f"LLM Provider created: {self.provider.provider_name}")
            except Exception as e:
                logger.error(f"Failed to create provider: {e}")
                class _NullProvider:
                    def list_models(self, *_args, **_kwargs):
                        return []
                    def get_langchain_llm(self):
                        return None
                self.provider = _NullProvider()
        return self.provider

    def get_available_models(self, provider_name: str = None):
        if self.provider is None:
            self.get_provider()
        return self.provider.list_models(provider_name)

    def get_langchain_llm(self):
        if self.provider is None:
            self.get_provider()
        return self.provider.get_langchain_llm()

def get_llm_service():
    return LLMService()
