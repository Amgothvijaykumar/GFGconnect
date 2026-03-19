"""
Browser Automation Module
Handles Playwright-based browser automation for GFG Connect posting.
"""

import os
from playwright.sync_api import sync_playwright
from utils.helpers import logger, log_success, log_error, log_info, log_warning


# GFG Connect URLs
GFG_CONNECT_URL = "https://connect.geeksforgeeks.org/"
GFG_LOGIN_URL = "https://auth.geeksforgeeks.org/"

# Browser session storage path
SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "browser_data")


class GFGBrowser:
    """Manages browser automation for GFG Connect."""

    def __init__(self, headless=False):
        """
        Initialize the browser manager.

        Args:
            headless: If False, browser is visible for debugging (recommended)
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self):
        """Launch the browser with persistent session."""
        log_info("Launching browser...")
        os.makedirs(SESSION_DIR, exist_ok=True)

        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=self.headless,
            viewport={"width": 1280, "height": 720},
            args=["--disable-blink-features=AutomationControlled"],
        )
        self.page = self.context.new_page()
        log_success("Browser launched successfully.")
        return self.page

    def navigate_to_gfg_connect(self):
        """Navigate to GFG Connect homepage."""
        log_info(f"Navigating to {GFG_CONNECT_URL}")
        self.page.goto(GFG_CONNECT_URL, wait_until="networkidle")
        log_success("GFG Connect page loaded.")

    def check_login_status(self):
        """
        Check if the user is logged in.

        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            # Check for common logged-in indicators
            # This selector may need adjustment based on GFG Connect's actual UI
            self.page.wait_for_selector('[class*="profile"]', timeout=5000)
            log_success("User is logged in.")
            return True
        except Exception:
            log_warning("User is NOT logged in.")
            return False

    def wait_for_manual_login(self):
        """Wait for user to manually log in."""
        print("\n" + "=" * 60)
        print("🔐 Please log in to GFG Connect manually in the browser.")
        print("   After logging in, press Enter here to continue...")
        print("=" * 60)
        input()
        log_info("User confirmed login. Continuing...")

    def fill_post(self, content):
        """
        Fill the post content in GFG Connect's post form.

        Args:
            content: The formatted post content

        Returns:
            bool: True if content was filled successfully
        """
        try:
            log_info("Looking for post input area...")

            # Try common selectors for the post textarea
            # These will need to be updated based on actual GFG Connect page structure
            selectors = [
                'textarea[placeholder*="write"]',
                'textarea[placeholder*="Write"]',
                'textarea[placeholder*="post"]',
                'div[contenteditable="true"]',
                'textarea.post-input',
                '[data-placeholder*="write"]',
                '[data-placeholder*="Write"]',
                'textarea',
            ]

            textarea = None
            for selector in selectors:
                try:
                    textarea = self.page.wait_for_selector(selector, timeout=3000)
                    if textarea:
                        log_info(f"Found input area with selector: {selector}")
                        break
                except Exception:
                    continue

            if not textarea:
                log_error("Could not find post input area. Selectors may need updating.")
                return False

            # Click on the textarea to focus
            textarea.click()
            self.page.wait_for_timeout(500)

            # Type the content
            textarea.fill(content)
            self.page.wait_for_timeout(500)

            log_success(f"Post content filled ({len(content)} chars).")
            return True

        except Exception as e:
            log_error(f"Failed to fill post content: {e}")
            return False

    def submit_post(self):
        """
        Click the post/submit button.

        Returns:
            bool: True if post was submitted successfully
        """
        try:
            log_info("Looking for submit button...")

            # Try common selectors for the post button
            selectors = [
                'button:has-text("Post")',
                'button:has-text("Submit")',
                'button:has-text("Publish")',
                'button[type="submit"]',
                'button.post-btn',
                'button.submit-btn',
            ]

            button = None
            for selector in selectors:
                try:
                    button = self.page.wait_for_selector(selector, timeout=3000)
                    if button:
                        log_info(f"Found submit button with selector: {selector}")
                        break
                except Exception:
                    continue

            if not button:
                log_error("Could not find submit button. Selectors may need updating.")
                return False

            button.click()
            self.page.wait_for_timeout(3000)

            log_success("Post submitted successfully! 🎉")
            return True

        except Exception as e:
            log_error(f"Failed to submit post: {e}")
            return False

    def close(self):
        """Close the browser."""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            log_info("Browser closed.")
        except Exception as e:
            log_warning(f"Error closing browser: {e}")
