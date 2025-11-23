import os
import json
from datetime import datetime

CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

def get_chat_list():
    """Returns a dictionary of {filename: title}."""
    chats = {}
    try:
        files = [f for f in os.listdir(CHAT_DIR) if f.endswith(".json")]
    except FileNotFoundError:
        return {}
        
    for f in sorted(files, reverse=True): # Show newest first
        path = os.path.join(CHAT_DIR, f)
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                # Use .get() for safety, fallback to filename
                title = data.get("title", f.replace('.json', '').replace('_', ' '))
                chats[f] = title
        except Exception:
            chats[f] = f # Fallback if file is corrupt
    return chats

def create_chat(title="New Chat"):
    """Creates a new, empty chat file with a title."""
    filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join(CHAT_DIR, filename)

    initial_chat = {
        "title": title,
        "messages": [
            {"role": "assistant", "content": "Hello! I’m your Groq-powered AI assistant."}
        ]
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(initial_chat, f, indent=4)
    return filename

def load_chat(filename):
    """Loads a chat file and returns (title, messages)."""
    path = os.path.join(CHAT_DIR, filename)
    if not os.path.exists(path):
        return "New Chat", [] # Return defaults

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Handle both old format (list) and new format (dict)
            if isinstance(data, list):
                # Legacy support for old chat files
                return filename.replace(".json", ""), data 
            
            title = data.get("title", "Untitled Chat")
            messages = data.get("messages", [])
            return title, messages
    except Exception:
        return "Error Loading Chat", []

def save_chat(filename, messages, title=None):
    """Saves the chat messages and (optionally) a new title."""
    path = os.path.join(CHAT_DIR, filename)
    
    # Load existing data first to preserve title if not provided
    chat_data = {"title": "Chat", "messages": []}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
                if not isinstance(chat_data, dict):
                    # Convert legacy list to new dict format
                    chat_data = {"title": "Legacy Chat", "messages": chat_data}
        except Exception:
            pass # File might be empty/corrupt, will overwrite

    # Update data
    chat_data["messages"] = messages
    if title:
        chat_data["title"] = title

    # Save the updated data
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=4)

def delete_chat(filename):
    """Deletes a chat file."""
    path = os.path.join(CHAT_DIR, filename)
    if os.path.exists(path):
        os.remove(path)