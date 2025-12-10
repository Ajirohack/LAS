import configparser
from sources.interaction import Interaction
from sources.agents import CasualAgent, CoderAgent, FileAgent, PlannerAgent, BrowserAgent
from sources.browser import Browser, create_driver
from sources.logger import Logger
from services.llm_service import get_llm_service
from config.settings import settings
import os
import sys

logger = Logger("interaction_service.log")

class InteractionService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InteractionService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.llm_service = get_llm_service()
        self.provider = self.llm_service.get_provider()
        self.interaction = self._initialize_system()

    def _initialize_system(self):
        stealth_mode = settings.stealth_mode
        personality_folder = "jarvis" if settings.jarvis_personality else "base"
        languages = settings.languages.split(' ')
        
        # Force headless mode in Docker containers
        headless = settings.headless_browser
        if self._is_running_in_docker() and not headless:
            logger.warning("Detected Docker environment - forcing headless_browser=True")
            headless = True
        
        try:
            browser = Browser(
                create_driver(headless=headless, stealth_mode=stealth_mode, lang=languages[0]),
                anticaptcha_manual_install=stealth_mode
            )
            logger.info("Browser initialized")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            browser = None

        agents = [
            CasualAgent(
                name=settings.agent_name,
                prompt_path=f"prompts/{personality_folder}/casual_agent.txt",
                provider=self.provider, verbose=False
            ),
            CoderAgent(
                name="coder",
                prompt_path=f"prompts/{personality_folder}/coder_agent.txt",
                provider=self.provider, verbose=False
            ),
            FileAgent(
                name="File Agent",
                prompt_path=f"prompts/{personality_folder}/file_agent.txt",
                provider=self.provider, verbose=False
            ),
            BrowserAgent(
                name="Browser",
                prompt_path=f"prompts/{personality_folder}/browser_agent.txt",
                provider=self.provider, verbose=False, browser=browser
            ),
            PlannerAgent(
                name="Planner",
                prompt_path=f"prompts/{personality_folder}/planner_agent.txt",
                provider=self.provider, verbose=False, browser=browser
            )
        ]
        logger.info("Agents initialized")

        from sources.langgraph_interaction import LangGraphInteraction
        interaction = LangGraphInteraction(
            agents,
            tts_enabled=settings.speak,
            stt_enabled=settings.listen,
            recover_last_session=settings.recover_last_session,
            langs=languages
        )
        logger.info("Interaction initialized (LangGraph)")
        return interaction

    def _is_running_in_docker(self):
        if os.path.exists('/.dockerenv'):
            return True
        try:
            with open('/proc/1/cgroup', 'r') as f:
                return 'docker' in f.read()
        except:
            pass
        return False

    def get_interaction(self):
        return self.interaction

def get_interaction_service():
    return InteractionService()
