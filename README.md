# Temporal Health Pattern Detection

This system analyzes multi-user conversational health data to detect hidden causal patterns over time. 
It identifies relationships between habits and symptoms using temporal reasoning and outputs structured explanations with confidence scores.

## Folder Architecture

```text
temporal-health-pattern-ai/
├── data/                       # Datasets & Results
│   ├── askfirst_synthetic_dataset.json
│   └── results.json
├── src/                        # Core Logic Package
│   ├── __init__.py
│   ├── engine/                 # AI Detection Engines
│   │   ├── __init__.py
│   │   ├── pattern_engine.py
│   │   └── timeline_builder.py
│   ├── processing/             # Data Preprocessing
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   └── preprocessor.py
│   └── utils.py                # Utilities
├── ui/                         # User Interface
│   └── app.py                  # Streamlit App
├── main.py                     # Entry Point
├── .env                        # Private config
└── .gitignore
```

## Requirements

1. Install Python dependencies:
   ```bash
   pip install streamlit requests python-dotenv
   ```

2. Create a `.env` file in the root directory and add your OpenRouter API Key:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

## Technical Decisions (Assignment Requirements)

### LLM Choice and Why
I chose `gpt-4o-mini` (via OpenRouter) because temporal reasoning requires a high degree of instruction-following to avoid confusing event spacing (occurrences) with causal gaps (cause-effect latency). It handles structured JSON generation flawlessly and provides a deep enough context window to evaluate the timeline.

### Chunking and Context Management Strategy
Instead of blindly chunking tokens or using a vector database (which inherently loses chronological continuity), I implemented a **Deterministic Timeline Condensation Strategy**. 
The `timeline_builder.py` preprocesses the entire conversational history for a user, sorting it strictly by timestamp, and extracts only the explicit metadata tags and symptoms mapped to `Session IDs`. 
By doing this, the entire compressed chronological history of a single user easily fits within the context window of a single LLM call. The LLM receives the complete, noise-free timeline of one user at a time, ensuring it has 100% of the relevant past context necessary to spot delayed effects (like a 6-week hair fall lag) without exceeding token limits or losing information via embedding chunks.

### Reasoning Trace
The reasoning trace is made visible directly in the output (`results.json` and the Streamlit UI). I enforce this by having the LLM generate a `reason` field before finalizing confidence, compelling it to explicitly cite the `[Session IDs]` and `[Dates]`, evaluate the exact time gap, and rule out contradictions. This prevents the LLM from making leaps of logic and allows me to see exactly which events the system considered when forming a conclusion.

## Running the Application

### Command-Line Interface (CLI)
You can run the analysis directly from the terminal. The script will look for `data/askfirst_synthetic_dataset.json` in the current directory or the `Downloads` folder, process all users, and save the results to `data/results.json`.

```bash
python main.py
```

### User Interface (Streamlit UI)
To launch the interactive dashboard, run:

```bash
python main.py ui
# Or alternatively:
streamlit run ui/app.py
```
This will open a browser window where you can upload the dataset or analyze the default one automatically, viewing formatted patterns per user.
