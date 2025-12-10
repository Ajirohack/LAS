import os
import platform
import socket
import subprocess
import time
from urllib.parse import urlparse
from typing import List, Dict, Any

import httpx
import requests
from dotenv import load_dotenv
from ollama import Client as OllamaClient
from openai import OpenAI
import google.generativeai as genai
from groq import Groq

from sources.logger import Logger
from sources.utility import pretty_print, animate_thinking
from sources.cache import LRUCache

class Provider:
    def __init__(self, provider_name, model, server_address="127.0.0.1:5000", is_local=False):
        self.provider_name = provider_name.lower()
        self.model = model
        self.is_local = is_local
        self.server_ip = server_address
        self.server_address = server_address
        self.available_providers = {
            "ollama": self.ollama_fn,
            "server": self.server_fn,
            "openai": self.openai_fn,
            "lm-studio": self.lm_studio_fn,
            "huggingface": self.huggingface_fn,
            "google": self.google_fn,
            "gemini": self.google_fn, # Alias
            "deepseek": self.deepseek_fn,
            "together": self.together_fn,
            "dsk_deepseek": self.dsk_deepseek,
            "openrouter": self.openrouter_fn,
            "groq": self.groq_fn,
            "ollama-cloud": self.ollama_cloud_fn,
            "test": self.test_fn
        }
        self.logger = Logger("provider.log")
        self.api_key = None
        self.internal_url, self.in_docker = self.get_internal_url()
        self.unsafe_providers = ["openai", "deepseek", "dsk_deepseek", "together", "google", "gemini", "openrouter", "groq"]
        
        # Initialize Cache
        self.cache = LRUCache(capacity=100, ttl=3600) # 1 hour cache

        if self.provider_name not in self.available_providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        if self.provider_name in self.unsafe_providers and self.is_local == False:
            pretty_print("Warning: you are using an API provider. You data will be sent to the cloud.", color="warning")
            self.api_key = self.get_api_key(self.provider_name)
        elif self.provider_name != "ollama":
            pretty_print(f"Provider: {provider_name} initialized at {self.server_ip}", color="success")

    def get_model_name(self) -> str:
        return self.model

    def get_api_key(self, provider):
        load_dotenv()
        if provider == "gemini":
            provider = "google"
        api_key_var = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_var)
        if not api_key:
            pretty_print(f"API key {api_key_var} not found in .env file. Please add it", color="warning")
            # Don't exit, just warn. The user might set it later or via UI.
            return None 
        return api_key
    
    def get_internal_url(self):
        load_dotenv()
        url = os.getenv("DOCKER_INTERNAL_URL")
        if not url: # running on host
            return "http://localhost", False
        return url, True

    def list_models(self, provider_name: str = None) -> List[str]:
        """
        List available models for a specific provider or the current one.
        """
        target_provider = provider_name.lower() if provider_name else self.provider_name
        
        if target_provider == "ollama":
            host = f"{self.internal_url}:11434" if self.is_local else f"http://{self.server_address}"
            try:
                client = OllamaClient(host=host)
                models = client.list()
                return [m['name'] for m in models['models']]
            except Exception as e:
                self.logger.error(f"Failed to list Ollama models: {e}")
                return []
                
        elif target_provider == "ollama-cloud":
            # List models from Ollama Cloud (if supported via API)
            # Typically this might be the same as local but with auth
            try:
                from config.settings import settings
                api_key = settings.ollama_cloud_api_key
                if not api_key:
                    self.logger.warning("Ollama Cloud API key not found")
                    return []
                
                client = OllamaClient(
                    host="https://ollama.com",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                response = client.list()
                
                # Handle response being an object or dict
                if hasattr(response, 'models'):
                    model_list = response.models
                else:
                    model_list = response.get('models', [])
                    
                # Handle model items being objects or dicts
                result = []
                for m in model_list:
                    if hasattr(m, 'model'):
                        result.append(m.model)
                    elif isinstance(m, dict):
                        result.append(m.get('name') or m.get('model'))
                    else:
                        result.append(str(m))
                return result
            except Exception as e:
                self.logger.error(f"Failed to list Ollama Cloud models: {e}")
                return []

        elif target_provider == "openrouter":
            # OpenRouter has a public API for models, but we can also just return a curated list
            # or fetch from https://openrouter.ai/api/v1/models
            try:
                response = requests.get("https://openrouter.ai/api/v1/models")
                if response.status_code == 200:
                    data = response.json()
                    return [m['id'] for m in data['data']]
            except Exception as e:
                self.logger.error(f"Failed to list OpenRouter models: {e}")
                return []
                
        elif target_provider in ["google", "gemini"]:
             # Google GenAI listing
            try:
                api_key = self.get_api_key("google")
                if not api_key: return []
                genai.configure(api_key=api_key)
                models = genai.list_models()
                return [m.name.replace("models/", "") for m in models if 'generateContent' in m.supported_generation_methods]
            except Exception as e:
                self.logger.error(f"Failed to list Google models: {e}")
                return []

        elif target_provider == "groq":
             # Groq listing
            try:
                api_key = self.get_api_key("groq")
                if not api_key: return []
                client = Groq(api_key=api_key)
                models = client.models.list()
                return [m.id for m in models.data]
            except Exception as e:
                self.logger.error(f"Failed to list Groq models: {e}")
                return []

        return []

    def get_langchain_llm(self):
        """
        Returns a LangChain-compatible LLM object based on the current provider.
        """
        if self.provider_name == "ollama":
            from langchain_community.chat_models import ChatOllama
            host = f"{self.internal_url}:11434" if self.is_local else f"http://{self.server_address}"
            return ChatOllama(model=self.model, base_url=host)
            
        elif self.provider_name == "ollama-cloud":
            from langchain_community.chat_models import ChatOllama
            from config.settings import settings
            api_key = settings.ollama_cloud_api_key
            # Assuming standard Ollama API structure but authenticated
            return ChatOllama(
                model=self.model, 
                base_url="https://ollama.com", # Or specific endpoint
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
        elif self.provider_name == "openrouter":
            from langchain_openai import ChatOpenAI
            from config.settings import settings
            return ChatOpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                model=self.model,
                default_headers={
                    "HTTP-Referer": settings.app_url,
                    "X-Title": settings.app_name
                }
            )
            
        elif self.provider_name in ["google", "gemini"]:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                convert_system_message_to_human=True
            )
            
        elif self.provider_name == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(
                api_key=self.api_key,
                model_name=self.model
            )
            
        elif self.provider_name == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(api_key=self.api_key, model=self.model)
            
        else:
            # Fallback for other providers or raise error
            # For now, try to use OpenAI compatible client if possible, or raise
            raise ValueError(f"Provider {self.provider_name} not supported for LangChain integration yet.")

    def respond(self, history, verbose=True):
        """
        Use the choosen provider to generate text.
        """
        # Check cache first
        cache_key = [self.provider_name, self.model, history]
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.info(f"Cache hit for provider: {self.provider_name}")
            if verbose:
                print(cached_response)
            return cached_response

        llm = self.available_providers[self.provider_name]
        self.logger.info(f"Using provider: {self.provider_name} at {self.server_ip}")
        try:
            thought = llm(history, verbose)
            # Cache the result
            self.cache.put(cache_key, thought)
        except KeyboardInterrupt:
            self.logger.warning("User interrupted the operation with Ctrl+C")
            return "Operation interrupted by user. REQUEST_EXIT"
        except ConnectionError as e:
            raise ConnectionError(f"{str(e)}\nConnection to {self.server_ip} failed.")
        except AttributeError as e:
            raise NotImplementedError(f"{str(e)}\nIs {self.provider_name} implemented ?")
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"{str(e)}\nA import related to provider {self.provider_name} was not found. Is it installed ?")
        except Exception as e:
            if "try again later" in str(e).lower():
                return f"{self.provider_name} server is overloaded. Please try again later."
            if "refused" in str(e):
                return f"Server {self.server_ip} seem offline. Unable to answer."
            raise Exception(f"Provider {self.provider_name} failed: {str(e)}") from e
        return thought

    def is_ip_online(self, address: str, timeout: int = 10) -> bool:
        """
        Check if an address is online by sending a ping request.
        """
        if not address:
            return False
        parsed = urlparse(address if address.startswith(('http://', 'https://')) else f'http://{address}')

        hostname = parsed.hostname or address
        if "127.0.0.1" in address or "localhost" in address:
            return True
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            self.logger.error(f"Cannot resolve: {hostname}")
            return False
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ip_address]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return False

    def server_fn(self, history, verbose=False):
        """
        Use a remote server with LLM to generate text.
        """
        thought = ""
        route_setup = f"{self.server_ip}/setup"
        route_gen = f"{self.server_ip}/generate"

        if not self.is_ip_online(self.server_ip):
            pretty_print(f"Server is offline at {self.server_ip}", color="failure")

        try:
            requests.post(route_setup, json={"model": self.model})
            requests.post(route_gen, json={"messages": history})
            is_complete = False
            while not is_complete:
                try:
                    response = requests.get(f"{self.server_ip}/get_updated_sentence")
                    if "error" in response.json():
                        pretty_print(response.json()["error"], color="failure")
                        break
                    thought = response.json()["sentence"]
                    is_complete = bool(response.json()["is_complete"])
                    time.sleep(2)
                except requests.exceptions.RequestException as e:
                    pretty_print(f"HTTP request failed: {str(e)}", color="failure")
                    break
                except ValueError as e:
                    pretty_print(f"Failed to parse JSON response: {str(e)}", color="failure")
                    break
                except Exception as e:
                    pretty_print(f"An error occurred: {str(e)}", color="failure")
                    break
        except KeyError as e:
            raise Exception(
                f"{str(e)}\nError occured with server route. Are you using the correct address for the config.ini provider?") from e
        except Exception as e:
            raise e
        return thought

    def ollama_fn(self, history, verbose=False):
        """
        Use local or remote Ollama server to generate text.
        """
        thought = ""
        host = f"{self.internal_url}:11434" if self.is_local else f"http://{self.server_address}"
        client = OllamaClient(host=host)

        try:
            stream = client.chat(
                model=self.model,
                messages=history,
                stream=True,
            )
            for chunk in stream:
                if verbose:
                    print(chunk["message"]["content"], end="", flush=True)
                thought += chunk["message"]["content"]
        except httpx.ConnectError as e:
            raise Exception(
                f"\nOllama connection failed at {host}. Check if the server is running."
            ) from e
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                # Auto-pull logic
                pretty_print(f"Model {self.model} not found. Attempting to pull...", color="info")
                animate_thinking(f"Downloading {self.model}...")
                try:
                    client.pull(self.model)
                    pretty_print(f"Model {self.model} pulled successfully.", color="success")
                    return self.ollama_fn(history, verbose) # Retry
                except Exception as pull_error:
                    raise Exception(f"Failed to pull model {self.model}: {pull_error}") from pull_error
            
            if "refused" in str(e).lower():
                raise Exception(f"Connection refused to {host}. Is Ollama running?")
            raise e
        return thought

    def ollama_cloud_fn(self, history, verbose=False):
        """
        Use Ollama Cloud to generate text.
        """
        thought = ""
        from config.settings import settings
        api_key = settings.ollama_cloud_api_key
        
        if not api_key:
            raise ValueError("Ollama Cloud API key not found in settings.")

        client = OllamaClient(
            host="https://ollama.com",
            headers={"Authorization": f"Bearer {api_key}"}
        )

        try:
            stream = client.chat(
                model=self.model,
                messages=history,
                stream=True,
            )
            for chunk in stream:
                # Handle chunk being object or dict
                content = ""
                if hasattr(chunk, 'message'):
                    msg = chunk.message
                    if hasattr(msg, 'content'):
                        content = msg.content
                    elif isinstance(msg, dict):
                        content = msg.get('content', '')
                elif isinstance(chunk, dict):
                    content = chunk.get('message', {}).get('content', '')
                
                if verbose:
                    print(content, end="", flush=True)
                thought += content
        except Exception as e:
            raise Exception(f"Ollama Cloud request failed: {e}") from e
        return thought


    def huggingface_fn(self, history, verbose=False):
        """
        Use HuggingFace Inference API to generate text.
        Supports streaming and advanced features.
        """
        from services.huggingface_service import get_huggingface_service
        from services.cost_tracker import get_cost_tracker, Provider as CostProvider
        
        hf_service = get_huggingface_service()
        
        try:
            # Use streaming for better UX
            stream = hf_service.chat_completion(
                messages=history,
                model=self.model,
                stream=True
            )
            
            thought = ""
            total_tokens = 0
            
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        content = delta.content
                        if verbose:
                            print(content, end="", flush=True)
                        thought += content
                
                # Track usage if available
                if hasattr(chunk, 'usage') and chunk.usage:
                    tracker = get_cost_tracker()
                    tracker.track_usage(
                        provider=CostProvider.OPENAI,  # HF uses similar pricing
                        input_tokens=chunk.usage.prompt_tokens,
                        output_tokens=chunk.usage.completion_tokens,
                        agent="user"
                    )
            
            return thought
        except Exception as e:
            raise Exception(f"HuggingFace Inference API error: {str(e)}") from e

    def openai_fn(self, history, verbose=False):
        """
        Use openai to generate text.
        """
        base_url = self.server_ip
        if self.is_local and self.in_docker:
            try:
                host, port = base_url.split(':')
            except Exception as e:
                port = "8000"
            client = OpenAI(api_key=self.api_key, base_url=f"{self.internal_url}:{port}")
        elif self.is_local:
            client = OpenAI(api_key=self.api_key, base_url=f"http://{base_url}")
        else:
            client = OpenAI(api_key=self.api_key)

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=history,
            )
            if response is None:
                raise Exception("OpenAI response is empty.")
            thought = response.choices[0].message.content
            if verbose:
                print(thought)
            return thought
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}") from e

    def google_fn(self, history, verbose=False):
        """
        Use google gemini to generate text.
        """
        if not self.api_key:
            raise ValueError("Google API Key is missing.")
            
        genai.configure(api_key=self.api_key)
        
        # Convert history to Gemini format
        # History is list of {'role': 'user'/'assistant'/'system', 'content': '...'}
        # Gemini uses 'user' and 'model'. System instructions are passed to GenerativeModel.
        
        system_instruction = None
        gemini_history = []
        
        for msg in history:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                system_instruction = content
            elif role == 'user':
                gemini_history.append({'role': 'user', 'parts': [content]})
            elif role == 'assistant':
                gemini_history.append({'role': 'model', 'parts': [content]})
                
        model = genai.GenerativeModel(self.model, system_instruction=system_instruction)
        
        try:
            # If there is history, start a chat session. 
            # Note: Gemini chat history management is slightly different, 
            # usually we just send the full history as a prompt or use start_chat with history.
            # Here we'll use start_chat with the history we built (excluding the last message which is the new prompt)
            
            if not gemini_history:
                # Should not happen if user sent a message
                return ""

            last_message = gemini_history.pop()
            if last_message['role'] != 'user':
                 # If last message is not user, something is wrong or it's a continuation.
                 # Just treat everything as history?
                 # For simplicity, let's just use generate_content with the full list if possible,
                 # or use chat.
                 pass

            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(last_message['parts'][0], stream=True)
            
            thought = ""
            for chunk in response:
                if verbose:
                    print(chunk.text, end="", flush=True)
                thought += chunk.text
            return thought
            
        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}") from e

    def together_fn(self, history, verbose=False):
        """
        Use together AI for completion
        """
        from together import Together
        client = Together(api_key=self.api_key)
        if self.is_local:
            raise Exception("Together AI is not available for local use. Change config.ini")

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=history,
            )
            if response is None:
                raise Exception("Together AI response is empty.")
            thought = response.choices[0].message.content
            if verbose:
                print(thought)
            return thought
        except Exception as e:
            raise Exception(f"Together AI API error: {str(e)}") from e

    def deepseek_fn(self, history, verbose=False):
        """
        Use deepseek api to generate text.
        """
        client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        if self.is_local:
            raise Exception("Deepseek (API) is not available for local use. Change config.ini")
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=history,
                stream=False
            )
            thought = response.choices[0].message.content
            if verbose:
                print(thought)
            return thought
        except Exception as e:
            raise Exception(f"Deepseek API error: {str(e)}") from e

    def lm_studio_fn(self, history, verbose=False):
        """
        Use local lm-studio server to generate text.
        """
        if self.in_docker:
            # Extract port from server_address if present
            port = "1234"  # default
            if ":" in self.server_address:
                port = self.server_address.split(":")[1]
            url = f"{self.internal_url}:{port}"
        else:
            url = f"http://{self.server_ip}"
        route_start = f"{url}/v1/chat/completions"
        payload = {
            "messages": history,
            "temperature": 0.7,
            "max_tokens": 4096,
            "model": self.model
        }

        try:
            response = requests.post(route_start, json=payload, timeout=30)
            if response.status_code != 200:
                raise Exception(f"LM Studio returned status {response.status_code}: {response.text}")
            if not response.text.strip():
                raise Exception("LM Studio returned empty response")
            try:
                result = response.json()
            except ValueError as json_err:
                raise Exception(f"Invalid JSON from LM Studio: {response.text[:200]}") from json_err

            if verbose:
                print("Response from LM Studio:", result)
            choices = result.get("choices", [])
            if not choices:
                raise Exception(f"No choices in LM Studio response: {result}")

            message = choices[0].get("message", {})
            content = message.get("content", "")
            if not content:
                raise Exception(f"Empty content in LM Studio response: {result}")
            return content

        except requests.exceptions.Timeout:
            raise Exception("LM Studio request timed out - check if server is responsive")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to LM Studio at {route_start} - check if server is running")
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}") from e
        except Exception as e:
            if "LM Studio" in str(e):
                raise  # Re-raise our custom exceptions
            raise Exception(f"Unexpected error: {str(e)}") from e
        return thought

    def openrouter_fn(self, history, verbose=False):
        """
        Use OpenRouter API to generate text.
        """
        from config.settings import settings
        from services.cost_tracker import get_cost_tracker, Provider as CostProvider

        client = OpenAI(
            api_key=self.api_key, 
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": settings.app_url,
                "X-Title": settings.app_name
            }
        )
        
        try:
            # Enable streaming and usage tracking
            response = client.chat.completions.create(
                model=self.model,
                messages=history,
                stream=True,
                stream_options={"include_usage": True}
            )
            
            thought = ""
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        if verbose:
                            print(delta.content, end="", flush=True)
                        thought += delta.content
                
                # Track usage if available in the chunk (usually the last one)
                if hasattr(chunk, 'usage') and chunk.usage:
                    tracker = get_cost_tracker()
                    tracker.track_usage(
                        provider=CostProvider.OPENROUTER,
                        input_tokens=chunk.usage.prompt_tokens,
                        output_tokens=chunk.usage.completion_tokens,
                        agent="user" 
                    )

            return thought
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}") from e

    def groq_fn(self, history, verbose=False):
        """
        Use Groq API to generate text.
        """
        if not self.api_key:
            raise ValueError("Groq API Key is missing.")
            
        client = Groq(api_key=self.api_key)
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=history,
                stream=True
            )
            
            thought = ""
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    if verbose:
                        print(content, end="", flush=True)
                    thought += content
            return thought
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}") from e

    def dsk_deepseek(self, history, verbose=False):
        """
        Use: xtekky/deepseek4free
        For free api. Api key should be set to DSK_DEEPSEEK_API_KEY
        This is an unofficial provider, you'll have to find how to set it up yourself.
        """
        from dsk.api import (
            DeepSeekAPI,
            AuthenticationError,
            RateLimitError,
            NetworkError,
            CloudflareError,
            APIError
        )
        thought = ""
        message = '\n---\n'.join([f"{msg['role']}: {msg['content']}" for msg in history])

        try:
            api = DeepSeekAPI(self.api_key)
            chat_id = api.create_chat_session()
            for chunk in api.chat_completion(chat_id, message):
                if chunk['type'] == 'text':
                    thought += chunk['content']
            return thought
        except AuthenticationError:
            raise AuthenticationError("Authentication failed. Please check your token.") from e
        except RateLimitError:
            raise RateLimitError("Rate limit exceeded. Please wait before making more requests.") from e
        except CloudflareError as e:
            raise CloudflareError(f"Cloudflare protection encountered: {str(e)}") from e
        except NetworkError:
            raise NetworkError("Network error occurred. Check your internet connection.") from e
        except APIError as e:
            raise APIError(f"API error occurred: {str(e)}") from e
        return None

    def test_fn(self, history, verbose=True):
        """
        This function is used to conduct tests.
        """
        thought = """
\n\n```json\n{\n  \"plan\": [\n    {\n      \"agent\": \"Web\",\n      \"id\": \"1\",\n      \"need\": null,\n      \"task\": \"Conduct a comprehensive web search to identify at least five AI startups located in Osaka. Use reliable sources and websites such as Crunchbase, TechCrunch, or local Japanese business directories. Capture the company names, their websites, areas of expertise, and any other relevant details.\"\n    },\n    {\n      \"agent\": \"Web\",\n      \"id\": \"2\",\n      \"need\": null,\n      \"task\": \"Perform a similar search to find at least five AI startups in Tokyo. Again, use trusted sources like Crunchbase, TechCrunch, or Japanese business news websites. Gather the same details as for Osaka: company names, websites, areas of focus, and additional information.\"\n    },\n    {\n      \"agent\": \"File\",\n      \"id\": \"3\",\n      \"need\": [\"1\", \"2\"],\n      \"task\": \"Create a new text file named research_japan.txt in the user's home directory. Organize the data collected from both searches into this file, ensuring it is well-structured and formatted for readability. Include headers for Osaka and Tokyo sections, followed by the details of each startup found.\"\n    }\n  ]\n}\n```
        """
        return thought


if __name__ == "__main__":
    provider = Provider("server", "deepseek-r1:32b", " x.x.x.x:8080")
    res = provider.respond(["user", "Hello, how are you?"])
    print("Response:", res)
