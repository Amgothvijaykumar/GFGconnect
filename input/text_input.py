"""
Input Handler Module
Handles capturing text input from voice dictation or typed text.
"""

import speech_recognition as sr
import pyperclip


def get_voice_input():
    """
    Capture voice input using the microphone and convert to text.
    Uses Google's free Speech-to-Text API.

    Returns:
        str: Recognized text, or None if failed
    """
    recognizer = sr.Recognizer()

    print("\n🎤 Voice Input Mode")
    print("-" * 40)
    print("🔊 Speak now... (will stop when you pause)")
    print("   Press Ctrl+C to cancel.\n")

    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            print("   🔇 Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("   ✅ Ready! Speak now...\n")

            # Listen for speech
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=60)

        print("   🔄 Converting speech to text...")
        text = recognizer.recognize_google(audio)

        if text:
            print(f"\n   📝 Recognized: \"{text}\"")
            return text.strip()
        else:
            print("   ❌ Could not recognize speech.")
            return None

    except sr.WaitTimeoutError:
        print("   ⏰ Timeout — no speech detected.")
        return None
    except sr.UnknownValueError:
        print("   ❌ Could not understand the audio. Try speaking more clearly.")
        return None
    except sr.RequestError as e:
        print(f"   ❌ Speech recognition service error: {e}")
        return None
    except KeyboardInterrupt:
        print("\n   ❌ Voice input cancelled.")
        return None
    except OSError as e:
        print(f"   ❌ Microphone error: {e}")
        print("   💡 Make sure your microphone is connected and permitted.")
        return None


def get_text_input():
    """Get text input directly from the user via CLI."""
    print("\n⌨️  Text Input Mode")
    print("-" * 40)
    print("Type your learning (press Enter twice to finish):\n")

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


def get_clipboard_input():
    """Read text from the system clipboard."""
    text = pyperclip.paste()
    if not text or not text.strip():
        return None
    return text.strip()


def get_input():
    """
    Get text input — let user choose between voice or text.

    Returns:
        str: The captured text, or None if empty
    """
    print("\n📌 How would you like to input your learning?")
    print("   1. 🎤 Voice (speak into microphone)")
    print("   2. ⌨️  Text (type it out)")
    print("   3. 📋 Clipboard (paste from clipboard)")

    choice = input("\n   Enter choice (1/2/3): ").strip()

    if choice == "1":
        text = get_voice_input()
        if not text:
            print("\n   ⚠️ Voice failed. Falling back to text input.")
            text = get_text_input()
    elif choice == "3":
        print("   📋 Reading from clipboard...")
        text = get_clipboard_input()
        if text:
            print(f"   ✅ Got {len(text)} characters from clipboard.")
            print(f"   📝 Content: \"{text[:100]}{'...' if len(text) > 100 else ''}\"")
        else:
            print("   ⚠️ Clipboard is empty. Falling back to text input.")
            text = get_text_input()
    else:
        text = get_text_input()

    if not text:
        print("   ❌ No input received.")
        return None

    return text
