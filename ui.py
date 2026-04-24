import streamlit as st
import json
import os
import time
from data_loader import load_dataset, get_users
from timeline_builder import build_timeline
from pattern_engine import detect_patterns, identify_intent, general_chat

# 1. Page Configuration & Setup
st.set_page_config(page_title="Clary - Health Pattern AI", page_icon="🤖", layout="centered")

# Custom Dark Mode Styling
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stChatMessage { background-color: #1E2127; border-radius: 10px; margin-bottom: 10px; }
    .stChatInputContainer { padding-bottom: 20px; }
    hr { margin: 1rem 0; border: 0; border-top: 1px solid #444; }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar - User Selection
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # Requirement: User must be able to upload data
    uploaded_file = st.file_uploader("📂 Upload Health Dataset (JSON)", type=["json"])
    
    # Fallback/Default path
    default_path = "askfirst_synthetic_dataset.json"
    dataset = None
    
    if uploaded_file is not None:
        dataset = json.load(uploaded_file)
        st.success("Custom dataset uploaded!")
    elif os.path.exists(default_path):
        with open(default_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        st.info("Using default dataset.")
            
    if dataset:
        users = get_users(dataset)
        user_ids = [u.get("user_id") for u in users]
        selected_user_id = st.selectbox("👤 Select User to Analyze", user_ids)
    else:
        st.error("Please upload a dataset to begin.")
        selected_user_id = None

    st.divider()
    if st.button("🗑️ Reset Conversation"):
        st.session_state.messages = []
        st.rerun()

# 3. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display Existing Messages
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. Chat Interaction Helper
def stream_response(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

if prompt := st.chat_input("Ask me to analyze your health patterns"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # AI Process & Response
    with st.chat_message("assistant", avatar="🤖"):
        # Process intent
        intent = identify_intent(prompt)
        
        # If intent is CHAT, use general chat
        if intent == "CHAT":
            with st.spinner("💭 ..."):
                chat_context = st.session_state.messages
                response = general_chat(chat_context)
            
            full_response = st.write_stream(stream_response(response))
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        elif not selected_user_id:
            st.error("Please select a user profile in the sidebar first.")
        else:
            # A. Find user data
            user_data = next(u for u in users if u["user_id"] == selected_user_id)
            
            # B. Display Temporal History
            st.write("### 📅 Temporal History")
            timeline = build_timeline(user_data)
            timeline_display = ""
            for entry in timeline:
                timeline_display += entry.replace(": ", " → ") + "\n"
            st.code(timeline_display, language="text")
            
            # C. Detect Patterns with a temporary spinner
            with st.spinner(f"🔍 Analyzing {selected_user_id}'s timeline..."):
                result = detect_patterns(selected_user_id, timeline)
                patterns = result.get("patterns", [])

            # D. Format Final Response
            intro = f"I have analyzed the temporal data for **{selected_user_id}**. Here are the causal patterns I identified:\n\n"
            if not patterns:
                full_text = intro + "No significant temporal patterns were detected."
            else:
                full_text = intro
                for p in patterns:
                    conf = p.get('confidence', 'low').upper()
                    full_text += f"#### 🔍 Pattern: {p.get('pattern')}\n"
                    full_text += f"**Confidence:** {conf}\n\n"
                    full_text += f"**Reasoning:** {p.get('reason')}\n"
                    full_text += "\n---\n\n"

            # E. Professional Streaming Output
            full_response = st.write_stream(stream_response(full_text))
            
            # Save assistant message
            st.session_state.messages.append({"role": "assistant", "content": full_response})
