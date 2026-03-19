"""
🚀 Voice-to-GFG Connect Auto Posting System
=============================================
Simplified pipeline:
  Voice/Text Input → Auto AI Rewrite → Review & Confirm → Auto Post

Usage:
    python main.py              # Interactive mode (choose voice/text)
    python main.py --clipboard  # Read from clipboard
"""

import sys

from input.text_input import get_input, get_text_input, get_voice_input, get_clipboard_input
from processing.content import rewrite_with_ai
from automation.browser import GFGBrowser
from utils.helpers import (
    log_success,
    log_error,
    log_info,
    save_post_history,
)


def display_banner():
    """Display the application banner."""
    print()
    print("=" * 60)
    print("  🚀 Voice-to-GFG Connect Auto Posting System")
    print("  📌 Speak/Type → AI Rewrites → Review → Post")
    print("=" * 60)
    print()


def step1_get_input():
    """Step 1: Get raw text input from user (voice or text)."""
    print("📌 STEP 1: Share Your Learning")
    print("-" * 40)

    raw_text = get_input()

    if not raw_text:
        log_error("No input received. Exiting.")
        return None

    print(f"\n✅ Captured {len(raw_text)} characters.")
    return raw_text


def step2_ai_rewrite(raw_text):
    """Step 2: Auto-rewrite using AI (Gemini)."""
    print("\n📌 STEP 2: AI Rewriting Your Post")
    print("-" * 40)

    rewritten = rewrite_with_ai(raw_text)

    if not rewritten:
        print("\n⚠️  AI rewrite failed. Using your original text instead.")
        return raw_text

    return rewritten


def step3_review_and_confirm(content, raw_text):
    """Step 3: Review the AI-rewritten post and confirm."""
    print("\n📌 STEP 3: Review & Confirm")
    print("-" * 40)

    while True:
        print("\n📄 Your post will look like this:")
        print("=" * 60)
        print(content)
        print("=" * 60)
        print(f"\n   📊 Character count: {len(content)}")

        print("\n   Options:")
        print("   ✅ yes  — Post it!")
        print("   ❌ no   — Cancel")
        print("   🔄 redo — Regenerate with AI")
        print("   ✏️  edit — Type your own version")

        response = input("\n🔔 What would you like to do? ").strip().lower()

        if response in ("yes", "y"):
            return content
        elif response in ("no", "n"):
            print("❌ Post cancelled.")
            save_post_history(content, status="cancelled")
            return None
        elif response in ("redo", "r"):
            print("\n🔄 Regenerating...")
            content = rewrite_with_ai(raw_text)
            if not content:
                print("⚠️  Regeneration failed. Using previous version.")
                content = raw_text
        elif response in ("edit", "e"):
            print("\n✏️  Type your custom post (press Enter twice when done):")
            custom = get_text_input()
            if custom:
                content = custom
        else:
            print("⚠️  Please enter 'yes', 'no', 'redo', or 'edit'.")


def step4_auto_post(content):
    """Step 4: Automatically post to GFG Connect."""
    print("\n📌 STEP 4: Auto Posting to GFG Connect")
    print("-" * 40)

    browser = GFGBrowser(headless=False)

    try:
        # Launch browser
        browser.launch()

        # Navigate to GFG Connect
        browser.navigate_to_gfg_connect()

        # Check if logged in
        if not browser.check_login_status():
            browser.login()

        # Fill the post content
        if not browser.fill_post(content):
            log_error("Failed to fill post content.")
            save_post_history(content, status="failed")
            return False

        # Final confirmation before publishing
        confirm = input("\n🔔 Content is filled in browser. Publish now? (yes/no): ").strip().lower()
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

    mode = "clipboard" if "--clipboard" in sys.argv else "interactive"
    log_info(f"Starting in '{mode}' mode.")

    # Step 1: Get raw input
    if mode == "clipboard":
        print("📌 STEP 1: Reading from Clipboard")
        print("-" * 40)
        raw_text = get_clipboard_input()
        if not raw_text:
            print("⚠️  Clipboard empty. Switching to interactive mode.")
            raw_text = get_input()
        else:
            print(f"✅ Got {len(raw_text)} chars from clipboard.")
            print(f"📝 Content: \"{raw_text[:100]}{'...' if len(raw_text) > 100 else ''}\"")
    else:
        raw_text = step1_get_input()

    if not raw_text:
        return

    # Step 2: AI rewrite
    content = step2_ai_rewrite(raw_text)

    # Step 3: Review and confirm
    content = step3_review_and_confirm(content, raw_text)
    if not content:
        return

    # Step 4: Auto post
    step4_auto_post(content)

    print("\n" + "=" * 60)
    print("  ✅ All done! See you tomorrow! 🚀")
    print("=" * 60)


if __name__ == "__main__":
    main()
