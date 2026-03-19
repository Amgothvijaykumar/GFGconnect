"""
Input Handler Module
Handles capturing text input from voice dictation or clipboard.
"""

import pyperclip


def get_text_from_clipboard():
    """Read text from the system clipboard."""
    text = pyperclip.paste()
    if not text or not text.strip():
        return None
    return text.strip()


def get_text_from_user():
    """Get text input directly from the user via CLI."""
    print("\n📝 Enter your learning text (press Enter twice to finish):")
    print("-" * 50)
    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
    return "\n".join(lines).strip()


def get_input(mode="manual"):
    """
    Get text input based on the selected mode.

    Args:
        mode: 'manual' for typed input, 'clipboard' for clipboard reading

    Returns:
        str: The captured text, or None if empty
    """
    if mode == "clipboard":
        print("📋 Reading from clipboard...")
        text = get_text_from_clipboard()
        if text:
            print(f"✅ Got {len(text)} characters from clipboard.")
        else:
            print("⚠️  Clipboard is empty. Falling back to manual input.")
            text = get_text_from_user()
    else:
        text = get_text_from_user()

    if not text:
        print("❌ No input received.")
        return None

    return text
