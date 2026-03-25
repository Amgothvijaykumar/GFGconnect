"""
Processing Module
Handles AI-powered content rewriting for GFG Connect posts.
Supports multiple AI providers: Groq (primary, fast+free) and Gemini (fallback).
"""

import os
import time
import re


# API key env variable names
GROQ_API_KEY_ENV = "GROQ_API_KEY"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"

# System prompt for consistent post formatting
SYSTEM_PROMPT = """You are an expert social media post writer for GeeksforGeeks Connect — 
a professional learning community for developers and students.

Your job is to take raw, unstructured learning notes and rewrite them into 
an engaging, professional post that's ready to publish.

Rules:
- Keep it concise: 3-5 short paragraphs MAX
- Prefer point-wise, skimmable lines over long paragraphs for better readability
- Use proper grammar and professional tone
- Add relevant emojis (but don't overdo it — 1-2 per paragraph max)
- Structure: Start with a hook → What was learned → Key takeaway
- Tone: Enthusiastic but professional, like talking to peer developers
- Add relevant hashtags at the end (3-5 max)
- Do NOT use markdown formatting (no **, no ##, no bullet points with *)
- Write in first person
- Make it feel authentic, not AI-generated
- Keep total length under 1000 characters"""

USER_PROMPT = """Rewrite the following raw learning notes into a polished 
GeeksforGeeks Connect post:

---
{raw_text}
---

Generate ONLY the post content, nothing else. No explanations or meta-text."""


def _get_env_file():
    """Get path to .env file."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


def _load_key_from_env(key_name):
    """Load an API key from environment or .env file."""
    # Check environment variable first
    val = os.environ.get(key_name)
    if val:
        return val

    # Check .env file
    env_file = _get_env_file()
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key_name}="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    return None


def _save_key_to_env(key_name, key_value):
    """Save an API key to .env file."""
    env_file = _get_env_file()
    with open(env_file, "a") as f:
        f.write(f"\n{key_name}={key_value}\n")


def _get_or_prompt_key(key_name, service_name, signup_url):
    """Get API key from env, or prompt user."""
    key = _load_key_from_env(key_name)
    if key:
        return key

    print(f"\n🔑 {service_name} API Key Required (free)")
    print(f"   Get yours at: {signup_url}")
    print("   (Completely FREE — no credit card needed)\n")

    key = input("   Paste your API key: ").strip()
    if not key:
        return None

    save = input("   💾 Save for future use? (yes/no): ").strip().lower()
    if save in ("yes", "y"):
        _save_key_to_env(key_name, key)
        print("   ✅ Saved to .env file.")

    return key


# ============================================================
# GROQ (Primary) - Fast & Free
# ============================================================

def _rewrite_with_groq(raw_text):
    """
    Rewrite using Groq API (Llama model — fast & free).
    Free tier: 30 RPM, 14400 RPD, 131072 tokens/min.
    """
    try:
        from groq import Groq
    except ImportError:
        print("   ⚠️  Groq package not installed.")
        return None

    api_key = _get_or_prompt_key(
        GROQ_API_KEY_ENV,
        "Groq",
        "https://console.groq.com/keys"
    )
    if not api_key:
        return None

    try:
        print("\n   🤖 Rewriting with AI (Groq/Llama — fast)...")

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT.format(raw_text=raw_text)},
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        if response and response.choices:
            result = response.choices[0].message.content.strip()
            result = clean_post(result)
            print("   ✅ AI rewrite complete! (via Groq)")
            return result

        print("   ❌ Empty response from Groq.")
        return None

    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            print("   ⏳ Groq rate limited. Will try Gemini...")
        else:
            print(f"   ❌ Groq error: {e}")
        return None


# ============================================================
# GEMINI (Fallback)
# ============================================================

def _rewrite_with_gemini(raw_text):
    """
    Rewrite using Google Gemini API (fallback).
    Includes retry logic for rate limits.
    """
    try:
        from google import genai
    except ImportError:
        print("   ⚠️  Google GenAI package not installed.")
        return None

    api_key = _load_key_from_env(GEMINI_API_KEY_ENV)
    if not api_key:
        # Don't prompt if we already tried Groq — just skip
        return None

    models = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]
    client = genai.Client(api_key=api_key)

    for model in models:
        for attempt in range(2):  # 2 attempts per model
            try:
                print(f"\n   🤖 Trying Gemini ({model})...")

                response = client.models.generate_content(
                    model=model,
                    contents=USER_PROMPT.format(raw_text=raw_text),
                    config={
                        "system_instruction": SYSTEM_PROMPT,
                        "temperature": 0.7,
                        "max_output_tokens": 1024,
                    },
                )

                if response and response.text:
                    result = response.text.strip()
                    result = clean_post(result)
                    print("   ✅ AI rewrite complete! (via Gemini)")
                    return result

            except Exception as e:
                if "429" in str(e):
                    retry_delay = _extract_retry_delay(str(e))
                    if attempt == 0 and retry_delay <= 30:
                        print(f"   ⏳ Waiting {int(retry_delay)}s...")
                        time.sleep(retry_delay)
                        continue
                    break  # Try next model
                else:
                    print(f"   ❌ Gemini error: {e}")
                    return None

    return None


# ============================================================
# Main entry point
# ============================================================

def rewrite_with_ai(raw_text):
    """
    Rewrite raw text into a polished GFG Connect post.
    Tries Groq first (fast+free), falls back to Gemini.

    Args:
        raw_text: The raw text from voice/manual input

    Returns:
        str: The AI-rewritten post content, or None if all providers fail
    """
    # Try Groq first (fast, reliable free tier)
    result = _rewrite_with_groq(raw_text)
    if result:
        return result

    # Fallback to Gemini
    print("\n   🔄 Trying Gemini as fallback...")
    result = _rewrite_with_gemini(raw_text)
    if result:
        return result

    print("\n   ❌ All AI providers failed.")
    return None


def _extract_retry_delay(error_msg):
    """Extract retry delay from error message."""
    match = re.search(r"retry in (\d+\.?\d*)s", str(error_msg))
    if match:
        return float(match.group(1))
    return 30


def clean_post(content):
    """Clean up AI-generated post content."""
    if not content:
        return None

    content = content.strip()

    # Remove wrapping quotes
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]

    # Remove markdown code blocks
    if content.startswith("```") and content.endswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1]).strip()

    # Remove markdown formatting
    content = content.replace("**", "")
    content = content.replace("##", "")
    content = content.replace("# ", "")

    return content.strip()
