# Temporal Health Pattern Detection

This system analyzes multi-user conversational health data to detect hidden causal patterns over time. 
It identifies relationships between habits and symptoms using temporal reasoning and outputs structured explanations with confidence scores.

## Architecture

* `data_loader.py`: Loads the JSON dataset.
* `preprocessor.py`: Sorts conversations and extracts relevant tags as events.
* `timeline_builder.py`: Converts conversations into a sequence of events.
* `pattern_engine.py`: Analyzes the sequence using an LLM (OpenRouter `gpt-4o-mini`) and outputs structured reasoning.
* `ui.py`: A premium **Chat-Streaming Companion** interface (Clary) that allows for conversational analysis, individual user data insertion (via file upload or manual paste), and streamed reasoning results.
* `main.py`: Entry point for CLI processing or launching the UI.

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
You can run the analysis directly from the terminal. The script will look for `askfirst_synthetic_dataset.json` in the current directory or the `Downloads` folder, process all users, and save the results to `results.json`.

```bash
python main.py
```

### User Interface (Streamlit UI)
To launch the interactive dashboard, run:

```bash
python main.py ui
# Or alternatively:
streamlit run ui.py
```
This will open a browser window where you can upload the dataset or analyze the default one automatically, viewing formatted patterns per user.
