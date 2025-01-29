import os
import shutil
import re

# Define the base directory where the agent files are located
BASE_DIR = "/home/daniel/Git/llm-assistants-web-library/agent-configs"

# Mapping of folder names
folder_names = {
    'Writing & Content',
    'Career & Professional',
    'Research & Analysis',
    'Project & Task Management',
    'AI & Development',
    'Technical & Engineering',
    'Personal & Lifestyle',
    'Shopping & Product',
    'Conversational & Creative',
    'Safety & Preparedness'
}


def create_folders(folders):
    """Creates the specified folders if they don't already exist within the BASE_DIR."""
    for folder in folders:
        folder_path = os.path.join(BASE_DIR, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")


def classify_file(filename, folders):
    """
    Classifies the file based on its name using keywords and patterns.
    Returns the name of the matching folder or None if no match found.
    """
    filename = filename.lower()

    if any(keyword in filename for keyword in ["email", "text", "script", "sonnet", "narratives", "bluf", "brief", "tldr", "medieval"]):
        return 'Writing & Content'
    elif any(keyword in filename for keyword in ["career", "job", "resume", "salary", "quiet-quitting", "performance", "go-sell-yourself"]):
      return 'Career & Professional'
    elif any(keyword in filename for keyword in ["company", "research", "report", "stat", "sustainability", "regulation", "monitoring", "open-data", "landscape", "backgrounder", "context", "ghg"]):
      return 'Research & Analysis'
    elif any(keyword in filename for keyword in ["agenda", "automate", "backup", "task", "schedule", "meeting", "minutes", "workflow", "keep-me-on-time"]):
       return 'Project & Task Management'
    elif any(keyword in filename for keyword in ["config", "gpt", "prompt", "llm", "code", "python", "assistant"]):
      return 'AI & Development'
    elif any(keyword in filename for keyword in ["docker", "data", "database", "mongodb", "mysql", "neo4j", "postgres", "schema", "sql", "sqlite", "stack", "hardware", "tech-spec"]):
        return 'Technical & Engineering'
    elif any(keyword in filename for keyword in ["declutter", "daniel", "gifted-adult", "personal", "travel", "forager", "wine-buff", "sunrise-riser", "remember"]):
        return 'Personal & Lifestyle'
    elif any(keyword in filename for keyword in ["aliexpress", "product", "ikea", "israel", "microphone", "ruggedized", "shopping", "self-hosted"]):
      return 'Shopping & Product'
    elif any(keyword in filename for keyword in ["chatmate", "cipher", "conspiracy", "grumpy", "lousy-pun", "musical", "shakespeare", "sloth", "social-awkwardness", "mimic", "dogmatic", "olde"]):
        return 'Conversational & Creative'
    elif any(keyword in filename for keyword in ["disaster", "emergency", "threat", "preparedness", "safety", "shelter"]):
        return 'Safety & Preparedness'

    return None


def move_files(folders):
    """Moves files to their respective folders based on classification."""
    for filename in os.listdir(BASE_DIR):
      if filename.endswith(".md"):
        source_path = os.path.join(BASE_DIR, filename)
        classification = classify_file(filename, folders)
        if classification:
            try:
                dest_path = os.path.join(BASE_DIR, classification, filename)
                shutil.move(source_path, dest_path)
                print(f"Moved {filename} to {classification}")
            except FileNotFoundError:
                print(f"File not found: {source_path}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            print(f"Skipped {filename}: could not be classified.")


if __name__ == "__main__":
    create_folders(folder_names)
    move_files(folder_names)
    print("File organization complete.")