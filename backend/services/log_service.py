import logging
import asyncio
from datetime import datetime
from collections import deque
from typing import List, Dict

class LogService:
    def __init__(self, max_logs=1000):
        self.logs: deque = deque(maxlen=max_logs)
        self.queues = set() # Set of asyncio.Queue for streaming clients

    def log(self, level: str, message: str, source: str = "system"):
        """Add a log entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "source": source
        }
        self.logs.append(entry)
        
        # Notify all active stream queues
        for q in list(self.queues):
            try:
                q.put_nowait(entry)
            except Exception:
                self.queues.remove(q)
                
        # Also print to terminal
        print(f"[{level.upper()}] {source}: {message}", flush=True)

    def info(self, message: str, source: str = "system"):
        self.log("INFO", message, source)

    def error(self, message: str, source: str = "system"):
        self.log("ERROR", message, source)
    
    def warning(self, message: str, source: str = "system"):
        self.log("WARNING", message, source)

    def get_logs(self, limit: int = 100) -> List[Dict]:
        return list(self.logs)[-limit:]

    async def subscribe(self):
        """Create a new queue for a streaming client."""
        q = asyncio.Queue()
        self.queues.add(q)
        try:
            yield q
        finally:
            self.queues.remove(q)

class UnifiedLoggingHandler(logging.Handler):
    """Custom logging handler to route all python logs into LogService."""
    def emit(self, record):
        try:
            msg = self.format(record)
            log_service.log(record.levelname, msg, source=record.name)
        except Exception:
            self.handleError(record)

# Singleton
log_service = LogService()
