import { useEffect, useMemo, useRef, useState } from "react";

const API_BASE =
  import.meta.env.VITE_API_BASE ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

const PLATFORM_LABELS = {
  gfg: "GeeksforGeeks",
  linkedin: "LinkedIn",
  twitter: "Twitter/X",
};

export default function App() {
  const [rawText, setRawText] = useState("");
  const [preview, setPreview] = useState("");
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("compose");
  const [loadingRewrite, setLoadingRewrite] = useState(false);
  const [loadingPost, setLoadingPost] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [deletingFilename, setDeletingFilename] = useState("");
  const [clearingHistory, setClearingHistory] = useState(false);
  const [status, setStatus] = useState("Ready");

  const [selectedPlatform, setSelectedPlatform] = useState("gfg");
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const [credentialsByPlatform, setCredentialsByPlatform] = useState(() => ({
    gfg: {
      email: localStorage.getItem("gfg_email") || "",
      password: localStorage.getItem("gfg_password") || "",
    },
    linkedin: {
      email: localStorage.getItem("linkedin_email") || "",
      password: localStorage.getItem("linkedin_password") || "",
    },
    twitter: {
      email: localStorage.getItem("twitter_email") || "",
      password: localStorage.getItem("twitter_password") || "",
    },
  }));

  const listenAbortController = useRef(null);

  const charCount = useMemo(() => preview.length, [preview]);
  const currentCreds = credentialsByPlatform[selectedPlatform] || { email: "", password: "" };
  const isLoggedIn = Boolean(currentCreds.email && currentCreds.password);

  useEffect(() => {
    void loadHistory();
  }, []);

  async function loadHistory() {
    try {
      const response = await fetch(`${API_BASE}/api/history?limit=30`);
      if (!response.ok) {
        throw new Error("Unable to load history");
      }
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      setStatus(`History error: ${error.message}`);
    }
  }

  async function deleteHistoryItem(filename) {
    if (!filename) {
      return;
    }

    setDeletingFilename(filename);
    setStatus("Deleting history item...");

    try {
      const response = await fetch(`${API_BASE}/api/history/${encodeURIComponent(filename)}`, {
        method: "DELETE",
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Delete failed");
      }

      setStatus("History item deleted");
      await loadHistory();
    } catch (error) {
      setStatus(`Delete failed: ${error.message}`);
    } finally {
      setDeletingFilename("");
    }
  }

  async function clearAllHistory() {
    if (!window.confirm("Delete all history? This cannot be undone.")) {
      return;
    }

    setClearingHistory(true);
    setStatus("Clearing history...");

    try {
      const response = await fetch(`${API_BASE}/api/history`, {
        method: "DELETE",
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Clear history failed");
      }

      setStatus(`History cleared (${payload.deleted_count || 0} items removed)`);
      await loadHistory();
    } catch (error) {
      setStatus(`Clear failed: ${error.message}`);
    } finally {
      setClearingHistory(false);
    }
  }

  async function startListening() {
    if (isListening) {
      return;
    }

    const controller = new AbortController();
    listenAbortController.current = controller;
    setIsListening(true);
    setStatus("Listening... speak naturally. It will wait for long pauses.");

    try {
      const response = await fetch(`${API_BASE}/api/listen`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_timeout_seconds: 180,
          phrase_time_limit_seconds: 900,
        }),
        signal: controller.signal,
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Voice capture failed");
      }

      setRawText((prev) => {
        if (!prev.trim()) {
          return payload.text;
        }
        return `${prev}\n${payload.text}`;
      });
      setStatus("Voice captured successfully");
    } catch (error) {
      if (error.name === "AbortError") {
        setStatus("Listening stopped");
      } else {
        setStatus(`Voice error: ${error.message}`);
      }
    } finally {
      setIsListening(false);
      listenAbortController.current = null;
    }
  }

  function stopListening() {
    if (listenAbortController.current) {
      listenAbortController.current.abort();
    }
  }

  async function rewriteContent() {
    const text = rawText.trim();
    if (!text) {
      setStatus("Enter text first");
      return;
    }

    setLoadingRewrite(true);
    setStatus("Generating preview...");

    try {
      const response = await fetch(`${API_BASE}/api/rewrite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_text: text }),
      });

      if (!response.ok) {
        throw new Error("Rewrite request failed");
      }

      const data = await response.json();
      setPreview(data.preview || text);
      setStatus(data.provider_used === "ai" ? "AI rewrite complete" : "Using original text");
    } catch (error) {
      setPreview(text);
      setStatus(`Rewrite failed: ${error.message}`);
    } finally {
      setLoadingRewrite(false);
    }
  }

  async function publishPost() {
    if (!isLoggedIn) {
      setLoginEmail(currentCreds.email || "");
      setLoginPassword(currentCreds.password || "");
      setShowLoginModal(true);
      setStatus("Please login first");
      return;
    }

    const content = preview.trim();
    if (!content) {
      setStatus("Preview content is empty");
      return;
    }

    setLoadingPost(true);
    setStatus("Publishing...");

    try {
      const response = await fetch(`${API_BASE}/api/post`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content,
          platform: selectedPlatform,
          email: currentCreds.email,
          password: currentCreds.password,
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Publish failed");
      }

      setStatus(`Posted to ${PLATFORM_LABELS[selectedPlatform]} successfully`);
      setRawText("");
      setPreview("");
      await loadHistory();
      setActiveTab("history");
    } catch (error) {
      setStatus(`Publish failed: ${error.message}`);
    } finally {
      setLoadingPost(false);
    }
  }

  function handleLogin() {
    if (!loginEmail.trim() || !loginPassword.trim()) {
      setStatus("Email and password required");
      return;
    }

    const platform = selectedPlatform;
    localStorage.setItem(`${platform}_email`, loginEmail.trim());
    localStorage.setItem(`${platform}_password`, loginPassword);

    setCredentialsByPlatform((prev) => ({
      ...prev,
      [platform]: { email: loginEmail.trim(), password: loginPassword },
    }));

    setShowLoginModal(false);
    setLoginEmail("");
    setLoginPassword("");
    setStatus(`Logged in to ${PLATFORM_LABELS[platform]}`);
  }

  function handleLogout() {
    const platform = selectedPlatform;
    localStorage.removeItem(`${platform}_email`);
    localStorage.removeItem(`${platform}_password`);

    setCredentialsByPlatform((prev) => ({
      ...prev,
      [platform]: { email: "", password: "" },
    }));
    setStatus(`Logged out from ${PLATFORM_LABELS[platform]}`);
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="header-content">
          <div>
            <h1>GFG Connect Control</h1>
            <p>Mobile-first panel for rewrite, preview, publish, and history tracking.</p>
          </div>
          <div className="header-login">
            <div className="platform-selector">
              <label htmlFor="platform-select">Platform:</label>
              <select
                id="platform-select"
                value={selectedPlatform}
                onChange={(event) => setSelectedPlatform(event.target.value)}
              >
                <option value="gfg">GeeksforGeeks</option>
                <option value="linkedin">LinkedIn</option>
                <option value="twitter">Twitter/X</option>
              </select>
            </div>

            {isLoggedIn ? (
              <div className="logout-section">
                <span className="user-email">{currentCreds.email}</span>
                <button className="ghost logout-btn" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            ) : (
              <button
                className="ghost login-btn"
                onClick={() => {
                  setLoginEmail(currentCreds.email || "");
                  setLoginPassword(currentCreds.password || "");
                  setShowLoginModal(true);
                }}
              >
                Login
              </button>
            )}
          </div>
        </div>
      </header>

      <nav className="tabs" aria-label="Sections">
        <button
          className={activeTab === "compose" ? "tab tab-active" : "tab"}
          onClick={() => setActiveTab("compose")}
        >
          Compose
        </button>
        <button
          className={activeTab === "history" ? "tab tab-active" : "tab"}
          onClick={() => {
            setActiveTab("history");
            void loadHistory();
          }}
        >
          History
        </button>
      </nav>

      {activeTab === "compose" ? (
        <section className="panel">
          <div className="label-row">
            <label htmlFor="raw">Raw learning notes</label>
            <div className="mic-controls">
              {!isListening ? (
                <button className="mic-btn" onClick={startListening} type="button">
                  <span className="mic-dot" />
                  Speak
                </button>
              ) : (
                <button className="mic-btn mic-active" onClick={stopListening} type="button">
                  <span className="mic-dot" />
                  Listening... Tap to Stop
                </button>
              )}
            </div>
          </div>

          <textarea
            id="raw"
            value={rawText}
            onChange={(event) => setRawText(event.target.value)}
            placeholder="Paste, type, or use Speak for microphone input..."
            rows={8}
          />

          <div className="row-buttons">
            <button disabled={loadingRewrite} onClick={rewriteContent}>
              {loadingRewrite ? "Rewriting..." : "Rewrite"}
            </button>
            <button
              className="ghost"
              onClick={() => {
                setPreview(rawText);
                setStatus("Raw text copied to preview");
              }}
            >
              Use Raw
            </button>
          </div>

          <label htmlFor="preview">Preview (editable)</label>
          <textarea
            id="preview"
            value={preview}
            onChange={(event) => setPreview(event.target.value)}
            placeholder="Your final post preview will appear here..."
            rows={8}
          />

          <div className="row-buttons">
            <button
              className="ghost"
              onClick={() => {
                setPreview("");
                setRawText("");
                setStatus("Cleared all");
              }}
            >
              Cancel
            </button>
            <button onClick={rewriteContent} disabled={loadingRewrite}>
              {loadingRewrite ? "Rewriting..." : "Rewrite"}
            </button>
          </div>

          <div className="row-meta">
            <span>{charCount} characters</span>
            <button className="publish" disabled={loadingPost || !preview.trim()} onClick={publishPost}>
              {loadingPost ? "Posting..." : "Post"}
            </button>
          </div>
        </section>
      ) : (
        <section className="panel">
          <div className="row-meta">
            <h2>Recent posts</h2>
            <div className="history-actions">
              <button className="ghost" onClick={() => void loadHistory()}>
                Refresh
              </button>
              <button className="danger" disabled={clearingHistory || history.length === 0} onClick={clearAllHistory}>
                {clearingHistory ? "Clearing..." : "Clear All"}
              </button>
            </div>
          </div>

          <div className="history-list">
            {history.length === 0 ? (
              <p className="empty">No history yet.</p>
            ) : (
              history.map((item) => (
                <article key={item.filename} className="history-item">
                  <div className="row-meta">
                    <strong>{item.status.toUpperCase()}</strong>
                    <span>{item.timestamp}</span>
                  </div>
                  <p>{item.content}</p>
                  <div className="history-item-actions">
                    <button
                      className="danger subtle"
                      onClick={() => void deleteHistoryItem(item.filename)}
                      disabled={deletingFilename === item.filename || clearingHistory}
                    >
                      {deletingFilename === item.filename ? "Deleting..." : "Delete"}
                    </button>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      )}

      <footer className="status">{status}</footer>

      {showLoginModal && (
        <div className="modal-overlay" onClick={() => setShowLoginModal(false)}>
          <div className="modal-content" onClick={(event) => event.stopPropagation()}>
            <h2>Login to {PLATFORM_LABELS[selectedPlatform]}</h2>
            <p>Enter your credentials to enable automated posting.</p>

            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              value={loginEmail}
              onChange={(event) => setLoginEmail(event.target.value)}
              placeholder="your.email@example.com"
            />

            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              value={loginPassword}
              onChange={(event) => setLoginPassword(event.target.value)}
              placeholder="********"
            />

            <div className="modal-buttons">
              <button className="ghost" onClick={() => setShowLoginModal(false)}>
                Cancel
              </button>
              <button onClick={handleLogin}>Save Login</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
