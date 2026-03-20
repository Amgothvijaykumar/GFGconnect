"""FastAPI server exposing rewrite/post/history operations for mobile frontend."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from automation.browser import GFGBrowser
from automation.linkedin import LinkedInBrowser
from automation.twitter import TwitterBrowser
from processing.content import rewrite_with_ai
from utils.helpers import save_post_history


ROOT_DIR = Path(__file__).resolve().parent.parent
HISTORY_DIR = ROOT_DIR / "history"


class RewriteRequest(BaseModel):
    raw_text: str = Field(min_length=1, max_length=4000)


class RewriteResponse(BaseModel):
    preview: str
    provider_used: str


class PostRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    platform: str = Field(default="gfg")  # gfg, linkedin, twitter
    email: str | None = Field(default=None, min_length=1, max_length=100)
    password: str | None = Field(default=None, min_length=1, max_length=200)


class PostResponse(BaseModel):
    status: str
    message: str


class ListenRequest(BaseModel):
    start_timeout_seconds: int = Field(default=180, ge=10, le=600)
    phrase_time_limit_seconds: int = Field(default=600, ge=30, le=1800)


class ListenResponse(BaseModel):
    text: str


class HistoryItem(BaseModel):
    filename: str
    status: str
    timestamp: str
    content: str


class DeleteHistoryResponse(BaseModel):
    status: str
    message: str
    deleted_count: int = 0


app = FastAPI(title="GFG Connect API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "gfg-connect-api"}


@app.post("/api/rewrite", response_model=RewriteResponse)
def rewrite_post(payload: RewriteRequest):
    rewritten = rewrite_with_ai(payload.raw_text)
    if rewritten:
        return RewriteResponse(preview=rewritten, provider_used="ai")

    return RewriteResponse(preview=payload.raw_text, provider_used="raw_fallback")


@app.post("/api/listen", response_model=ListenResponse)
def listen_from_microphone(payload: ListenRequest):
    try:
        # Import here so API can still start even when microphone deps are not installed.
        from input.text_input import get_voice_input

        text = get_voice_input(
            start_timeout_seconds=payload.start_timeout_seconds,
            phrase_time_limit_seconds=payload.phrase_time_limit_seconds,
        )
        if not text:
            raise HTTPException(
                status_code=408,
                detail="No speech captured. Please try again and speak clearly.",
            )
        return ListenResponse(text=text)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Voice capture failed: {exc}") from exc


@app.post("/api/post", response_model=PostResponse)
def publish_post(payload: PostRequest):
    # Route to appropriate platform
    if payload.platform == "linkedin":
        browser = LinkedInBrowser(headless=False)
    elif payload.platform == "twitter":
        browser = TwitterBrowser(headless=False)
    else:  # default to GFG
        browser = GFGBrowser(headless=False)

    try:
        browser.launch()

        if payload.platform == "gfg":
            browser.navigate_to_gfg_connect()

            # Respect cached session first. Only attempt credential login when required.
            already_logged_in = browser.check_login_status()
            if not already_logged_in:
                if payload.email and payload.password:
                    if not browser.login_with_credentials(payload.email, payload.password):
                        save_post_history(payload.content, status="draft", platform=payload.platform)
                        return PostResponse(
                            status="login_failed",
                            message="Login failed with provided credentials.",
                        )
                else:
                    save_post_history(payload.content, status="draft", platform=payload.platform)
                    return PostResponse(
                        status="login_required",
                        message="Please login in the opened browser window, then submit again.",
                    )

            if not browser.fill_post(payload.content):
                save_post_history(payload.content, status="failed", platform=payload.platform)
                raise HTTPException(status_code=500, detail="Could not fill post editor on GFG Connect.")

            if not browser.submit_post():
                save_post_history(payload.content, status="failed", platform=payload.platform)
                raise HTTPException(status_code=500, detail="Could not click Publish button.")

        elif payload.platform == "linkedin":
            if payload.email and payload.password:
                if not browser.login_with_credentials(payload.email, payload.password):
                    save_post_history(payload.content, status="draft", platform=payload.platform)
                    return PostResponse(
                        status="login_failed",
                        message="LinkedIn login failed with provided credentials.",
                    )
            else:
                raise HTTPException(status_code=400, detail="LinkedIn requires credentials.")

            if not browser.post_content(payload.content):
                save_post_history(payload.content, status="failed", platform=payload.platform)
                raise HTTPException(status_code=500, detail="Could not post on LinkedIn.")

        elif payload.platform == "twitter":
            if payload.email and payload.password:
                if not browser.login_with_credentials(payload.email, payload.password):
                    save_post_history(payload.content, status="draft", platform=payload.platform)
                    return PostResponse(
                        status="login_failed",
                        message="Twitter login failed with provided credentials.",
                    )
            else:
                raise HTTPException(status_code=400, detail="Twitter requires credentials.")

            if not browser.post_content(payload.content):
                save_post_history(payload.content, status="failed", platform=payload.platform)
                raise HTTPException(status_code=500, detail="Could not post on Twitter.")

        save_post_history(payload.content, status="posted", platform=payload.platform)
        return PostResponse(status="posted", message=f"Post published to {payload.platform.upper()} successfully.")

    except HTTPException:
        raise
    except Exception as exc:
        save_post_history(payload.content, status="failed", platform=payload.platform)
        raise HTTPException(status_code=500, detail=f"Unexpected posting error: {exc}") from exc
    finally:
        browser.close()


@app.get("/api/history", response_model=list[HistoryItem])
def get_history(limit: int = 20):
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 200")

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    entries: list[HistoryItem] = []

    files = sorted(HISTORY_DIR.glob("*.md"), reverse=True)[:limit]
    for file_path in files:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        status = _extract_status(text, fallback=file_path.stem.split("_")[-1])
        timestamp = _extract_timestamp(text, fallback=file_path.stem.split("_")[0])
        content = _extract_content(text)

        entries.append(
            HistoryItem(
                filename=file_path.name,
                status=status,
                timestamp=timestamp,
                content=content,
            )
        )

    return entries


@app.delete("/api/history/{filename}", response_model=DeleteHistoryResponse)
def delete_history_item(filename: str):
    if not filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only markdown history files are allowed")

    target = (HISTORY_DIR / filename).resolve()
    history_root = HISTORY_DIR.resolve()

    # Prevent path traversal outside the history directory.
    if history_root not in target.parents:
        raise HTTPException(status_code=400, detail="Invalid history filename")

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="History item not found")

    target.unlink()
    return DeleteHistoryResponse(
        status="deleted",
        message=f"Deleted {filename}",
        deleted_count=1,
    )


@app.delete("/api/history", response_model=DeleteHistoryResponse)
def clear_history():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    deleted = 0
    for file_path in HISTORY_DIR.glob("*.md"):
        if file_path.is_file():
            file_path.unlink()
            deleted += 1

    return DeleteHistoryResponse(
        status="deleted",
        message="History cleared",
        deleted_count=deleted,
    )


def _extract_status(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("**Status:**"):
            return line.replace("**Status:**", "").strip()
    return fallback


def _extract_timestamp(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("**Date:**"):
            return line.replace("**Date:**", "").strip()

    try:
        parsed = datetime.strptime(fallback, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return fallback


def _extract_content(text: str) -> str:
    if "---" not in text:
        return text.strip()

    parts = text.split("---", 1)
    if len(parts) < 2:
        return text.strip()
    return parts[1].strip()
