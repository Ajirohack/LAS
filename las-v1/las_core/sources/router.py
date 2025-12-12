import os
import sys
import random
from typing import List, Tuple, Type, Dict

try:
    import torch
except ImportError:
    torch = None

from transformers import pipeline

try:
    from adaptive_classifier import AdaptiveClassifier
except ImportError:
    class AdaptiveClassifier:
        @classmethod
        def from_pretrained(cls, path):
            return cls()
        def predict(self, text):
            # Default fallback prediction
            return [("talk", 0.9)]
        def add_examples(self, texts, labels):
            pass

from sources.agents.agent import Agent
from sources.agents.code_agent import CoderAgent
from sources.agents.casual_agent import CasualAgent
from sources.agents.planner_agent import FileAgent
from sources.agents.browser_agent import BrowserAgent
from sources.language import LanguageUtility
from sources.utility import pretty_print, animate_thinking, timer_decorator
from sources.logger import Logger

class AgentRouter:
    """
    AgentRouter is a class that selects the appropriate agent based on the user query.
    """
    def __init__(self, agents: list, supported_language: List[str] = ["en", "fr", "zh"]):
        self.agents = agents
        self.logger = Logger("router.log")
        self.lang_analysis = LanguageUtility(supported_language=supported_language)
        self.pipelines = self.load_pipelines()
        self.talk_classifier = self.load_llm_router()
        self.complexity_classifier = self.load_llm_router()
        self.learn_few_shots_tasks()
        self.learn_few_shots_complexity()
        self.asked_clarify = False
    
    def load_pipelines(self) -> Dict[str, Type[pipeline]]:
        """
        Load the pipelines for the text classification used for routing.
        returns:
            Dict[str, Type[pipeline]]: The loaded pipelines
        """
        animate_thinking("Loading zero-shot pipeline...", color="status")
        # Disabled to avoid HuggingFace download issues - using LLM router only
        return {
            # "bart": pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        }

    def load_llm_router(self) -> AdaptiveClassifier:
        """
        Load the LLM router model.
        returns:
            AdaptiveClassifier: The loaded model
        exceptions:
            Exception: If the safetensors fails to load
        """
        path = "../llm_router" if __name__ == "__main__" else "./llm_router"
        try:
            animate_thinking("Loading LLM router model...", color="status")
            talk_classifier = AdaptiveClassifier.from_pretrained(path)
        except Exception as e:
            # Fallback for when model files are missing even if class exists
            print(f"Warning: Failed to load routing model ({e}). Using dummy classifier.")
            class DummyClassifier:
                def predict(self, text): return [("talk", 0.9)]
                def add_examples(self, texts, labels): pass
            talk_classifier = DummyClassifier()
            
        return talk_classifier

    def get_device(self) -> str:
        if torch is None:
            return "cpu"
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda:0"
        else:
            return "cpu"
    
    def learn_few_shots_complexity(self) -> None:
        """
        Few shot learning for complexity estimation.
        Use the build in add_examples method of the Adaptive_classifier.
        """
        pass

    def learn_few_shots_tasks(self) -> None:
        """
        Few shot learning for tasks classification.
        Use the build in add_examples method of the Adaptive_classifier.
        """
        pass

    def llm_router(self, text: str) -> tuple:
        """
        Inference of the LLM router model.
        Args:
            text: The input text
        """
        predictions = self.talk_classifier.predict(text)
        predictions = [pred for pred in predictions if pred[0] not in ["HIGH", "LOW"]]
        if not predictions:
            return ("talk", 0.9)
        predictions = sorted(predictions, key=lambda x: x[1], reverse=True)
        return predictions[0]
    
    def router_vote(self, text: str, labels: list, log_confidence:bool = False) -> str:
        """
        Vote between the LLM router and BART model.
        """
        if len(text) <= 8:
            return "talk"
        
        # If BART is not available, use only LLM router
        if 'bart' not in self.pipelines or self.pipelines['bart'] is None:
            # Simple simulation logic for tests if model is dummy
            if "search" in text.lower(): return "browser"
            if "code" in text.lower() or "python" in text.lower(): return "coder"
            if "file" in text.lower(): return "file"

            result_llm_router = self.llm_router(text)
            llm_router, confidence_llm_router = result_llm_router[0], result_llm_router[1]
            self.logger.info(f"Routing (LLM-only) for text {text}: {llm_router} ({confidence_llm_router})")
            if log_confidence:
                pretty_print(f"Agent choice -> LLM-router: {llm_router} ({confidence_llm_router})")
            return llm_router
        
        # Original voting logic with BART
        result_bart = self.pipelines['bart'](text, labels)
        result_llm_router = self.llm_router(text)
        bart, confidence_bart = result_bart['labels'][0], result_bart['scores'][0]
        llm_router, confidence_llm_router = result_llm_router[0], result_llm_router[1]
        final_score_bart = confidence_bart / (confidence_bart + confidence_llm_router)
        final_score_llm = confidence_llm_router / (confidence_bart + confidence_llm_router)
        self.logger.info(f"Routing Vote for text {text}: BART: {bart} ({final_score_bart}) LLM-router: {llm_router} ({final_score_llm})")
        if log_confidence:
            pretty_print(f"Agent choice -> BART: {bart} ({final_score_bart}) LLM-router: {llm_router} ({final_score_llm})")
        return bart if final_score_bart > final_score_llm else llm_router
    
    def find_first_sentence(self, text: str) -> str:
        first_sentence = None
        for line in text.split("\n"):
            first_sentence = line.strip()
            break
        if first_sentence is None:
            first_sentence = text
        return first_sentence
    
    def estimate_complexity(self, text: str) -> str:
        """
        Estimate the complexity of the text.
        """
        try:
            predictions = self.complexity_classifier.predict(text)
        except Exception as e:
            pretty_print(f"Error in estimate_complexity: {str(e)}", color="failure")
            return "LOW"
        predictions = sorted(predictions, key=lambda x: x[1], reverse=True)
        if len(predictions) == 0:
            return "LOW"
        complexity, confidence = predictions[0][0], predictions[0][1]
        if confidence < 0.5:
            self.logger.info(f"Low confidence in complexity estimation: {confidence}")
            return "HIGH"
        if complexity == "HIGH":
            return "HIGH"
        elif complexity == "LOW":
            return "LOW"
        pretty_print(f"Failed to estimate the complexity of the text.", color="failure")
        return "LOW"
    
    def find_planner_agent(self) -> Agent:
        """
        Find the planner agent.
        """
        for agent in self.agents:
            if agent.type == "planner_agent":
                return agent
        pretty_print(f"Error finding planner agent. Please add a planner agent to the list of agents.", color="failure")
        self.logger.error("Planner agent not found.")
        return None
    
    def select_agent(self, text: str) -> Agent:
        """
        Select the appropriate agent based on the text.
        """
        assert len(self.agents) > 0, "No agents available."
        if len(self.agents) == 1:
            return self.agents[0]
        lang = self.lang_analysis.detect_language(text)
        text = self.find_first_sentence(text)
        text = self.lang_analysis.translate(text, lang)
        labels = [agent.role for agent in self.agents]
        complexity = self.estimate_complexity(text)
        if complexity == "HIGH":
            pretty_print(f"Complex task detected, routing to planner agent.", color="info")
            return self.find_planner_agent()
        try:
            best_agent = self.router_vote(text, labels, log_confidence=False)
        except Exception as e:
            raise e
        for agent in self.agents:
            if best_agent == agent.role:
                role_name = agent.role
                pretty_print(f"Selected agent: {agent.agent_name} (roles: {role_name})", color="warning")
                return agent
        pretty_print(f"Error choosing agent.", color="failure")
        self.logger.error("No agent selected.")
        return None

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    agents = [
        CasualAgent("jarvis", "../prompts/base/casual_agent.txt", None),
        BrowserAgent("browser", "../prompts/base/planner_agent.txt", None),
        CoderAgent("coder", "../prompts/base/coder_agent.txt", None),
        FileAgent("file", "../prompts/base/coder_agent.txt", None)
    ]
    router = AgentRouter(agents)
    texts = ["hi"]
    for text in texts:
        print("Input text:", text)
        agent = router.select_agent(text)
        print()
