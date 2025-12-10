#!/usr/bin/env python3
"""
LAS CLI - Terminal client for Local Agent System

Usage:
    las-cli chat                    # Interactive chat mode
    las-cli query <text>           # One-shot query
    las-cli status                 # Check API status
    las-cli skills                 # List saved skills
    las-cli reflections            # List reflections
    las-cli plugins                # List plugins
"""

import sys
import argparse
import requests
from typing import Optional

class LASCLIClient:
    """CLI client for LAS API."""
    
    def __init__(self, base_url: str = "http://localhost:7777"):
        self.base_url = base_url.rstrip('/')
    
    def chat(self):
        """Interactive chat mode."""
        print("LAS Interactive Chat")
        print("Type 'exit' or 'quit' to end session\n")
        
        while True:
            try:
                query = input("You: ").strip()
                
                if query.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Send query
                response = requests.post(
                    f"{self.base_url}/api/query",
                    json={"query": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", data.get("result", "No response"))
                    print(f"\nAgent: {answer}\n")
                else:
                    print(f"Error: {response.status_code} - {response.text}\n")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")
    
    def query(self, text: str):
        """One-shot query."""
        try:
            response = requests.post(
                f"{self.base_url}/api/query",
                json={"query": text}
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", data.get("result", "No response"))
                print(answer)
            else:
                print(f"Error: {response.status_code} - {response.text}")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def status(self):
        """Check API health."""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data.get('status', 'unknown')}")
                print(f"Version: {data.get('version', 'unknown')}")
            else:
                print(f"API unavailable: {response.status_code}")
                sys.exit(1)
        except Exception as e:
            print(f"Cannot connect to API: {e}")
            sys.exit(1)
    
    def list_skills(self):
        """List saved skills."""
        try:
            response = requests.get(f"{self.base_url}/api/memory/skills")
            if response.status_code == 200:
                skills = response.json().get("skills", [])
                if skills:
                    print("Saved Skills:")
                    for skill in skills:
                        print(f"  - {skill}")
                else:
                    print("No skills saved yet")
            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
    
    def list_reflections(self):
        """List reflections."""
        try:
            response = requests.get(f"{self.base_url}/api/memory/reflections")
            if response.status_code == 200:
                reflections = response.json().get("reflections", [])
                if reflections:
                    print(f"Reflections ({len(reflections)}):")
                    for r in reflections:
                        task = r.get("task_description", "Unknown")
                        print(f"  - {task[:60]}...")
                else:
                    print("No reflections yet")
            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
    
    def list_plugins(self):
        """List plugins."""
        try:
            response = requests.get(f"{self.base_url}/api/plugins")
            if response.status_code == 200:
                plugins = response.json().get("plugins", [])
                if plugins:
                    print("Installed Plugins:")
                    for p in plugins:
                        status = "✓" if p.get("loaded") else "○"
                        print(f"  {status} {p['name']} v{p['version']} - {p['description']}")
                else:
                    print("No plugins installed")
            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="LAS CLI - Terminal client for Local Agent System")
    parser.add_argument("--url", default="http://localhost:7777", help="LAS API URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Chat command
    subparsers.add_parser("chat", help="Interactive chat mode")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="One-shot query")
    query_parser.add_argument("text", nargs="+", help="Query text")
    
    # Status command
    subparsers.add_parser("status", help="Check API status")
    
    # Skills command
    subparsers.add_parser("skills", help="List saved skills")
    
    # Reflections command
    subparsers.add_parser("reflections", help="List reflections")
    
    # Plugins command
    subparsers.add_parser("plugins", help="List plugins")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    client = LASCLIClient(base_url=args.url)
    
    if args.command == "chat":
        client.chat()
    elif args.command == "query":
        query_text = " ".join(args.text)
        client.query(query_text)
    elif args.command == "status":
        client.status()
    elif args.command == "skills":
        client.list_skills()
    elif args.command == "reflections":
        client.list_reflections()
    elif args.command == "plugins":
        client.list_plugins()

if __name__ == "__main__":
    main()
