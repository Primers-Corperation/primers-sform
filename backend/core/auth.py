import os
import time
import hashlib
import json
from typing import Optional

# Sovereign operator registry
# In production this moves to a secure database — for now, sovereign local store
OPERATOR_REGISTRY = {
    "admin": {
        "password_hash": hashlib.sha256("sip-admin-2024".encode()).hexdigest(),
        "tier": 3,
        "role": "ADMIN",
        "name": "System Administrator",
        "clearance": "TOP SECRET"
    },
    "analyst": {
        "password_hash": hashlib.sha256("sip-analyst-2024".encode()).hexdigest(),
        "tier": 2,
        "role": "ANALYST",
        "name": "Intelligence Analyst",
        "clearance": "SECRET"
    },
    "operator": {
        "password_hash": hashlib.sha256("sip-operator-2024".encode()).hexdigest(),
        "tier": 1,
        "role": "FIELD OPERATOR",
        "name": "Field Operator",
        "clearance": "RESTRICTED"
    }
}

TIER_PERMISSIONS = {
    1: ["triage", "voice_guardian", "view_alerts"],
    2: ["triage", "voice_guardian", "view_alerts", "detr_scan", "export_report"],
    3: ["triage", "voice_guardian", "view_alerts", "detr_scan", "export_report", "system_health", "manage_users"]
}

# Sovereign session store — in-memory, no external dependency
_sessions: dict = {}

def authenticate(username: str, password: str) -> Optional[dict]:
    user = OPERATOR_REGISTRY.get(username)
    if not user:
        return None
    if user["password_hash"] != hashlib.sha256(password.encode()).hexdigest():
        return None
    
    # Generate sovereign session token
    token = hashlib.sha256(
        f"{username}{time.time()}{os.urandom(16).hex()}".encode()
    ).hexdigest()
    
    session = {
        "token": token,
        "username": username,
        "tier": user["tier"],
        "role": user["role"],
        "name": user["name"],
        "clearance": user["clearance"],
        "permissions": TIER_PERMISSIONS[user["tier"]],
        "issued_at": time.time(),
        "expires_at": time.time() + (8 * 3600)  # 8-hour duty cycle
    }
    _sessions[token] = session
    return session

def validate_token(token: str) -> Optional[dict]:
    session = _sessions.get(token)
    if not session:
        return None
    if time.time() > session["expires_at"]:
        del _sessions[token]
        return None
    return session

def require_permission(token: str, permission: str) -> bool:
    session = validate_token(token)
    if not session:
        return False
    return permission in session.get("permissions", [])

def revoke_token(token: str):
    _sessions.pop(token, None)
