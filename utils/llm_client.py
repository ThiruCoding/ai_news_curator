import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_llm_summary(prompt, retries=3, wait=10):
    """
    Executes inference using Google Gemini API.
    Uses gemma-3-12b-it for free-tier summarization.
    Retries up to 3 times on transient errors before returning empty string.
    """
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemma-3-12b-it",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if attempt < retries - 1:
                print(f"  [RETRY {attempt + 1}/{retries}] Model unavailable, retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [FAILED] All retries exhausted: {error_str[:80]}")
                return ""