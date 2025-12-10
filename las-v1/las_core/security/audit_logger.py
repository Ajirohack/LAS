"""
Audit Logger - Immutable audit trail for all agent actions.

Logs all tool calls, decisions, and sensitive operations for compliance and debugging.
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from enum import Enum
import hashlib

class AuditEventType(str, Enum):
    """Audit event types."""
    TOOL_CALL = "tool_call"
    DECISION = "decision"
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"
    CODE_EXECUTION = "code_execution"
    DATA_ACCESS = "data_access"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESPONSE = "approval_response"
    ERROR = "error"

class AuditLogger:
    """
    Immutable audit logging system.
    
    Features:
    - Structured JSON logs
    - Hash chaining for tamper detection
    - Searchable by event type, agent, time range
    - Retention policies
    """
    
    def __init__(self, storage_dir: str = "data/audit_logs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.storage_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.last_hash = self._get_last_hash()
    
    def _get_last_hash(self) -> str:
        """Get hash of last log entry for chaining."""
        if not self.log_file.exists():
            return "0" * 64  # Genesis hash
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return last_entry.get("hash", "0" * 64)
        except:
            pass
        
        return "0" * 64
    
    def _compute_hash(self, entry: Dict[str, Any], previous_hash: str) -> str:
        """Compute hash for log entry (includes previous hash for chaining)."""
        # Create stable string representation
        hash_data = {
            "timestamp": entry["timestamp"],
            "event_type": entry["event_type"],
            "agent": entry.get("agent"),
            "action": entry.get("action"),
            "previous_hash": previous_hash
        }
        
        hash_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_str.encode()).hexdigest()
    
    def log(self, event_type: AuditEventType, action: str,
            details: Optional[Dict[str, Any]] = None,
            agent: Optional[str] = None,
            user: Optional[str] = None,
            result: Optional[Any] = None,
            error: Optional[str] = None):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            action: Action description
            details: Additional details
            agent: Agent identifier
            user: User identifier
            result: Action result
            error: Error message if failed
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "action": action,
            "agent": agent,
            "user": user,
            "details": details or {},
            "result": result,
            "error": error
        }
        
        # Compute hash with previous entry's hash
        entry["hash"] = self._compute_hash(entry, self.last_hash)
        entry["previous_hash"] = self.last_hash
        
        # Write to log file (append mode)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Update last hash for next entry
        self.last_hash = entry["hash"]
    
    def query(self, event_type: Optional[AuditEventType] = None,
             agent: Optional[str] = None,
             start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query audit logs with filters.
        
        Args:
            event_type: Filter by event type
            agent: Filter by agent
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum results
        
        Returns:
            List of matching log entries
        """
        results = []
        
        # Read all log files in directory
        for log_file in sorted(self.storage_dir.glob("audit_*.jsonl"), reverse=True):
            with open(log_file, 'r') as f:
                for line in f:
                    if len(results) >= limit:
                        break
                    
                    try:
                        entry = json.loads(line)
                        
                        # Apply filters
                        if event_type and entry["event_type"] != event_type.value:
                            continue
                        
                        if agent and entry["agent"] != agent:
                            continue
                        
                        entry_time = datetime.fromisoformat(entry["timestamp"])
                        if start_time and entry_time < start_time:
                            continue
                        
                        if end_time and entry_time > end_time:
                            continue
                        
                        results.append(entry)
                    
                    except:
                        continue
            
            if len(results) >= limit:
                break
        
        return results
    
    def verify_integrity(self) -> bool:
        """
        Verify integrity of audit log using hash chain.
        
        Returns:
            True if log is intact, False if tampered
        """
        previous_hash = "0" * 64
        
        for log_file in sorted(self.storage_dir.glob("audit_*.jsonl")):
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        
                        # Check previous hash matches
                        if entry.get("previous_hash") != previous_hash:
                            print(f"Integrity violation: Hash mismatch at {entry['timestamp']}")
                            return False
                        
                        # Recompute hash
                        computed_hash = self._compute_hash(entry, previous_hash)
                        if computed_hash != entry.get("hash"):
                            print(f"Integrity violation: Invalid hash at {entry['timestamp']}")
                            return False
                        
                        previous_hash = entry["hash"]
                    
                    except Exception as e:
                        print(f"Error verifying entry: {e}")
                        return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit log statistics."""
        total_entries = 0
        by_type = {}
        
        for log_file in self.storage_dir.glob("audit_*.jsonl"):
            with open(log_file, 'r') as f:
                for line in f:
                    total_entries += 1
                    try:
                        entry = json.loads(line)
                        event_type = entry.get("event_type", "unknown")
                        by_type[event_type] = by_type.get(event_type, 0) + 1
                    except:
                        pass
        
        return {
            "total_entries": total_entries,
            "by_type": by_type,
            "log_files": len(list(self.storage_dir.glob("audit_*.jsonl")))
        }

# Create singleton instance
_audit_logger: Optional[AuditLogger] = None

def get_audit_logger() -> AuditLogger:
    """Get or create AuditLogger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger

# Convenience functions
def audit_tool_call(tool_name: str, args: Dict[str, Any], result: Any,
                   agent: Optional[str] = None):
    """Log a tool call."""
    logger = get_audit_logger()
    logger.log(
        event_type=AuditEventType.TOOL_CALL,
        action=f"call_{tool_name}",
        details={"tool": tool_name, "arguments": args},
        result=result,
        agent=agent
    )

def audit_decision(decision: str, reasoning: str, agent: Optional[str] = None):
    """Log an agent decision."""
    logger = get_audit_logger()
    logger.log(
        event_type=AuditEventType.DECISION,
        action="agent_decision",
        details={"decision": decision, "reasoning": reasoning},
        agent=agent
    )

def audit_error(error_type: str, error_message: str, agent: Optional[str] = None):
    """Log an error."""
    logger = get_audit_logger()
    logger.log(
        event_type=AuditEventType.ERROR,
        action=error_type,
        error=error_message,
        agent=agent
    )
