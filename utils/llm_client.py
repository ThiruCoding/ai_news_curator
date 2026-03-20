import ollama

def get_llm_summary(prompt):
    """
    Executes local inference using Ollama.
    Optimized for Llama 3.2 1B to ensure speed on 8GB RAM/CPU.
    """
    try:
        # We use the 1B model for faster CPU processing
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0,      # Keeps it factual (no hallucination)
                'num_ctx': 4096,       # Limits context to prevent RAM overflow
                'num_thread': 4        # Optimized for standard CPU core counts
            }
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"[OLLAMA ERROR] Ensure the Ollama app is running: {str(e)}"