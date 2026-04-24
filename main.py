import sys
import json
import os
from src.processing.data_loader import load_dataset, get_users
from src.engine.timeline_builder import build_timeline
from src.engine.pattern_engine import analyze_all_users

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "ui":
        os.system("streamlit run ui/app.py")
        return
        
    dataset_path = "data/askfirst_synthetic_dataset.json"
    download_path = r"c:\Users\darap\Downloads\askfirst_synthetic_dataset.json"
    
    path_to_use = None
    if os.path.exists(dataset_path):
        path_to_use = dataset_path
    elif os.path.exists(download_path):
        path_to_use = download_path
    else:
        print("Dataset not found. Please place 'askfirst_synthetic_dataset.json' in the current directory.")
        return

    print(f"Loading dataset from {path_to_use}...")
    dataset = load_dataset(path_to_use)
    users = get_users(dataset)
    
    print(f"Found {len(users)} users. Analyzing (this might take a while if using local LLM)...")
    results = analyze_all_users(users, build_timeline)
    
    print("\n--- RESULTS ---")
    print(json.dumps(results, indent=2))
    
    with open("data/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to data/results.json")

if __name__ == "__main__":
    main()
