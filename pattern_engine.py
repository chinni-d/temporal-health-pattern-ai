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
