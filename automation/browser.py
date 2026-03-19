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
GFG_CONNECT_URL = "https://www.geeksforgeeks.org/connect/explore"
GFG_CONNECT_HOME = "https://www.geeksforgeeks.org/connect/home"
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

        # Clean up stale lock file from crashed/suspended sessions
        lock_file = os.path.join(SESSION_DIR, "SingletonLock")
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                log_info("Removed stale browser lock file.")
            except OSError:
                pass

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
        """Navigate to GFG Connect explore page."""
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
            # If "Sign In" button exists on this page, user is NOT logged in
            sign_in_btn = self.page.query_selector('button.signinButton.login-modal-btn')
            if sign_in_btn:
                log_warning("User is NOT logged in.")
                return False

            # Also check for the top-right "Sign In" text
            sign_in_link = self.page.query_selector('text="Sign In"')
            if sign_in_link:
                # Could be a post's Sign In - check if it's in the header area
                bounding = sign_in_link.bounding_box()
                if bounding and bounding["y"] < 60:
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

            sign_in_selectors = [
                'button.signinButton.login-modal-btn',
                'button.signinButton',
                'button:has-text("Sign In")',
                'text="Sign In"',
            ]

            sign_in_btn = None
            for selector in sign_in_selectors:
                try:
                    sign_in_btn = self.page.wait_for_selector(selector, timeout=3000)
                    if sign_in_btn:
                        break
                except Exception:
                    continue

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
                'input.loginInput[placeholder="Username or Email"]',
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
                'input.loginInput[placeholder="Enter password"]',
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
                'button.loginBtn.btnGreen.notSocialAuthBtn',
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
                log_error("Could not find Sign In button in modal.")
                return False

            login_btn.click()
            log_info("Sign In clicked. Waiting for login to complete...")

            # Wait for login to complete
            self.page.wait_for_timeout(5000)

            # Navigate to connect home after login
            self.page.goto(GFG_CONNECT_HOME, wait_until="networkidle")
            self.page.wait_for_timeout(2000)

            # Verify login success — check for Sign In button absence
            sign_in_check = self.page.query_selector('button.signinButton.login-modal-btn')
            if sign_in_check:
                log_error("Login may have failed. Sign In button still visible.")
                print("\n⚠️  Login might have failed. Please check:")
                print("   - Are your credentials correct?")
                print("   - Is there a CAPTCHA to solve?")
                retry = input("   Press Enter after resolving, or type 'skip' to continue: ").strip()
                if retry.lower() == "skip":
                    return True
                # Reload and recheck
                self.page.reload(wait_until="networkidle")
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

    def navigate_to_home(self):
        """Navigate to GFG Connect home page (for posting)."""
        log_info(f"Navigating to {GFG_CONNECT_HOME}")
        self.page.goto(GFG_CONNECT_HOME, wait_until="networkidle")
        self.page.wait_for_timeout(2000)
        log_success("GFG Connect Home page loaded.")

    def fill_post(self, content):
        """
        Fill the post content in GFG Connect's post form.

        Args:
            content: The formatted post content

        Returns:
            bool: True if content was filled successfully
        """
        try:
            # Make sure we're on the home page (where posting is available)
            current_url = self.page.url
            if "/connect/home" not in current_url:
                self.navigate_to_home()

            log_info("Looking for 'Share your thoughts' area...")

            # Click on "Share your thoughts." to open the post editor
            share_selectors = [
                'text="Share your thoughts."',
                'div:has-text("Share your thoughts")',
                '[placeholder*="Share your thoughts"]',
            ]

            share_area = None
            for selector in share_selectors:
                try:
                    share_area = self.page.wait_for_selector(selector, timeout=5000)
                    if share_area:
                        log_info(f"Found share area with: {selector}")
                        break
                except Exception:
                    continue

            if not share_area:
                log_error("Could not find 'Share your thoughts' area.")
                return False

            share_area.click()
            self.page.wait_for_timeout(2000)
            log_info("Post editor opened.")

            # Find the content-editable textbox
            textbox_selectors = [
                'div.ContentEditable__root[role="textbox"]',
                'div[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"]',
                'div.ContentEditable__root',
            ]

            textbox = None
            for selector in textbox_selectors:
                try:
                    textbox = self.page.wait_for_selector(selector, timeout=5000)
                    if textbox:
                        log_info(f"Found textbox with: {selector}")
                        break
                except Exception:
                    continue

            if not textbox:
                log_error("Could not find post textbox. Selectors may need updating.")
                return False

            # Click on the textbox and type content
            textbox.click()
            self.page.wait_for_timeout(500)

            # Use keyboard to type content (contenteditable divs work better with type)
            self.page.keyboard.type(content, delay=10)
            self.page.wait_for_timeout(1000)

            log_success(f"Post content filled ({len(content)} chars).")
            return True

        except Exception as e:
            log_error(f"Failed to fill post content: {e}")
            return False

    def submit_post(self):
        """
        Click the Publish button to submit the post.

        Returns:
            bool: True if post was submitted successfully
        """
        try:
            log_info("Looking for Publish button...")

            # Try selectors for the Publish button
            selectors = [
                'button:has-text("Publish")',
                'button:has-text("Post")',
                'button:has-text("Submit")',
                'button[type="submit"]',
            ]

            button = None
            for selector in selectors:
                try:
                    button = self.page.wait_for_selector(selector, timeout=5000)
                    if button:
                        log_info(f"Found publish button with: {selector}")
                        break
                except Exception:
                    continue

            if not button:
                log_error("Could not find Publish button. Selectors may need updating.")
                return False

            button.click()
            self.page.wait_for_timeout(5000)

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
