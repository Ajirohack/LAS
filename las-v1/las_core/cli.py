#!/usr/bin python3

import sys
import argparse
import configparser
import asyncio
import os
import json
from pathlib import Path

from sources.llm_provider import Provider
from sources.interaction import Interaction
from sources.agents import Agent, CoderAgent, CasualAgent, FileAgent, PlannerAgent, BrowserAgent, McpAgent
from sources.browser import Browser, create_driver
from sources.utility import pretty_print

import warnings
warnings.filterwarnings("ignore")

config = configparser.ConfigParser()
config.read('config.ini')

async def run_agent():
    pretty_print("Initializing...", color="status")
    stealth_mode = config.getboolean('BROWSER', 'stealth_mode')
    personality_folder = "jarvis" if config.getboolean('MAIN', 'jarvis_personality') else "base"
    languages = config["MAIN"]["languages"].split(' ')

    provider = Provider(provider_name=config["MAIN"]["provider_name"],
                        model=config["MAIN"]["provider_model"],
                        server_address=config["MAIN"]["provider_server_address"],
                        is_local=config.getboolean('MAIN', 'is_local'))

    browser = Browser(
        create_driver(headless=config.getboolean('BROWSER', 'headless_browser'), stealth_mode=stealth_mode, lang=languages[0]),
        anticaptcha_manual_install=stealth_mode
    )

    agents = [
        CasualAgent(name=config["MAIN"]["agent_name"],
                    prompt_path=f"prompts/{personality_folder}/casual_agent.txt",
                    provider=provider, verbose=False),
        CoderAgent(name="coder",
                   prompt_path=f"prompts/{personality_folder}/coder_agent.txt",
                   provider=provider, verbose=False),
        FileAgent(name="File Agent",
                  prompt_path=f"prompts/{personality_folder}/file_agent.txt",
                  provider=provider, verbose=False),
        BrowserAgent(name="Browser",
                     prompt_path=f"prompts/{personality_folder}/browser_agent.txt",
                     provider=provider, verbose=False, browser=browser),
        PlannerAgent(name="Planner",
                     prompt_path=f"prompts/{personality_folder}/planner_agent.txt",
                     provider=provider, verbose=False, browser=browser),
    ]

    interaction = Interaction(agents,
                              tts_enabled=config.getboolean('MAIN', 'speak'),
                              stt_enabled=config.getboolean('MAIN', 'listen'),
                              recover_last_session=config.getboolean('MAIN', 'recover_last_session'),
                              langs=languages
                            )
    try:
        while interaction.is_active:
            interaction.get_user()
            if await interaction.think():
                interaction.show_answer()
                interaction.speak_answer()
    except Exception as e:
        if config.getboolean('MAIN', 'save_session'):
            interaction.save_session()
        raise e
    finally:
        if config.getboolean('MAIN', 'save_session'):
            interaction.save_session()

def create_plugin_scaffold(name: str):
    """Create a new plugin scaffold."""
    base_dir = Path("plugins")
    plugin_dir = base_dir / name
    
    if plugin_dir.exists():
        print(f"Plugin '{name}' already exists.")
        return

    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    # manifest.json
    manifest = {
        "name": name,
        "version": "0.1.0",
        "description": f"Description for {name}",
        "entry_point": "plugin.py",
        "permissions": []
    }
    
    with open(plugin_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    # plugin.py
    plugin_code = f"""
from typing import Dict, Any

def run(args: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Entry point for {name} plugin.
    \"\"\"
    print("Running plugin: {name}")
    return {{"status": "success", "message": "Hello from {name}!"}}
"""
    with open(plugin_dir / "plugin.py", "w") as f:
        f.write(plugin_code.strip())
        
    # __init__.py
    with open(plugin_dir / "__init__.py", "w") as f:
        f.write("")
        
    print(f"Created plugin scaffold in {plugin_dir}")

async def main():
    parser = argparse.ArgumentParser(description="Local Agent System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the agent system")
    
    # Create plugin command
    plugin_parser = subparsers.add_parser("create-plugin", help="Create a new plugin")
    plugin_parser.add_argument("name", help="Name of the plugin")
    
    args = parser.parse_args()
    
    if args.command == "run" or args.command is None:
        await run_agent()
    elif args.command == "create-plugin":
        create_plugin_scaffold(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())