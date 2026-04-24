# AI Intern Assignment Writeup

## 1. Approach to the Reasoning Problem
The core challenge was to construct a robust reasoning layer capable of detecting temporal connections across messy, unstructured, cross-conversational data without hallucinating or merely acting as a keyword retriever. My approach was split into a deterministic preprocessing layer and an LLM-based pattern engine:
1. **Deterministic Timeline Construction (`timeline_builder.py`)**: Before querying the LLM, I sorted conversations temporally and abstracted them down to essential events linked to exact dates and Session IDs. This stripped away conversational noise while keeping the causal sequence perfectly intact.
2. **Constrained Prompting (`pattern_engine.py`)**: I utilized `openai/gpt-4o-mini` (via OpenRouter) as the reasoning engine. The system prompt enforces strict rules: 
   - Patterns must *strictly* flow from Cause to Effect.
   - Exact timestamps and Session IDs must be cited to prove non-coincidence and justify confidence.
   - External medical jargon (e.g., cortisol, melatonin) is strictly banned to ensure all conclusions are drawn *solely* from the provided data.
   - The LLM is directed to actively scan for delayed patterns (e.g., a 6-week lag between calorie restriction and hair fall), dose-response relationships (small vs. large dairy intake), and cascading chains (screens -> sleep deprivation -> anxiety).

By anchoring the LLM prompt to explicit temporal definitions (immediate vs delayed) and strict evidence citation (Session IDs), I shifted the LLM from loosely associating keywords to executing logical, timeline-bound pattern recognition.

## 2. Failures, Hallucinations, and Future Improvements
### Where the System Fails or Confidently Hallucinates
During development, the system exhibited several confident failure modes:
* **Over-associative Hallucinations**: It occasionally linked unrelated causes, such as confidently linking dairy intake directly to hair fall instead of isolating the dietary calorie deficit.
* **External Medical Hallucinations**: Because LLMs are trained on vast medical data, it initially reasoned using external concepts (e.g., assuming stress caused a "cortisol surge" leading to cramps, or that dairy caused "inflammation"). While technically medically plausible, it was a hallucination within the context of the explicit dataset.
* **Time-Lag Misinterpretation**: It struggled to differentiate between the *gap between repeated occurrences* versus the *gap between a cause and an effect*, occasionally predicting that an effect took weeks to occur when it actually happened the same night (e.g., late-night eating).
* **Missing Cascading Roots**: It sometimes analyzed symptoms in isolation (e.g., Anxiety -> Cramps) rather than tracing the root lifestyle cause (Late Night Screens -> Sleep Deprivation -> Anxiety -> Cramps).

### What I Would Build Differently With More Time
If given more time, I would rebuild the system using an agentic or multi-step graph approach rather than relying on a single zero-shot LLM pass:
1. **Multi-Agent Evaluation**: I would implement a two-step LLM pipeline: an *Extractor Agent* to propose causal links and a *Critic Agent* to rigorously verify the temporal constraints of each proposed link against the raw timeline.
2. **Graph-Based Event Representation**: Instead of feeding the LLM a flat text timeline, I would construct a Knowledge Graph embedding temporal distances as edge weights. This would allow deterministic algorithms to identify clusters and cascading chains (e.g., A -> B -> C) before the LLM generates the human-readable reasoning.
3. **Dynamic Few-Shot Prompting**: I would implement dynamic context management to inject similar past resolved cases into the prompt as few-shot examples, improving the LLM's understanding of delayed symptoms versus immediate dose-response reactions.
