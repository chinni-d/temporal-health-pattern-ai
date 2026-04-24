# Temporal Health Pattern Detection

This system analyzes multi-user conversational health data to detect hidden causal patterns over time. 
It identifies relationships between habits and symptoms using temporal reasoning and outputs structured explanations with confidence scores.

## Architecture

* `data_loader.py`: Loads the JSON dataset.
* `preprocessor.py`: Sorts conversations and extracts relevant tags as events.
* `timeline_builder.py`: Converts conversations into a sequence of events.
* `pattern_engine.py`: Analyzes the sequence using an LLM (OpenRouter `gpt-4o-mini`) and outputs structured reasoning.
* `ui.py`: Streamlit-based web interface to upload datasets and view insights.
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
