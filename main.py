"""
🚀 Voice-to-GFG Connect Auto Posting System
=============================================
Main entry point that orchestrates the full pipeline:
  Voice/Text Input → AI Formatting → Review → Confirm → Auto Post

Usage:
    python main.py                  # Manual text input mode
    python main.py --clipboard      # Read from clipboard
    python main.py --prompt-only    # Only generate AI prompt (no posting)
"""

import sys
import pyperclip

from input.text_input import get_input
from processing.content import generate_prompt, format_post
from automation.browser import GFGBrowser
from utils.helpers import (
    logger,
    log_success,
    log_error,
    log_info,
    log_warning,
    save_post_history,
)


def display_banner():
    """Display the application banner."""
    print()
    print("=" * 60)
    print("  🚀 Voice-to-GFG Connect Auto Posting System")
    print("  📌 Speak → Review → Post (in under 1 minute)")
    print("=" * 60)
    print()


def get_mode_from_args():
    """Parse command line arguments for input mode."""
    args = sys.argv[1:]
    if "--clipboard" in args:
        return "clipboard"
    if "--prompt-only" in args:
        return "prompt-only"
    return "manual"


def step1_get_input(mode):
    """Step 1: Get raw text input from user."""
    print("\n📌 STEP 1: Capture Your Learning")
    print("-" * 40)

    if mode == "clipboard":
        raw_text = get_input(mode="clipboard")
    else:
        print("💡 Tip: Use voice dictation (macOS: Fn Fn) then paste here,")
        print("   or type your learning directly.\n")
        raw_text = get_input(mode="manual")

    if not raw_text:
        log_error("No input received. Exiting.")
        return None

    print(f"\n✅ Captured {len(raw_text)} characters of text.")
    return raw_text


def step2_generate_prompt(raw_text):
    """Step 2: Generate AI prompt for content formatting."""
    print("\n📌 STEP 2: Generate AI Prompt")
    print("-" * 40)

    prompt = generate_prompt(raw_text)

    print("\n📋 Copy this prompt and paste it into ChatGPT (free):")
    print("=" * 60)
    print(prompt)
    print("=" * 60)

    # Copy prompt to clipboard for convenience
    try:
        pyperclip.copy(prompt)
        print("\n✅ Prompt copied to clipboard! Paste it in ChatGPT.")
    except Exception:
        print("\n⚠️  Could not copy to clipboard. Please copy manually.")

    return prompt


def step3_get_ai_response():
    """Step 3: Get the AI-generated post content from user."""
    print("\n📌 STEP 3: Paste AI Response")
    print("-" * 40)
    print("📋 After ChatGPT generates your post, copy it and paste here.")
    print("   (Press Enter twice when done)\n")

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

    content = "\n".join(lines).strip()
    if not content:
        log_error("No AI response received.")
        return None

    return format_post(content)


def step4_review_and_confirm(content):
    """Step 4: Display content for review and get confirmation."""
    print("\n📌 STEP 4: Review & Confirm")
    print("-" * 40)
    print("\n📄 Your post will look like this:")
    print("=" * 60)
    print(content)
    print("=" * 60)

    while True:
        response = input("\n🔔 Do you want to post this? (yes/no/edit): ").strip().lower()
        if response in ("yes", "y"):
            return True
        elif response in ("no", "n"):
            print("❌ Post cancelled.")
            save_post_history(content, status="cancelled")
            return False
        elif response in ("edit", "e"):
            print("\n✏️  Enter the edited content (press Enter twice when done):")
            return "edit"
        else:
            print("⚠️  Please enter 'yes', 'no', or 'edit'.")


def step5_auto_post(content):
    """Step 5: Automatically post to GFG Connect using Playwright."""
    print("\n📌 STEP 5: Auto Posting to GFG Connect")
    print("-" * 40)

    browser = GFGBrowser(headless=False)

    try:
        # Launch browser
        browser.launch()

        # Navigate to GFG Connect
        browser.navigate_to_gfg_connect()

        # Check if logged in
        if not browser.check_login_status():
            browser.wait_for_manual_login()

        # Fill the post content
        if not browser.fill_post(content):
            log_error("Failed to fill post content.")
            save_post_history(content, status="failed")
            return False

        # Final confirmation before clicking submit
        confirm = input("\n🔔 Content is filled. Click 'Post' now? (yes/no): ").strip().lower()
        if confirm not in ("yes", "y"):
            print("❌ Posting cancelled at final step.")
            save_post_history(content, status="draft")
            return False

        # Submit the post
        if browser.submit_post():
            log_success("Post published to GFG Connect! 🎉")
            save_post_history(content, status="posted")
            return True
        else:
            log_error("Failed to submit post.")
            save_post_history(content, status="failed")
            return False

    except Exception as e:
        log_error(f"An error occurred during posting: {e}")
        save_post_history(content, status="failed")
        return False

    finally:
        input("\nPress Enter to close the browser...")
        browser.close()


def main():
    """Main execution flow."""
    display_banner()

    mode = get_mode_from_args()
    log_info(f"Starting in '{mode}' mode.")

    # Step 1: Get raw input
    raw_text = step1_get_input(mode)
    if not raw_text:
        return

    # Step 2: Generate AI prompt
    if mode == "prompt-only":
        step2_generate_prompt(raw_text)
        print("\n✅ Done! Use the prompt above with ChatGPT.")
        return

    step2_generate_prompt(raw_text)

    # Step 3: Get AI response
    content = step3_get_ai_response()
    if not content:
        return

    # Step 4: Review and confirm
    while True:
        result = step4_review_and_confirm(content)
        if result is True:
            break
        elif result == "edit":
            content = step3_get_ai_response()
            if not content:
                return
        else:
            return

    # Step 5: Auto post
    step5_auto_post(content)

    print("\n" + "=" * 60)
    print("  ✅ All done! See you tomorrow! 🚀")
    print("=" * 60)


if __name__ == "__main__":
    main()
