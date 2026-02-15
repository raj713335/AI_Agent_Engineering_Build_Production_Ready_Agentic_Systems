import importlib
import inspect
from langchain.tools import BaseTool
import logging
import pkgutil

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def find_tools(package) -> list[BaseTool]:
    """
    Dynamically and recursively discovers and instantiates tools from a given package.
    It looks for classes that inherit from langchain.tools.BaseTool.
    """
    tools = []

    def on_error(name):
        """Log errors during package walking."""
        logger.warning(f"Could not import module {name} during tool discovery.")

    for module_info in pkgutil.walk_packages(
            path=package.__path__, prefix=package.__name__ + ".", onerror=on_error
    ):
        try:
            # walk_packages finds all modules, but we must import them to inspect
            module = importlib.import_module(module_info.name)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                # Ensure the class is a subclass of BaseTool, is not BaseTool itself,
                # and was defined in the module we are currently inspecting.
                if (
                        issubclass(obj, BaseTool)
                        and obj is not BaseTool
                        and obj.__module__ == module_info.name
                ):
                    # logger.info(f"Discovered tool: {obj.__name__} in {module_info.name}")
                    tools.append(obj())
        except Exception as e:
            # Catch other errors, e.g., during tool instantiation
            logger.warning(f"Error processing module {module_info.name} for tools: {e}")
    logger.info(f"Discovered {len(tools)} tools: {[tool.name for tool in tools]}")
    return tools
