"""
Input Handler Module
Handles capturing text input from voice dictation or typed text.
"""

import speech_recognition as sr
import pyperclip
import threading
import sys


def get_voice_input(start_timeout_seconds=120, phrase_time_limit_seconds=300):
    """
    Capture voice input using the microphone and convert to text.
    Uses Google's free Speech-to-Text API.
    Waits until the user finishes speaking (long pauses allowed).

    Returns:
        str: Recognized text, or None if failed
    """
    recognizer = sr.Recognizer()

    # Allow longer pauses between words/sentences (default is 0.8s)
    recognizer.pause_threshold = 3.0      # Wait 3 seconds of silence before stopping
    recognizer.phrase_threshold = 0.3      # Minimum speaking duration to consider
    recognizer.non_speaking_duration = 1.5  # Seconds of silence to keep in buffer

    print("\n🎤 Voice Input Mode")
    print("-" * 40)
    print("🔊 Speak clearly into your microphone.")
    print("   The system will listen until you pause for 3+ seconds.")
    print(f"   Start timeout: {start_timeout_seconds}s | Max phrase: {phrase_time_limit_seconds}s")
    print("   Press Ctrl+C to stop early.\n")

    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            print("   🔇 Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("   ✅ Microphone ready!")
            print("   🎙️  Listening... (speak now)\n")

            # Start a background indicator
            stop_indicator = threading.Event()
            indicator_thread = threading.Thread(
                target=_listening_indicator, args=(stop_indicator,), daemon=True
            )
            indicator_thread.start()

            # Listen without strict timeout — wait for user to finish naturally
            audio = recognizer.listen(
                source,
                timeout=start_timeout_seconds,
                phrase_time_limit=phrase_time_limit_seconds,
            )

            stop_indicator.set()

        print("\n\n   🔄 Converting speech to text...")
        text = recognizer.recognize_google(audio)

        if text:
            print(f"\n   📝 Recognized text:")
            print(f"   \"{text}\"\n")
            return text.strip()
        else:
            print("   ❌ Could not recognize speech.")
            return None

    except sr.WaitTimeoutError:
        print(f"\n   ⏰ Timeout — no speech detected in {start_timeout_seconds} seconds.")
        return None
    except sr.UnknownValueError:
        print("\n   ❌ Could not understand the audio. Try speaking more clearly.")
        return None
    except sr.RequestError as e:
        print(f"\n   ❌ Speech recognition service error: {e}")
        return None
    except KeyboardInterrupt:
        print("\n\n   ⏹️  Voice input stopped.")
        # If we captured some audio before Ctrl+C, try to recognize it
        return None
    except OSError as e:
        print(f"\n   ❌ Microphone error: {e}")
        print("   💡 Make sure your microphone is connected and has permission.")
        print("   💡 On macOS: System Settings → Privacy & Security → Microphone")
        return None


def _listening_indicator(stop_event):
    """Show a live indicator while listening."""
    dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r   {dots[i % len(dots)]} Recording... (pause for 3s to finish)")
        sys.stdout.flush()
        stop_event.wait(0.1)
        i += 1


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
