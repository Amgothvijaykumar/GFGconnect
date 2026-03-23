"""
Utility Functions
Logging, clipboard helpers, and general utilities.
"""

import logging
import os
from datetime import datetime


# Setup logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "gfgconnect.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("GFGConnect")


def log_success(message):
    """Log a success message."""
    logger.info(f"✅ {message}")


def log_error(message):
    """Log an error message."""
    logger.error(f"❌ {message}")


def log_info(message):
    """Log an info message."""
    logger.info(f"ℹ️  {message}")


def log_warning(message):
    """Log a warning message."""
    logger.warning(f"⚠️  {message}")


def save_post_history(content, status="posted", platform=None):
    """
    Save post content to history for tracking.

    Args:
        content: The post content
        status: 'posted', 'failed', 'login_failed', 'login_required', or 'draft'
        platform: 'gfg', 'linkedin', 'twitter' (optional)
    """
    history_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "history")
    os.makedirs(history_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_{status}.md"
    filepath = os.path.join(history_dir, filename)

    with open(filepath, "w") as f:
        f.write(f"# {platform.upper() if platform else 'GFG Connect'} Post - {status.upper()}\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Status:** {status}\n")
        if platform:
            f.write(f"**Platform:** {platform}\n")
        f.write("\n---\n\n")
        f.write(content)

    log_info(f"Post saved to history: {filename}")
    return filepath
