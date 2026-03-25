"""
JARVIS 2.0 — Command Router
Dynamically imports and executes tools resolved by the Intent Engine.
"""
import importlib
import asyncio
from core.logger import get_logger
from core.tool_registry import ToolSpec

logger = get_logger("CommandRouter")


class CommandRouter:
    """
    Executes a ToolSpec by dynamically importing its module and calling its function.
    Handles both sync and async callables.
    """

    def execute(self, tool: ToolSpec, params: dict) -> str:
        """
        Execute a tool and return the response string.
        Handles dynamic import, sync/async dispatch, and error wrapping.
        """
        try:
            module = importlib.import_module(tool.module_path)
            func = getattr(module, tool.function_name, None)

            # If the function lives on a class instance (like ActionEngine),
            # try to find a singleton or instance first.
            if func is None:
                # Look for common singleton patterns
                instance = self._find_instance(module, tool.function_name)
                if instance:
                    func = getattr(instance, tool.function_name, None)

            if func is None:
                logger.error(f"CommandRouter: Function '{tool.function_name}' not found in '{tool.module_path}'")
                return f"Tool '{tool.name}' is registered but its function could not be found."

            logger.info(f"CommandRouter: Executing {tool.name} -> {tool.module_path}.{tool.function_name}({params})")

            # Execute sync or async
            if tool.is_async or asyncio.iscoroutinefunction(func):
                return self._run_async(func, params)
            else:
                return self._run_sync(func, params)

        except Exception as e:
            logger.error(f"CommandRouter execution error for {tool.name}: {e}")
            return f"Tool execution failed: {e}"

    def _find_instance(self, module, function_name: str):
        """
        Search a module for a class instance that has the target method.
        Looks for common patterns: singletons, *_instance vars, etc.
        """
        for attr_name in dir(module):
            attr = getattr(module, attr_name, None)
            if attr and not isinstance(attr, type) and hasattr(attr, function_name):
                return attr
        return None

    def _run_sync(self, func, params: dict) -> str:
        """Run a synchronous function with extracted params."""
        try:
            if params:
                result = func(**params)
            else:
                result = func()
            return str(result) if result is not None else "Done."
        except TypeError:
            # If keyword args don't match, try positional
            try:
                result = func(*params.values()) if params else func()
                return str(result) if result is not None else "Done."
            except Exception as e:
                logger.error(f"Sync execution fallback failed: {e}")
                return f"Execution error: {e}"

    def _run_async(self, func, params: dict) -> str:
        """Run an async function, handling event loop edge cases."""
        try:
            loop = asyncio.get_running_loop()
            future = asyncio.run_coroutine_threadsafe(
                func(**params) if params else func(), loop
            )
            return str(future.result(timeout=60))
        except RuntimeError:
            # No running loop — create one
            result = asyncio.run(func(**params) if params else func())
            return str(result) if result is not None else "Done."


# Singleton
command_router = CommandRouter()
