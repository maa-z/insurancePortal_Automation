import asyncio
import sys


def proactor_loop_factory():
    """
    Custom loop factory for Uvicorn and AsyncIO Runner on Windows.
    Returns a new ProactorEventLoop instance to enable Playwright
    browser subprocess execution without NotImplementedError.
    """
    if sys.platform == "win32":
        return asyncio.ProactorEventLoop()
    return asyncio.new_event_loop()
