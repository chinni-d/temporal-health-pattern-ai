import streamlit as st
import json
import os
import traceback
from data_loader import load_dataset, get_users
from timeline_builder import build_timeline
from pattern_engine import analyze_all_users

st.set_page_config(page_title="Temporal Health Pattern Detection", layout="wide")

st.title("Temporal Health Pattern Detection")
st.write("Analyze conversational health data to detect hidden cause-effect patterns.")

uploaded_file = st.file_uploader("Upload dataset (JSON)", type=["json"])
default_file_path = "askfirst_synthetic_dataset.json"
download_path = r"c:\Users\darap\Downloads\askfirst_synthetic_dataset.json"

dataset = None
if uploaded_file is not None:
    dataset = json.load(uploaded_file)
elif os.path.exists(default_file_path):
    st.info(f"Using default dataset: {default_file_path}")
    with open(default_file_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
elif os.path.exists(download_path):
    st.info("Using default dataset from Downloads.")
    with open(download_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
else:
    st.warning("Please upload a dataset or place 'askfirst_synthetic_dataset.json' in the working directory.")

if dataset and st.button("Analyze"):
    with st.spinner("Analyzing users... This may take a moment."):
        users = get_users(dataset)
        try:
            results = analyze_all_users(users, build_timeline)
            st.success("Analysis Complete!")
            
            # Display results
            results_list = results.get("results", [])
            if not results_list:
                st.warning("No patterns detected.")
            
            for user_result in results_list:
                st.subheader(f"User: {user_result.get('user_id')}")
                
                patterns = user_result.get("patterns", [])
                if not patterns:
                    st.write("No specific patterns identified for this user.")
                
                for pattern in patterns:
                    confidence = str(pattern.get("confidence", "low")).lower()
                    color = "green" if confidence == "high" else "orange" if confidence == "medium" else "red"
                    
                    st.markdown(f"**Pattern:** {pattern.get('pattern')}")
                    st.markdown(f"**Confidence:** :{color}[{confidence.capitalize()}]")
                    st.markdown(f"**Reasoning:** {pattern.get('reason')}")
                    st.divider()
                    
            st.subheader("Raw Output")
            st.json(results)
            
            # Add download button
            json_string = json.dumps(results, indent=2)
            st.download_button(
                label="Download Results JSON",
                file_name="results.json",
                mime="application/json",
                data=json_string,
            )
            
        except Exception as e:
            st.error(f"Error during analysis: {e}")
            st.code(traceback.format_exc())
