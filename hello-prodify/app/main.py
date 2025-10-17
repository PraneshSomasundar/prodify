import os
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from google.cloud import firestore

from app.auth import verify_bearer_token
from app.roles import get_roles

app = FastAPI(title="Prodify", version="0.1")

# ---- Firestore client ----
FIRESTORE_DB = os.getenv("FIRESTORE_DB", "(default)")
_db = firestore.Client(database=FIRESTORE_DB)

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
          form { margin-top: 16px; display: flex; gap: 8px; }
          input[type=email] { flex: 1; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; }
          button { padding: 10px 14px; border: 0; border-radius: 8px; background: #0d62ff; color: white; cursor: pointer; }
          .ok { color: #1a7f37; }
          .err { color: #b3261e; }
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

          <h3>Get early access</h3>
          <p class="muted">Drop your email — we’ll send the first templates & docs.</p>
          <form id="wl-form">
            <input id="wl-email" type="email" placeholder="you@example.com" required />
            <button type="submit">Notify me</button>
          </form>
          <p id="wl-msg" class="muted"></p>

          <script>
            const f = document.getElementById('wl-form');
            const em = document.getElementById('wl-email');
            const msg = document.getElementById('wl-msg');
            f.addEventListener('submit', async (e) => {
              e.preventDefault();
              msg.textContent = 'Submitting...';
              try {
                const res = await fetch('/subscribe', {
                  method: 'POST',
                  headers: {'Content-Type': 'application/json'},
                  body: JSON.stringify({ email: em.value })
                });
                const j = await res.json();
                if (res.ok && j.ok) {
                  msg.textContent = 'Thanks! You are on the list.';
                  msg.className = 'ok';
                  em.value = '';
                } else {
                  msg.textContent = (j.detail || 'Something went wrong.');
                  msg.className = 'err';
                }
              } catch (err) {
                msg.textContent = 'Network error. Try again.';
                msg.className = 'err';
              }
            });
          </script>

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

# ---------- Waitlist ----------
class SubscribeIn(BaseModel):
    email: EmailStr

@app.post("/subscribe")
def subscribe(payload: SubscribeIn, request: Request):
    email = payload.email.lower()
    # Use email as doc id to keep it unique/idempotent
    _db.collection("waiting_list").document(email).set({
        "email": email,
        "ua": request.headers.get("user-agent", ""),
        "ts": firestore.SERVER_TIMESTAMP
    }, merge=True)
    return {"ok": True}

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

@app.get("/admin")
def admin(claims: dict = Depends(verify_bearer_token)):
    uid = claims.get("user_id") or claims.get("sub")
    roles = get_roles(uid)
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admins only")
    return {"ok": True, "roles": roles}
