import urllib.request
import urllib.error
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def generate_llm_response(prompt: str) -> str:
    """
    Sends a prompt to the Groq chat completions API and returns the generated content.
    Uses Python's built-in urllib to avoid external dependencies.
    """
    if not GROQ_API_KEY:
        print("[WARNING] GROQ_API_KEY is not set in .env. Returning warning message.")
        return "Chatbot API Key is missing. Please configure GROQ_API_KEY in your .env file."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }


    data = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        # Use a 15-second timeout to avoid locking the request threads
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = response.read().decode("utf-8")
            res_data = json.loads(res_body)
            return res_data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        try:
            error_msg = e.read().decode("utf-8")
        except Exception:
            error_msg = e.reason
        print(f"[HTTP Error calling Groq API]: status={e.code}, body={error_msg}")
        return f"Unable to reach Groq LLM (HTTP status {e.code}). Please try again later."
    except Exception as e:
        print(f"[Error calling Groq API]: {str(e)}")
        return "Sorry, I ran into an error communicating with the LLM. Please try again later."
