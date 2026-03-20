"""Twitter/X Automation Module"""

import os
from playwright.sync_api import sync_playwright
from utils.helpers import logger, log_success, log_error, log_info, log_warning

TWITTER_URL = "https://x.com/home"
TWITTER_LOGIN_URL = "https://x.com/i/flow/login"
SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "browser_data")


class TwitterBrowser:
    """Manages browser automation for Twitter/X posting."""

    def __init__(self, headless=False):
        """Initialize the Twitter browser manager."""
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self):
        """Launch the browser with persistent session."""
        log_info("Launching Twitter browser...")
        os.makedirs(SESSION_DIR, exist_ok=True)

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            storage_state=os.path.join(SESSION_DIR, "twitter_state.json")
            if os.path.exists(os.path.join(SESSION_DIR, "twitter_state.json"))
            else None
        )
        self.page = self.context.new_page()
        log_success("Twitter browser launched.")

    def login_with_credentials(self, email: str, password: str) -> bool:
        """Login to Twitter with email and password."""
        try:
            log_info("Navigating to Twitter login...")
            self.page.goto(TWITTER_LOGIN_URL, wait_until="networkidle")
            self.page.wait_for_timeout(2000)

            # Fill email/username
            log_info("Entering email/username...")
            email_field = self.page.wait_for_selector('input[autocomplete="username"]', timeout=5000)
            email_field.fill(email)
            self.page.wait_for_timeout(300)

            # Click next button
            log_info("Clicking next...")
            next_btn = self.page.wait_for_selector('button:has-text("Next"), button[role="button"]:has-text("Next")', timeout=5000)
            if next_btn:
                next_btn.click()
            else:
                self.page.keyboard.press("Enter")
            
            self.page.wait_for_timeout(2000)

            # Fill password
            log_info("Entering password...")
            try:
                password_field = self.page.wait_for_selector('input[autocomplete="current-password"]', timeout=5000)
                password_field.fill(password)
                self.page.wait_for_timeout(300)

                # Click login button
                log_info("Clicking login...")
                login_btn = self.page.wait_for_selector('button:has-text("Log in"), button[role="button"]:has-text("Log in")', timeout=5000)
                if login_btn:
                    login_btn.click()
                else:
                    self.page.keyboard.press("Enter")

                self.page.wait_for_timeout(5000)
                log_success("Twitter login successful!")
                return True
            except:
                log_error("Password field not found - login may have failed")
                return False

        except Exception as e:
            log_error(f"Twitter login failed: {e}")
            return False

    def post_content(self, content: str) -> bool:
        """Post content to Twitter."""
        try:
            log_info("Navigating to Twitter home...")
            self.page.goto(TWITTER_URL, wait_until="networkidle")
            self.page.wait_for_timeout(2000)

            # Click the compose tweet area
            log_info("Clicking compose area...")
            compose_area = self.page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=5000)
            if not compose_area:
                compose_area = self.page.wait_for_selector('div[role="textbox"][data-testid*="tweet"]', timeout=5000)
            
            compose_area.click()
            self.page.wait_for_timeout(500)

            # Fill in the tweet text
            log_info("Entering tweet content...")
            compose_area.fill(content)
            self.page.wait_for_timeout(1000)

            # Click tweet/post button
            log_info("Clicking tweet button...")
            tweet_btn = self.page.wait_for_selector('button[data-testid="Tweet"], button:has-text("Post")', timeout=5000)
            if tweet_btn:
                tweet_btn.click()
            else:
                # Try alternative selector
                tweet_btn = self.page.wait_for_selector('button[aria-label*="Tweet"]', timeout=5000)
                tweet_btn.click()

            self.page.wait_for_timeout(3000)
            log_success("Twitter post published!")
            return True

        except Exception as e:
            log_error(f"Failed to post on Twitter: {e}")
            return False

    def close(self):
        """Close the browser and save session."""
        try:
            if self.context:
                self.context.storage_state(path=os.path.join(SESSION_DIR, "twitter_state.json"))
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            log_info("Twitter browser closed.")
        except Exception as e:
            log_error(f"Error closing Twitter browser: {e}")
