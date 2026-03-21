"""
Browser Automation Module
Handles Playwright-based browser automation for GFG Connect posting.
Includes automated login via CLI credentials (never stored).
"""

import os
import getpass
import re
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

        # Kill any stale "Chrome for Testing" processes from previous runs
        self._cleanup_stale_processes()

        # Clean up ALL singleton files from crashed/suspended sessions
        singleton_files = ["SingletonLock", "SingletonSocket", "SingletonCookie"]
        for fname in singleton_files:
            fpath = os.path.join(SESSION_DIR, fname)
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                    log_info(f"Removed stale {fname}.")
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

    def _cleanup_stale_processes(self):
        """Kill any stale Chrome for Testing processes from previous runs."""
        import subprocess
        try:
            result = subprocess.run(
                ["pkill", "-9", "-f", "Google Chrome for Testing"],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                log_info("Killed stale Chrome processes.")
                import time
                time.sleep(1)  # Give OS time to release the lock
        except Exception:
            pass

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

    def login_with_credentials(self, email: str, password: str) -> bool:
        """
        Automate login using provided email and password credentials.
        Designed for programmatic/API usage.

        Args:
            email: User's email or username
            password: User's password

        Returns:
            bool: True if login was successful
        """
        if not email or not password:
            log_error("Email and password cannot be empty.")
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

            # Fill email/username
            log_info("Entering email/username...")
            email_field = None
            email_selectors = [
                'input.loginInput[placeholder="Username or Email"]',
                'input[placeholder="Username or Email"]',
                'input[placeholder="Username or email"]',
                'input#luser',
                'input[type="text"]',
            ]
            for selector in email_selectors:
                try:
                    email_field = self.page.wait_for_selector(selector, timeout=3000)
                    if email_field:
                        break
                except Exception:
                    continue

            if not email_field:
                log_error("Could not find email/username field.")
                return False

            email_field.click()
            self.page.wait_for_timeout(300)
            email_field.fill(email)
            log_success("Email/username entered.")

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
                'button:has-text("Sign In")',
                'button.loginBtn',
                'button[type="submit"]',
            ]
            for selector in login_selectors:
                try:
                    login_btn = self.page.wait_for_selector(selector, timeout=3000)
                    if login_btn:
                        break
                except Exception:
                    continue

            if login_btn:
                login_btn.click()
            else:
                log_warning("Could not find Sign In button, trying keyboard.")
                self.page.press('input[type="password"]', 'Enter')

            # Wait for login to complete
            self.page.wait_for_timeout(3000)

            if self.check_login_status():
                log_success("Login successful! 🎉")
                return True
            else:
                log_error("Login check failed after submission.")
                return False

        except Exception as e:
            log_error(f"Login with credentials failed: {e}")
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
            # Start from home where composer is usually available.
            current_url = self.page.url
            if "/connect/home" not in current_url:
                self.navigate_to_home()

            textbox_selectors = [
                'div.ContentEditable__root[role="textbox"]',
                'div[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"][data-testid*="editor"]',
                'div[contenteditable="true"][aria-label*="post" i]',
                'div[contenteditable="true"]',
                'div.ContentEditable__root',
            ]

            # First, check if editor is already open (common with cached sessions).
            textbox = self._find_first_visible(textbox_selectors, timeout=2500)

            if not textbox:
                log_info("Post editor not open yet. Trying composer triggers...")
                open_editor_selectors = [
                    'text="Share your thoughts."',
                    'text="Share your thoughts"',
                    'button:has-text("Create")',
                    'button:has-text("Write")',
                    '[placeholder*="Share your thoughts"]',
                    '[aria-label*="Share your thoughts" i]',
                    'div:has-text("Start a post")',
                ]

                opener = self._find_first_visible(open_editor_selectors, timeout=5000)
                if opener:
                    opener.click()
                    self.page.wait_for_timeout(1500)
                    log_info("Composer trigger clicked.")

                # Retry textbox detection after attempting to open editor.
                textbox = self._find_first_visible(textbox_selectors, timeout=6000)

            if not textbox:
                # Final fallback: reload home and try once more.
                log_warning("Composer not found, reloading home and retrying...")
                self.navigate_to_home()
                textbox = self._find_first_visible(textbox_selectors, timeout=6000)

            if not textbox:
                log_error("Could not find post textbox. Selectors may need updating.")
                return False

            # Normalize content to avoid hidden Unicode chars breaking hashtag parsing.
            prepared_content = self._prepare_post_content(content)

            # Focus editor and clear existing draft text if any.
            textbox.click()
            self.page.wait_for_timeout(300)
            self.page.keyboard.press("ControlOrMeta+a")
            self.page.keyboard.press("Backspace")
            self.page.wait_for_timeout(100)

            # Type content in a hashtag-aware way so platform suggestions can resolve tags.
            self._type_content_with_hashtag_commit(prepared_content)
            self.page.wait_for_timeout(1000)

            log_success(f"Post content filled ({len(prepared_content)} chars).")
            return True

        except Exception as e:
            log_error(f"Failed to fill post content: {e}")
            return False

    def _prepare_post_content(self, content):
        """Normalize post text and rebuild a clean hashtag line."""
        if not content:
            return ""

        text = content.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\u00A0", " ")
        text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)

        lines = [re.sub(r"[ \t]+$", "", line) for line in text.split("\n")]
        text = "\n".join(lines).strip()

        tags = re.findall(r"(?<!\w)[#＃]([A-Za-z0-9_]{1,50})", text)
        if not tags:
            return text

        # Keep tag order while deduplicating.
        seen = set()
        normalized_tags = []
        for tag in tags:
            key = tag.lower()
            if key not in seen:
                seen.add(key)
                normalized_tags.append(f"#{key}")

        text_without_tags = re.sub(r"(?<!\w)[#＃][A-Za-z0-9_]{1,50}", "", text)
        text_without_tags = re.sub(r"[ \t]{2,}", " ", text_without_tags)
        text_without_tags = re.sub(r"\n{3,}", "\n\n", text_without_tags).strip()

        hashtag_line = " ".join(normalized_tags)
        if not text_without_tags:
            return hashtag_line
        return f"{text_without_tags}\n\n{hashtag_line}"

    def _type_content_with_hashtag_commit(self, content):
        """
        Type post content with slower handling around hashtags so hashtag chips can resolve.

        Some rich editors only convert hashtags to recognized tokens when the tag is typed
        naturally and then committed with a delimiter key.
        """
        hashtag_pattern = re.compile(r"(#[A-Za-z0-9_]+)")
        lines = content.split("\n")

        for line_index, line in enumerate(lines):
            parts = hashtag_pattern.split(line)
            for part in parts:
                if not part:
                    continue

                if hashtag_pattern.fullmatch(part):
                    # Type hashtag character-by-character to mimic real typing cadence.
                    self.page.keyboard.type("#", delay=140)
                    tag_text = part[1:]
                    for ch in tag_text:
                        self.page.keyboard.type(ch, delay=85)

                    self.page.wait_for_timeout(520)
                    selected = self._select_hashtag_suggestion_if_visible(preferred_tag=tag_text)

                    if selected:
                        # Add delimiter after accepted suggestion.
                        self.page.keyboard.press("Space")
                        self.page.wait_for_timeout(140)
                    else:
                        # Keep plain hashtag and commit with delimiter.
                        self.page.keyboard.press("Space")
                        self.page.wait_for_timeout(180)
                else:
                    self.page.keyboard.type(part, delay=18)

            # Preserve original line breaks without adding a trailing newline.
            if line_index < len(lines) - 1:
                self.page.keyboard.press("Enter")
                self.page.wait_for_timeout(80)

    def _select_hashtag_suggestion_if_visible(self, preferred_tag=None):
        """Try selecting the first visible hashtag suggestion dropdown option."""
        suggestion_option_selectors = [
            '[role="listbox"] [role="option"]',
            'ul[role="listbox"] li',
            '[role="menu"] [role="menuitem"]',
            '[role="dialog"] [role="option"]',
            'div[class*="suggest"] li',
            'div[class*="suggest"] [role="option"]',
            'div[class*="autocomplete"] li',
            'div[class*="dropdown"] li',
        ]

        try:
            # Small pause to allow suggestion dropdown to render.
            self.page.wait_for_timeout(180)

            for selector in suggestion_option_selectors:
                locator = self.page.locator(selector)
                total = min(locator.count(), 8)
                if total == 0:
                    continue

                visible_items = []
                for idx in range(total):
                    candidate = locator.nth(idx)
                    try:
                        if candidate.is_visible():
                            visible_items.append(candidate)
                    except Exception:
                        continue

                if not visible_items:
                    continue

                target = visible_items[0]
                if preferred_tag:
                    for item in visible_items:
                        text = (item.inner_text() or "").strip().lower()
                        if preferred_tag.lower() in text:
                            target = item
                            break

                try:
                    target.click(timeout=500)
                except Exception:
                    self.page.keyboard.press("ArrowDown")
                    self.page.wait_for_timeout(120)
                    self.page.keyboard.press("Enter")

                log_info(f"Hashtag suggestion selected via: {selector}")
                return True

            # Fallback: text-based click in case options are rendered with unusual structure.
            if preferred_tag:
                variants = [f"#{preferred_tag}", preferred_tag]
                broad_selectors = [
                    'li',
                    '[role="option"]',
                    '[role="menuitem"]',
                    'button',
                    'div',
                    'span',
                ]
                for variant in variants:
                    for base in broad_selectors:
                        locator = self.page.locator(f'{base}:has-text("{variant}")')
                        total = min(locator.count(), 6)
                        for idx in range(total):
                            candidate = locator.nth(idx)
                            try:
                                if candidate.is_visible():
                                    candidate.click(timeout=500)
                                    log_info(f"Hashtag suggestion selected via text match: {base}")
                                    return True
                            except Exception:
                                continue

            # No visible suggestion options found through known selectors.
            return False
        except Exception:
            # Any selector or visibility failure should gracefully fall back.
            pass

        return False

    def _find_first_visible(self, selectors, timeout=5000):
        """Return first visible element found among selectors, otherwise None."""
        for selector in selectors:
            try:
                el = self.page.wait_for_selector(selector, timeout=timeout)
                if el and el.is_visible():
                    log_info(f"Matched selector: {selector}")
                    return el
            except Exception:
                continue
        return None

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
