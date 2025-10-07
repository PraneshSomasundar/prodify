import os
from functools import lru_cache
from typing import List
from google.cloud import firestore

DB_ID = os.getenv("FIRESTORE_DB", "(default)")

@lru_cache()
def _db():
    # Uses Cloud Run's default credentials
    return firestore.Client(database=DB_ID)

def get_roles(user_id: str) -> List[str]:
    doc = _db().collection("roles").document(user_id).get()
    if doc.exists:
        data = doc.to_dict() or {}
        return data.get("roles", [])
    return []

def set_roles(user_id: str, roles: List[str]) -> None:
    _db().collection("roles").document(user_id).set({"roles": roles}, merge=True)

