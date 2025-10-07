kcat > README.md <<'MD'
# Prodify (v0.1)

Turn weekend demos into a real app on Cloud Run, fast.

## Stack
- FastAPI on Cloud Run
- Identity Platform (email/password now; Google Sign-In enabled)
- Firestore (roles)
- Build: Cloud Buildpacks

## Endpoints
- Health: `GET /health`
- Protected: `GET /private` (needs `Authorization: Bearer <ID_TOKEN>`)
- Admin-only: `GET /admin` (requires Firestore doc `roles/<user_id> => { roles: ["admin"] }`)

## Deploy
```bash
gcloud run deploy hello-prodify --source . --allow-unauthenticated \
  --set-env-vars FIRESTORE_DB=prodifydb

