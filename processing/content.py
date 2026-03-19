"""
Processing Module
Handles AI prompt generation and content formatting for GFG Connect posts.
"""


# Default prompt template for ChatGPT
PROMPT_TEMPLATE = """You are a helpful assistant that converts raw learning notes into a structured, 
professional post for GeeksforGeeks Connect.

Rules:
- Keep it concise (3-5 short paragraphs max)
- Use proper grammar and formatting
- Add relevant emojis for visual appeal
- Structure: Title → What I learned → Key takeaway
- Tone: Enthusiastic but professional
- Do NOT add hashtags unless the user mentions them

Raw learning notes:
{raw_text}

Generate a well-structured GFG Connect post:"""


PROMPT_TEMPLATE_SHORT = """Convert these learning notes into a short, engaging GFG Connect post 
(2-3 paragraphs, with emojis, professional tone):

{raw_text}"""


def generate_prompt(raw_text, template="default"):
    """
    Generate an AI prompt from raw text using a template.

    Args:
        raw_text: The raw text from voice/manual input
        template: 'default' or 'short'

    Returns:
        str: The formatted prompt ready for ChatGPT
    """
    if template == "short":
        return PROMPT_TEMPLATE_SHORT.format(raw_text=raw_text)
    return PROMPT_TEMPLATE.format(raw_text=raw_text)


def format_post(content):
    """
    Apply final formatting to the AI-generated post content.

    Args:
        content: The AI-generated post content

    Returns:
        str: Cleaned and formatted content ready for posting
    """
    if not content:
        return None

    # Clean up common formatting issues
    content = content.strip()

    # Remove leading/trailing quotes if present
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]

    # Remove markdown code blocks if present
    if content.startswith("```") and content.endswith("```"):
        content = content[3:-3].strip()

    return content
