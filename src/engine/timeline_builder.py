from datetime import datetime
from src.processing.preprocessor import sort_conversations, extract_events

def build_timeline(user_data: dict) -> list:
    """
    For a user, convert sorted conversations into a temporal sequence like:
    [
      "Jan 8: started low calorie diet",
      "Feb 10: fatigue",
      "Feb 19: hair fall",
      "Mar 18: recovery"
    ]
    """
    user_data = sort_conversations(user_data)
    timeline = []
    
    for conv in user_data.get("conversations", []):
        ts_str = conv.get("timestamp")
        try:
            dt = datetime.fromisoformat(ts_str)
        except ValueError:
            dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
            
        date_str = dt.strftime("%b %d").replace(" 0", " ")
        
        session_id = conv.get("session_id", "")
        tags = extract_events(conv)
        if tags:
            event_str = f"[{session_id}] {date_str}: " + ", ".join(tags)
            timeline.append(event_str)
            
    return timeline
