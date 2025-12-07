from enum import Enum
from typing import Callable, Dict, List
from fastapi import BackgroundTasks

event_listeners: Dict[str, List[Callable]] = {}

class EventTypes(str, Enum):
    low_stock = "low_stock"
    repair_request_created = "repair_request_created"
    health_check = "health_check"


def on(event_name: str):
    def decorator(func: Callable):
        if event_name not in event_listeners:
            event_listeners[event_name] = []
        event_listeners[event_name].append(func)
        return func
    return decorator

async def emit(event_name: str, background_tasks: BackgroundTasks, *args, **kwargs):
    if event_name in event_listeners:
        for listener in event_listeners[event_name]:
            background_tasks.add_task(listener, *args, **kwargs)