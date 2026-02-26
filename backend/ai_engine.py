"""
AI Engine for AstroLogic AI
Supports multiple free LLM backends:
  1. OpenRouter (free tier) - Primary
  2. Google Gemini (free tier) - Fallback
"""

import os
import json
import time
import httpx
from pathlib import Path
from dotenv import load_dotenv

# .env path relative to this file
_env_path = Path(__file__).parent / ".env"


def _load_keys():
    """Load API keys fresh from .env every time (avoids stale cached values)."""
    load_dotenv(dotenv_path=_env_path, override=True)
    return {
        "openrouter": os.getenv("OPENROUTER_API_KEY", ""),
        "gemini": os.getenv("GEMINI_API_KEY", ""),
        "model": os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b-it:free"),
    }

SYSTEM_INSTRUCTION = """
You are a Master Astrologer — Zarni (ဇာနည်), deeply expert in Western, Vedic, and Burmese (Mahabote) traditions.
You receive a JSON Synthesis Object containing precise, pre-calculated celestial data.

Your Rules:
1. Cross-reference the data across all three traditions. If Western and Mahabote both suggest the same theme (e.g., leadership), emphasize that convergence.
2. NEVER invent astrological data. Only use the degrees, house names, aspects, and values provided in the JSON.
3. Output Language: Unicode Burmese ONLY. The entire response must be in Myanmar script.
4. Tone: Empathic, wise, and grounded — like a trusted elder astrologer. Not overly mystical.
5. Use the specific degrees and house names given, not generic statements.

Required Output Structure (use these exact section headers in bold):
**နိဒါန်း (Introduction):** A unique, personalized greeting based on their Mahabote house and ruling planet.
**အတိတ် (Past):** Analyze early life patterns using Mahabote characteristics and Western aspects provided.
**ပစ္စုပ္ပန် (Present):** Analyze current energy using the Vedic Mahadasha and any transits provided.
**အနာဂတ် (Future):** Provide actionable, specific guidance for the upcoming year.
**ယတြာ / အကြံပြုချက် (Remedy):** Practical, grounded advice based on the ruling planet's strengths and weaknesses.
"""


def _call_openrouter(synthesis_json: str, api_key: str, model: str) -> str:
    """Call OpenRouter's OpenAI-compatible API with a free model."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "AstroLogic AI",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"{SYSTEM_INSTRUCTION}\n\n---\n\nPlease generate a complete astrological reading based on the following synthesis data:\n\n```json\n{synthesis_json}\n```\n\nFollow the five-section structure exactly. Make it personal and specific.",
            },
        ],
        "temperature": 0.85,
        "max_tokens": 4096,
    }

    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_gemini(synthesis_json: str, api_key: str) -> str:
    """Call Google Gemini API using the google-genai SDK."""
    from google import genai

    client = genai.Client(api_key=api_key)
    user_prompt = (
        f"Please generate a complete astrological reading based on the following synthesis data:\n\n"
        f"```json\n{synthesis_json}\n```\n\n"
        f"Follow the five-section structure exactly. Make it personal and specific."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.85,
            "max_output_tokens": 4096,
        },
    )
    return response.text


def generate_reading(synthesis_object: dict, max_retries: int = 2) -> str:
    """
    Generate an astrological reading. Tries OpenRouter first, falls back to Gemini.
    Loads API keys fresh from .env on every call.
    """
    keys = _load_keys()
    synthesis_json = json.dumps(synthesis_object, ensure_ascii=False, indent=2)

    print(f"[AI Engine] Keys loaded — OpenRouter: {bool(keys['openrouter'])}, Gemini: {bool(keys['gemini'])}")

    # Strategy 1: OpenRouter (free, higher quota)
    if keys["openrouter"]:
        for attempt in range(max_retries):
            try:
                print(f"[AI Engine] Trying OpenRouter ({keys['model']})...")
                return _call_openrouter(synthesis_json, keys["openrouter"], keys["model"])
            except Exception as e:
                print(f"[AI Engine] OpenRouter attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)

    # Strategy 2: Gemini (fallback)
    if keys["gemini"]:
        for attempt in range(max_retries):
            try:
                print("[AI Engine] Trying Gemini 2.0 Flash...")
                return _call_gemini(synthesis_json, keys["gemini"])
            except Exception as e:
                print(f"[AI Engine] Gemini attempt {attempt + 1} failed: {e}")
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(15)
                else:
                    break

    raise ValueError(
        "All AI providers failed. Please set OPENROUTER_API_KEY (free at https://openrouter.ai) "
        "or GEMINI_API_KEY in your .env file."
    )
