import json
import os
from core.logger import get_logger

# Give the Memory Vault a voice in the logs
logger = get_logger("MemoryVault")

class MemoryVault:
    """JARVIS's long-term storage drive."""
    
    def __init__(self):
        # We will store his memories right in the main project folder
        self.filepath = "memory.json"
        self.memory = self._load_memory()
        logger.info("Memory Vault initialized. Long-term storage is online.")

    def _load_memory(self) -> dict:
        """Loads the JSON file. If it doesn't exist, creates a blank memory template."""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as file:
                return json.load(file)
        
        # This is his default "blank" brain
        return {
            "boss_name": "Boss",
            "facts": []
        }

    def _save_memory(self):
        """Silently saves the current memory dictionary back to the JSON file."""
        with open(self.filepath, 'w') as file:
            # indent=4 makes the file easily readable for humans in VS Code
            json.dump(self.memory, file, indent=4)

    def remember_fact(self, fact: str) -> str:
        """Saves a new fact to the permanent array."""
        logger.info(f"Saving to permanent storage: '{fact}'")
        self.memory["facts"].append(fact)
        self._save_memory()
        return "I have securely committed that to my permanent memory."

    def recall_facts(self) -> str:
        """Retrieves everything he knows."""
        logger.info("Accessing permanent storage...")
        if not self.memory["facts"]:
            return "My memory vault is currently empty."
            
        # Glues all the facts together into one paragraph
        all_facts = ". ".join(self.memory["facts"])
        return f"Here is what I remember: {all_facts}."

# Test the Memory Vault directly!
if __name__ == "__main__":
    vault = MemoryVault()
    print("\n🧠 Testing the Memory Vault...\n")
    
    # Let's teach him something permanent!
    print(vault.remember_fact("My name is Kanna."))
    print(vault.remember_fact("I am working on a major Python AI project."))
    
    # Let's see if he remembers it
    print(f"\nJARVIS: {vault.recall_facts()}\n")