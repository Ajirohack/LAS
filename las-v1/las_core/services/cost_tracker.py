"""
Cost Tracker - Monitor and manage API costs for LLM providers.
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum

class Provider(str, Enum):
    """Supported providers for cost tracking."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    GEMINI = "gemini"
    OLLAMA = "ollama"  # Free/local

# Cost per 1M tokens (approximate, should be configurable)
COST_PER_1M_TOKENS = {
    Provider.OPENAI: {"input": 0.50, "output": 1.50},  # GPT-4o mini avg
    Provider.ANTHROPIC: {"input": 3.00, "output": 15.00},  # Claude avg
    Provider.OPENROUTER: {"input": 0.50, "output": 1.50},  # Model-dependent
    Provider.GROQ: {"input": 0.0, "output": 0.0},  # Currently free
    Provider.GEMINI: {"input": 0.125, "output": 0.375},  # Gemini 1.5 Flash
    Provider.OLLAMA: {"input": 0.0, "output": 0.0}  # Local/free
}

class CostTracker:
    """Track API costs and manage budgets."""
    
    def __init__(self, storage_dir: str = "data/costs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.usage_file = self.storage_dir / "usage.json"
        self.budgets_file = self.storage_dir / "budgets.json"
        
        self.usage: Dict[str, Any] = self.load_usage()
        self.budgets: Dict[str, float] = self.load_budgets()
    
    def load_usage(self) -> Dict[str, Any]:
        """Load usage data from disk."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load usage: {e}")
        
        return {"daily": {}, "monthly": {}, "total": {}}
    
    def save_usage(self):
        """Save usage data to disk."""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage, f, indent=2)
        except Exception as e:
            print(f"Failed to save usage: {e}")
    
    def load_budgets(self) -> Dict[str, float]:
        """Load budget limits from disk."""
        if self.budgets_file.exists():
            try:
                with open(self.budgets_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load budgets: {e}")
        
        return {}
    
    def save_budgets(self):
        """Save budget limits to disk."""
        try:
            with open(self.budgets_file, 'w') as f:
                json.dump(self.budgets, f, indent=2)
        except Exception as e:
            print(f"Failed to save budgets: {e}")
    
    def track_usage(self, provider: str, input_tokens: int, output_tokens: int,
                   agent: Optional[str] = None):
        """
        Track token usage and calculate cost.
        
        Args:
            provider: Provider name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            agent: Optional agent identifier
        """
        # Get cost rates
        rates = COST_PER_1M_TOKENS.get(provider, {"input": 0, "output": 0})
        
        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        total_cost = input_cost + output_cost
        
        # Get current date keys
        now = datetime.now()
        daily_key = now.strftime("%Y-%m-%d")
        monthly_key = now.strftime("%Y-%m")
        
        # Initialize structures if needed
        for period_type in ["daily", "monthly", "total"]:
            if period_type not in self.usage:
                self.usage[period_type] = {}
        
        # Get period key
        if period_type == "daily":
            period_key = daily_key
        elif period_type == "monthly":
            period_key = monthly_key
        else:
            period_key = "all_time"
        
        # Track by provider
        for period_type, period_key in [("daily", daily_key), ("monthly", monthly_key), ("total", "all_time")]:
            if period_key not in self.usage[period_type]:
                self.usage[period_type][period_key] = {}
            
            if provider not in self.usage[period_type][period_key]:
                self.usage[period_type][period_key][provider] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_cost": 0.0,
                    "requests": 0
                }
            
            usage_data = self.usage[period_type][period_key][provider]
            usage_data["input_tokens"] += input_tokens
            usage_data["output_tokens"] += output_tokens
            usage_data["total_cost"] += total_cost
            usage_data["requests"] += 1
        
        self.save_usage()
        
        # Check budget
        if agent and agent in self.budgets:
            self._check_budget_alert(agent)
    
    def _check_budget_alert(self, agent: str) -> bool:
        """Check if budget limit is exceeded."""
        budget = self.budgets.get(agent, float('inf'))
        spent = self.get_cost_by_agent(agent)
        
        if spent >= budget:
            self.trigger_alert(
                agent=agent,
                message=f"Budget exceeded: ${spent:.2f} / ${budget:.2f}",
                alert_type="critical"
            )
            return True
        elif spent >= budget * 0.9:
            self.trigger_alert(
                agent=agent,
                message=f"Budget warning: ${spent:.2f} / ${budget:.2f} (90%)",
                alert_type="warning"
            )
            return True
        
        return False
    
    def set_budget(self, agent: str, amount: float):
        """Set budget limit for an agent."""
        self.budgets[agent] = amount
        self.save_budgets()
    
    def get_budget(self, agent: str) -> Optional[float]:
        """Get budget limit for an agent."""
        return self.budgets.get(agent)
    
    def get_cost_summary(self, period: str = "daily") -> Dict[str, Any]:
        """
        Get cost summary for a period.
        
        Args:
            period: Period type (daily, monthly, total)
        
        Returns:
            Cost summary dict
        """
        now = datetime.now()
        if period == "daily":
            key = now.strftime("%Y-%m-%d")
        elif period == "monthly":
            key = now.strftime("%Y-%m")
        else:
            key = "all_time"
        
        usage_data = self.usage.get(period, {}).get(key, {})
        
        total_cost = sum(
            provider_data["total_cost"]
            for provider_data in usage_data.values()
        )
        
        total_requests = sum(
            provider_data["requests"]
            for provider_data in usage_data.values()
        )
        
        return {
            "period": period,
            "key": key,
            "total_cost": round(total_cost, 4),
            "total_requests": total_requests,
            "by_provider": {
                provider: {
                    "cost": round(data["total_cost"], 4),
                    "requests": data["requests"],
                    "input_tokens": data["input_tokens"],
                    "output_tokens": data["output_tokens"]
                }
                for provider, data in usage_data.items()
            }
        }
    
    def get_cost_by_agent(self, agent: str, period: str = "total") -> float:
        """Get total cost for a specific agent."""
        # This is a simplified version - would need to track per-agent in production
        return 0.0

    def set_alert_callback(self, callback):
        """Set callback function for budget alerts."""
        self.alert_callback = callback
    
    def trigger_alert(self, agent: str, message: str, alert_type: str = "warning"):
        """Trigger a budget alert."""
        alert = {
            "agent": agent,
            "message": message,
            "type": alert_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Call custom callback if set
        if hasattr(self, 'alert_callback') and self.alert_callback:
            self.alert_callback(alert)
        
        # Save to alert log
        alert_file = self.storage_dir / "alerts.json"
        alerts = []
        
        if alert_file.exists():
            with open(alert_file, 'r') as f:
                alerts = json.load(f)
        
        alerts.append(alert)
        
        with open(alert_file, 'w') as f:
            json.dump(alerts, f, indent=2)
        
        return alert
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent budget alerts."""
        alert_file = self.storage_dir / "alerts.json"
        
        if not alert_file.exists():
            return []
        
        with open(alert_file, 'r') as f:
            alerts = json.load(f)
        
        return alerts[-limit:]

# Create singleton instance
_cost_tracker: Optional[CostTracker] = None

def get_cost_tracker() -> CostTracker:
    """Get or create CostTracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker
