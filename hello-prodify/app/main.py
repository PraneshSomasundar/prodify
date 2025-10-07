from fastapi import FastAPI, Depends, HTTPException, status
from app.auth import verify_bearer_token
from app.roles import get_roles

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Prodify on Cloud Run!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# Any signed-in user
@app.get("/private")
def private(claims: dict = Depends(verify_bearer_token)):
    return {
        "message": "Welcome to the private endpoint!",
        "email": claims.get("email", "(no email)"),
        "user_id": claims.get("user_id") or claims.get("sub"),
        "issuer": claims.get("iss"),
        "audience": claims.get("aud"),
    }

def require_role(role: str):
    def _dep(claims: dict = Depends(verify_bearer_token)):
        user_id = claims.get("user_id") or claims.get("sub")
        roles = get_roles(user_id)
        if role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: missing role")
        return {"claims": claims, "roles": roles}
    return _dep

# Admin-only
@app.get("/admin")
def admin(_ctx: dict = Depends(require_role("admin"))):
    return {"ok": True, "roles": _ctx["roles"]}

