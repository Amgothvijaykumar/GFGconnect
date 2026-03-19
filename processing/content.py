"""
Processing Module
Handles AI-powered content rewriting using Google Gemini (free).
Automatically converts raw learning notes into polished GFG Connect posts.
"""

import os
from google import genai


# Gemini API configuration
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_MODEL = "gemini-2.0-flash"


# System prompt for consistent post formatting
SYSTEM_PROMPT = """You are an expert social media post writer for GeeksforGeeks Connect — 
a professional learning community for developers and students.

Your job is to take raw, unstructured learning notes and rewrite them into 
an engaging, professional post that's ready to publish.

Rules:
- Keep it concise: 3-5 short paragraphs MAX
- Use proper grammar and professional tone
- Add relevant emojis (but don't overdo it — 1-2 per paragraph max)
- Structure: Start with a hook → What was learned → Key takeaway
- Tone: Enthusiastic but professional, like talking to peer developers
- Add relevant hashtags at the end (3-5 max)
- Do NOT use markdown formatting (no **, no ##, no bullet points with *)
- Write in first person
- Make it feel authentic, not AI-generated
- Keep total length under 1000 characters"""


def get_api_key():
    """
    Get Gemini API key from environment or prompt user.

    Returns:
        str: The API key, or None if not provided
    """
    api_key = os.environ.get(GEMINI_API_KEY_ENV)
    if api_key:
        return api_key

    # Check .env file in project root
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{GEMINI_API_KEY_ENV}="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if api_key:
                        return api_key

    # Prompt user for API key
    print("\n🔑 Gemini API Key Required (free)")
    print("   Get yours at: https://aistudio.google.com/apikey")
    print("   (It's completely FREE — no credit card needed)\n")

    api_key = input("   Paste your API key: ").strip()
    if not api_key:
        return None

    # Save to .env for next time
    save = input("   💾 Save key for future use? (yes/no): ").strip().lower()
    if save in ("yes", "y"):
        with open(env_file, "a") as f:
            f.write(f"\n{GEMINI_API_KEY_ENV}={api_key}\n")
        print("   ✅ Saved to .env file (git-ignored).")

    return api_key


def rewrite_with_ai(raw_text):
    """
    Rewrite raw text into a polished GFG Connect post using Gemini AI.

    Args:
        raw_text: The raw text from voice/manual input

    Returns:
        str: The AI-rewritten post content, or None if failed
    """
    api_key = get_api_key()
    if not api_key:
        print("   ❌ No API key provided. Cannot rewrite with AI.")
        return None

    try:
        print("\n   🤖 Rewriting with AI (Gemini)...")

        client = genai.Client(api_key=api_key)

        prompt = f"""Rewrite the following raw learning notes into a polished 
GeeksforGeeks Connect post:

---
{raw_text}
---

Generate ONLY the post content, nothing else. No explanations or meta-text."""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.7,
                "max_output_tokens": 1024,
            },
        )

        if response and response.text:
            result = response.text.strip()
            # Clean up common formatting artifacts
            result = clean_post(result)
            print("   ✅ AI rewrite complete!")
            return result
        else:
            print("   ❌ Empty response from AI.")
            return None

    except Exception as e:
        print(f"   ❌ AI rewrite failed: {e}")
        return None


def clean_post(content):
    """
    Clean up AI-generated post content.

    Args:
        content: Raw AI output

    Returns:
        str: Cleaned content ready for posting
    """
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

    # Remove markdown bold markers
    content = content.replace("**", "")
    content = content.replace("##", "")
    content = content.replace("# ", "")

    return content.strip()
