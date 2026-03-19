"""
Browser Automation Module
Handles Playwright-based browser automation for GFG Connect posting.
Includes automated login via CLI credentials (never stored).
"""

import os
import getpass
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

    def _dismiss_cookie_banner(self):
        """Dismiss the cookie consent banner if present."""
        try:
            cookie_btn = self.page.wait_for_selector(
                'text="Got It !"', timeout=3000
            )
            if cookie_btn:
                cookie_btn.click()
                log_info("Cookie consent dismissed.")
                self.page.wait_for_timeout(500)
        except Exception:
            pass  # No cookie banner, that's fine

    def check_login_status(self):
        """
        Check if the user is logged in.

        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            # If "Sign In" button exists, user is NOT logged in
            sign_in_btn = self.page.query_selector('div.signinButton')
            if sign_in_btn:
                log_warning("User is NOT logged in.")
                return False

            # Also check the top-right "Sign In" link
            sign_in_link = self.page.query_selector('a:has-text("Sign In")')
            if sign_in_link:
                log_warning("User is NOT logged in.")
                return False

            log_success("User is logged in.")
            return True
        except Exception:
            log_warning("Could not determine login status.")
            return False

    def automated_login(self):
        """
        Automate login using credentials entered via CLI.
        Credentials are NEVER stored — entered at runtime only.

        Returns:
            bool: True if login was successful
        """
        print("\n" + "=" * 60)
        print("  🔐 GFG Connect Login")
        print("  Your credentials are NOT stored anywhere.")
        print("=" * 60)

        username = input("  📧 Username or Email: ").strip()
        password = getpass.getpass("  🔑 Password: ").strip()

        if not username or not password:
            log_error("Username and password cannot be empty.")
            return False

        try:
            # Dismiss cookie banner first
            self._dismiss_cookie_banner()

            # Click the "Sign In" button on GFG Connect page to open modal
            log_info("Opening login modal...")
            sign_in_btn = self.page.query_selector('div.signinButton')
            if not sign_in_btn:
                # Try the top-right Sign In link
                sign_in_btn = self.page.query_selector('a:has-text("Sign In")')

            if sign_in_btn:
                sign_in_btn.click()
                self.page.wait_for_timeout(2000)
                log_info("Login modal opened.")
            else:
                log_warning("Could not find Sign In button, trying direct auth page...")
                self.page.goto(GFG_LOGIN_URL, wait_until="networkidle")
                self.page.wait_for_timeout(2000)

            # Fill username
            log_info("Entering username...")
            username_field = None
            username_selectors = [
                'input[placeholder="Username or Email"]',
                'input[placeholder="Username or email"]',
                'input#luser',
                'input[type="text"]',
            ]
            for selector in username_selectors:
                try:
                    username_field = self.page.wait_for_selector(selector, timeout=3000)
                    if username_field:
                        break
                except Exception:
                    continue

            if not username_field:
                log_error("Could not find username field.")
                return False

            username_field.click()
            self.page.wait_for_timeout(300)
            username_field.fill(username)
            log_success("Username entered.")

            # Fill password
            log_info("Entering password...")
            password_field = None
            password_selectors = [
                'input[placeholder="Enter password"]',
                'input[placeholder="Password"]',
                'input#password',
                'input[type="password"]',
            ]
            for selector in password_selectors:
                try:
                    password_field = self.page.wait_for_selector(selector, timeout=3000)
                    if password_field:
                        break
                except Exception:
                    continue

            if not password_field:
                log_error("Could not find password field.")
                return False

            password_field.click()
            self.page.wait_for_timeout(300)
            password_field.fill(password)
            log_success("Password entered.")

            # Click Sign In button
            log_info("Clicking Sign In...")
            login_btn = None
            login_selectors = [
                'button.notSocialAuthBtn',
                'button.signin-button',
                'button:has-text("Sign In")',
            ]
            for selector in login_selectors:
                try:
                    login_btn = self.page.wait_for_selector(selector, timeout=3000)
                    if login_btn:
                        break
                except Exception:
                    continue

            if not login_btn:
                log_error("Could not find Sign In button.")
                return False

            login_btn.click()
            log_info("Sign In clicked. Waiting for login to complete...")

            # Wait for login to complete (page navigation or modal close)
            self.page.wait_for_timeout(5000)

            # Verify login success
            # After login, the Sign In button should disappear
            sign_in_check = self.page.query_selector('div.signinButton')
            if sign_in_check:
                log_error("Login may have failed. Sign In button still visible.")
                print("\n⚠️  Login might have failed. Please check:")
                print("   - Are your credentials correct?")
                print("   - Is there a CAPTCHA to solve?")
                retry = input("   Press Enter after resolving, or type 'skip' to continue: ").strip()
                if retry.lower() == 'skip':
                    return True
                return self.check_login_status()

            log_success("Login successful! 🎉")
            return True

        except Exception as e:
            log_error(f"Login failed: {e}")
            return False

    def wait_for_manual_login(self):
        """Wait for user to manually log in (fallback method)."""
        print("\n" + "=" * 60)
        print("🔐 Please log in to GFG Connect manually in the browser.")
        print("   After logging in, press Enter here to continue...")
        print("=" * 60)
        input()
        log_info("User confirmed login. Continuing...")

    def login(self):
        """
        Handle login flow — auto login or manual fallback.

        Returns:
            bool: True if logged in successfully
        """
        print("\n🔐 Login Required. Choose a method:")
        print("   1. Auto login (enter credentials here)")
        print("   2. Manual login (log in via browser window)")
        choice = input("   Enter choice (1/2): ").strip()

        if choice == "1":
            success = self.automated_login()
            if not success:
                print("\n⚠️  Auto login failed. Falling back to manual login.")
                self.wait_for_manual_login()
            return True
        else:
            self.wait_for_manual_login()
            return True

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
