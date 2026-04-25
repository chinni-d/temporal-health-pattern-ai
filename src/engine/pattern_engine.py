import json
import requests
import re
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_api_key():
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return os.environ.get("OPENROUTER_API_KEY", "")

def detect_patterns(user_id: str, timeline: list) -> dict:
    """
    Use LLM to infer causal relationships and output JSON.
    """
    api_key = get_api_key()
    
    prompt = f"""Analyze the timeline and detect patterns.

STRICT RULES:
1. Always express patterns as: CAUSE -> EFFECT. Never reverse the direction. Cause must ALWAYS come before effect.
2. Time gap must describe when the effect happens after the cause.
3. You MUST detect delayed effects (weeks later, e.g. nutritional changes taking ~6 weeks to show symptoms).
4. Do NOT link unrelated causes. Look for dose-response relationships (e.g. small dose = no effect, large dose = effect).
5. Look for monthly cycles (e.g., events happening exactly in Week 2 of every month) combined with immediate correlations (e.g. same day stress).
6. Connect cascading chains! Show how one habit causes a domino effect across multiple symptoms (e.g. Habit -> Symptom 1 -> Symptom 2 -> Symptom 3).
7. Confidence rules STRICTLY:
   - HIGH: repeated multiple times AND strong temporal evidence
   - MEDIUM: limited repetition (1-2 times)
   - LOW: appears once or weak evidence. NEVER assign HIGH to single occurrence patterns.
8. Do NOT use terms like cortisol, melatonin, inflammation, blood sugar. Only use evidence directly present in the data.
9. Reason MUST include:
   - exact Session IDs (e.g. S01, S04) to prove non-coincidence
   - when effect happens (same day / after weeks)
   - repetition evidence
10. You MUST detect ALL major patterns in the timeline (typically 3-5 per user). Do NOT stop early.

Output strictly in JSON format:
{{
  "user_id": "{user_id}",
  "patterns": [
    {{
      "pattern": "CAUSE -> EFFECT",
      "confidence": "high/medium/low",
      "reason": "Observed in [N] sessions ([Session IDs, Dates]). [Explain sequence and exact time gap using only observed events. Detail any cascading chains or dose-responses.]"
    }}
  ]
}}

Timeline:
{json.dumps(timeline, indent=2)}
"""
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            },
            timeout=120
        )
        if response.status_code == 200:
            result_text = response.json()["choices"][0]["message"]["content"]
            
            # clean up output if the model added extra markdown
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                return {"user_id": user_id, "patterns": [{"pattern": "JSON Parse Error", "confidence": "low", "reason": "Model returned invalid JSON format."}]}
        else:
            return {"user_id": user_id, "patterns": [{"pattern": "API Error", "confidence": "low", "reason": f"Status code {response.status_code}: {response.text}"}]}
    except requests.exceptions.RequestException as e:
        return {"user_id": user_id, "patterns": [{"pattern": "Connection Error", "confidence": "low", "reason": f"Failed to connect to local Ollama instance: {str(e)}"}]}
    except Exception as e:
        return {"user_id": user_id, "patterns": [{"pattern": "Unexpected Error", "confidence": "low", "reason": str(e)}]}

def identify_intent(prompt: str) -> str:
    """
    Use LLM to identify if the user wants an analysis or just a general chat.
    Returns: 'ANALYZE' or 'CHAT'
    """
    p = prompt.lower().strip()
    # Lenient keyword matching to handle typos like 'amalyze'
    if any(word in p for word in ["analy", "pattern", "caus", "effect", "history"]):
        return "ANALYZE"
        
    api_key = get_api_key()
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a classifier. If the user mentions analysis, patterns, health, causes, or anything related to processing their history, output 'ANALYZE'. Otherwise output 'CHAT'. Even if they are vague or have typos (like 'amalyze'), if they want to start the process, output 'ANALYZE'."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=10
        )
        intent = response.json()["choices"][0]["message"]["content"].strip().upper()
        return "ANALYZE" if "ANALYZE" in intent else "CHAT"
    except Exception:
        return "CHAT"

def handle_general_chat(messages: list, user_data: dict = None) -> str:
    """
    Handle general conversational messages contextually.
    """
    api_key = get_api_key()
    
    user_context = ""
    if user_data:
        name = user_data.get('name', 'User')
        age = user_data.get('age', 'N/A')
        gender = user_data.get('gender', 'N/A')
        location = user_data.get('location', 'N/A')
        occupation = user_data.get('occupation', 'N/A')
        notes = user_data.get('onboarding_notes', '')
        
        # Include full conversation history for detailed queries
        full_history = []
        for conv in user_data.get('conversations', []):
            session_id = conv.get('session_id')
            user_msg = conv.get('user_message')
            followup = conv.get('user_followup', '')
            response = conv.get('clary_response', '')
            tags = ", ".join(conv.get('tags', []))
            
            session_text = f"Session {session_id} ({conv.get('timestamp')[:10]}):\n"
            session_text += f"- User: {user_msg}\n"
            if followup: session_text += f"- Follow-up: {followup}\n"
            session_text += f"- Clary: {response}\n"
            session_text += f"- Tags: {tags}\n"
            full_history.append(session_text)
        
        history_str = "\n".join(full_history)
        user_context = (
            f"You are talking to {name}. Profile: Age {age}, Gender {gender}, Location {location}, Occupation {occupation}. "
            f"Onboarding notes: {notes}. "
            f"Full Health History:\n{history_str}"
        )

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system", 
                        "content": f"You are Clary, a Health Pattern AI companion. {user_context} "
                                   "You help users understand causal links in their health history. "
                                   "If the user says 'Hi' or greets you, reply with 'Hi {name}' (replacing {name} with their actual name if known). "
                                   "Be concise, empathetic, and professional. You MUST be highly contextual: use the provided user profile, "
                                   "full health history, and current chat history to provide accurate and relevant answers. "
                                   "If the user asks to summarize a specific session (e.g., 'summarize session USR001_S07'), "
                                   "use the 'Full Health History' provided in the context to give a detailed summary of that specific session. "
                                   "If they ask about their general data or patterns, connect the dots across their entire history."
                    }
                ] + messages[-10:] # send last 10 messages for context
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "I'm having trouble connecting right now. How can I help you with your health analysis?"
    except Exception:
        return "I'm here to help with your health pattern analysis. What would you like to know?"

def analyze_all_users(users: list, timeline_builder_func) -> dict:
    all_results = []
    for user in users:
        user_id = user.get("user_id", "UNKNOWN")
        timeline = timeline_builder_func(user)
        result = detect_patterns(user_id, timeline)
        
        # Ensure correct structure
        if not isinstance(result, dict):
            result = {"user_id": user_id, "patterns": []}
        if "user_id" not in result:
            result["user_id"] = user_id
        if "patterns" not in result:
            result["patterns"] = []
            
        all_results.append(result)
        
    return {"results": all_results}
