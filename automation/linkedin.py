"""LinkedIn Automation Module"""

import os
from playwright.sync_api import sync_playwright
from utils.helpers import logger, log_success, log_error, log_info, log_warning

LINKEDIN_URL = "https://www.linkedin.com/feed/"
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "browser_data")


class LinkedInBrowser:
    """Manages browser automation for LinkedIn posting."""

    def __init__(self, headless=False):
        """Initialize the LinkedIn browser manager."""
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self):
        """Launch the browser with persistent session."""
        log_info("Launching LinkedIn browser...")
        os.makedirs(SESSION_DIR, exist_ok=True)

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            storage_state=os.path.join(SESSION_DIR, "linkedin_state.json")
            if os.path.exists(os.path.join(SESSION_DIR, "linkedin_state.json"))
            else None
        )
        self.page = self.context.new_page()
        log_success("LinkedIn browser launched.")

    def login_with_credentials(self, email: str, password: str) -> bool:
        """Login to LinkedIn with email and password."""
        try:
            log_info("Navigating to LinkedIn login...")
            self.page.goto(LINKEDIN_LOGIN_URL, wait_until="networkidle")
            self.page.wait_for_timeout(2000)

            # Fill email
            log_info("Entering email...")
            email_field = self.page.wait_for_selector('input[name="session_key"]', timeout=5000)
            email_field.fill(email)
            self.page.wait_for_timeout(300)

            # Fill password
            log_info("Entering password...")
            password_field = self.page.wait_for_selector('input[name="session_password"]', timeout=5000)
            password_field.fill(password)
            self.page.wait_for_timeout(300)

            # Click sign in
            log_info("Clicking sign in...")
            signin_btn = self.page.wait_for_selector('button[type="submit"]', timeout=5000)
            signin_btn.click()

            # Wait for successful login
            self.page.wait_for_timeout(5000)
            
            # Check if logged in by looking for feed
            try:
                self.page.wait_for_selector('button[aria-label="Start a post"]', timeout=10000)
                log_success("LinkedIn login successful!")
                return True
            except:
                log_error("Login check failed - start post button not found")
                return False

        except Exception as e:
            log_error(f"LinkedIn login failed: {e}")
            return False

    def post_content(self, content: str) -> bool:
        """Post content to LinkedIn."""
        try:
            log_info("Navigating to LinkedIn feed...")
            self.page.goto(LINKEDIN_URL, wait_until="networkidle")
            self.page.wait_for_timeout(2000)

            # Click the "Start a post" button
            log_info("Clicking start post button...")
            start_post_btn = self.page.wait_for_selector('button[aria-label="Start a post"]', timeout=5000)
            start_post_btn.click()
            self.page.wait_for_timeout(2000)

            # Fill in the post textarea
            log_info("Entering post content...")
            post_textarea = self.page.wait_for_selector('div[role="textbox"][contenteditable="true"]', timeout=5000)
            post_textarea.click()
            post_textarea.fill(content)
            self.page.wait_for_timeout(1000)

            # Click post button
            log_info("Clicking post button...")
            post_btn = self.page.wait_for_selector('button:has-text("Post")', timeout=5000)
            if post_btn:
                post_btn.click()
            else:
                # Try alternative selector
                post_btn = self.page.wait_for_selector('button[aria-label="Post"]', timeout=5000)
                post_btn.click()

            self.page.wait_for_timeout(3000)
            log_success("LinkedIn post published!")
            return True

        except Exception as e:
            log_error(f"Failed to post on LinkedIn: {e}")
            return False

    def close(self):
        """Close the browser and save session."""
        try:
            if self.context:
                self.context.storage_state(path=os.path.join(SESSION_DIR, "linkedin_state.json"))
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            log_info("LinkedIn browser closed.")
        except Exception as e:
            log_error(f"Error closing LinkedIn browser: {e}")
