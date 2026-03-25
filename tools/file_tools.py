import os
from core.logger import get_logger

logger = get_logger("FileTools")

class FileTools:
    """
    Tools for file system operations.
    """
    @staticmethod
    def list_files(directory: str) -> str:
        try:
            files = os.listdir(directory)
            return f"Files in {directory}: " + ", ".join(files)
        except Exception as e:
            return f"Error listing files: {e}"

    @staticmethod
    def read_file(path: str) -> str:
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
