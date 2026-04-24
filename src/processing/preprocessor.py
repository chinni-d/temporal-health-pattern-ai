from datetime import datetime

def sort_conversations(user_data: dict) -> dict:
    """Sort conversations by timestamp."""
    conversations = user_data.get("conversations", [])
    
    def parse_time(ts):
        try:
            return datetime.fromisoformat(ts)
        except ValueError:
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
            
    sorted_convos = sorted(conversations, key=lambda x: parse_time(x["timestamp"]))
    user_data["conversations"] = sorted_convos
    return user_data

def extract_events(conversation: dict) -> list:
    """Extract tags and relevant info as events."""
    tags = conversation.get("tags", [])
    return tags
