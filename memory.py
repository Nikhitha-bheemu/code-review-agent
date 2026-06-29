import json
import os
from datetime import datetime

# Path to the storage JSON file
MEMORY_FILE = "fixes_memory.json"

# Saves a bug description and its associated fix code to the memory file.
def save_fix(bug_description: str, fix_code: str):
    """
    Saves a code fix along with its bug description and current timestamp to JSON storage.
    
    Parameters:
    - bug_description (str): Description of the bug.
    - fix_code (str): The correct code fix.
    """
    try:
        data = {}
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
        now_str = datetime.now().isoformat()
        data[bug_description] = {
            "fix": fix_code,
            "timestamp": now_str
        }
        
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
        print(f"[DEBUG] Fix successfully saved to memory for: '{bug_description}'")
    except Exception as e:
        print(f"[DEBUG] Error saving fix to memory: {e}")

# Recalls a similar fix code from memory based on matching words.
def recall_similar_fix(bug_description: str) -> str or None:
    """
    Searches stored bug fixes for a similar bug description based on word match count.
    
    Parameters:
    - bug_description (str): Description of the bug to search.
    
    Returns:
    - str or None: The stored fix code if at least 3 words match, otherwise None.
    """
    try:
        if not os.path.exists(MEMORY_FILE):
            return None
            
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        input_words = set(bug_description.lower().split())
        
        for stored_desc, value in data.items():
            stored_words = set(stored_desc.lower().split())
            matching_words = len(input_words.intersection(stored_words))
            
            if matching_words >= 3:
                print(f"[DEBUG] Similar fix found with {matching_words} matching words.")
                return value.get("fix")
                
        return None
    except Exception as e:
        print(f"[DEBUG] Error recalling fix: {e}")
        return None
