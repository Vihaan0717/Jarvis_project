import os
import subprocess
import shutil
from core.logger import get_logger

logger = get_logger("ProjectTools")

class ProjectTools:
    """
    Tools for managing projects: Create, Delete, and Open in IDE.
    """
    
    @staticmethod
    def create_project(name: str, base_path: str = ".") -> str:
        project_dir = os.path.join(base_path, name)
        try:
            if os.path.exists(project_dir):
                return f"Error: Project '{name}' already exists."
            
            os.makedirs(project_dir)
            # Create a basic structure
            with open(os.path.join(project_dir, "main.py"), "w") as f:
                f.write("# Project: " + name + "\n\ndef main():\n    print('Hello from " + name + "')\n\nif __name__ == '__main__':\n    main()\n")
            
            # Initialize git if available
            try:
                subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
            except:
                pass
                
            logger.info(f"Project created: {name}")
            return f"Successfully created project '{name}' at {project_dir}."
        except Exception as e:
            logger.error(f"Failed to create project {name}: {e}")
            return f"Failed to create project: {str(e)}"

    @staticmethod
    def delete_project(name: str, base_path: str = ".") -> str:
        project_dir = os.path.join(base_path, name)
        try:
            if not os.path.exists(project_dir):
                return f"Error: Project '{name}' does not exist."
            
            # Use shutil.rmtree for recursive deletion
            shutil.rmtree(project_dir)
            logger.info(f"Project deleted: {name}")
            return f"Successfully deleted project '{name}'."
        except Exception as e:
            logger.error(f"Failed to delete project {name}: {e}")
            return f"Failed to delete project: {str(e)}"

    @staticmethod
    def open_ide(path: str) -> str:
        try:
            # Try to open VS Code (code)
            if os.path.exists(path):
                subprocess.run(["code", path], shell=True)
                return f"Opening IDE at {path}."
            else:
                return f"Error: Path {path} does not exist."
        except Exception as e:
            logger.error(f"Failed to open IDE: {e}")
            return f"Failed to open IDE. Make sure 'code' is in your PATH."
