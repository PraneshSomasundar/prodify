from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from app.auth import verify_bearer_token
from app.roles import get_roles

app = FastAPI(title="Prodify", version="0.1")

# ---------- Public ----------
# Support both GET and HEAD on "/"
@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def home():
    return """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <title>Prodify is live</title>
        <style>
          body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 40px; }
          .card { max-width: 720px; margin: 0 auto; padding: 24px; border: 1px solid #eee; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); }
          h1 { margin: 0 0 12px; }
          code, pre { background: #f6f8fa; padding: 2px 6px; border-radius: 6px; }
          ul { line-height: 1.8; }
          .muted { color: #666; font-size: 14px; }
          a { color: #0d62ff; text-decoration: none; }
          a:hover { text-decoration: underline; }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>🚢 Prodify is live on Cloud Run</h1>
          <p>Your backend is running. Useful links:</p>
          <ul>
            <li><a href="/docs">OpenAPI docs</a> (interactive)</li>
            <li><a href="/health">/health</a> (health check JSON)</li>
            <li><code>GET /private</code> — requires <code>Authorization: Bearer &lt;ID_TOKEN&gt;</code></li>
            <li><code>GET /admin</code> — same as above, plus Firestore role <code>admin</code></li>
          </ul>
          <p class="muted">Tip: curl your service URL with <code>/health</code> to check status.</p>
        </div>
      </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ---------- Auth-protected ----------
@app.get("/private")
def private(claims: dict = Depends(verify_bearer_token)):
    return {
        "message": "Welcome to the private endpoint!",
        "email": claims.get("email", "(no email)"),
        "user_id": claims.get("user_id") or claims.get("sub"),
        "issuer": claims.get("iss"),
        "audience": claims.get("aud"),
    }

