import hmac
import hashlib
import time
import base64
from typing import Optional
from app.core.config import settings

TOKEN_TTL_SECONDS = 900  # 15 minutes per ENG-007


def create_magic_link_token(email: str) -> str:
    """Generate a single-use 15-minute magic link token with HMAC signature."""
    now = int(time.time())
    payload = f"{email}:{now}"
    sig = hmac.new(settings.SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    b64_payload = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    b64_sig = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{b64_payload}.{b64_sig}"


def verify_magic_link_token(token: str) -> Optional[str]:
    """Verify magic link signature and expiration (<= 15 minutes). Returns email or None."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        b64_payload, b64_sig = parts
        
        # Add padding back
        pad_payload = b64_payload + "=" * (-len(b64_payload) % 4)
        pad_sig = b64_sig + "=" * (-len(b64_sig) % 4)
        
        payload = base64.urlsafe_b64decode(pad_payload).decode()
        sig = base64.urlsafe_b64decode(pad_sig)
        
        expected_sig = hmac.new(settings.SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        
        email, ts_str = payload.rsplit(":", 1)
        created_at = int(ts_str)
        if time.time() - created_at > TOKEN_TTL_SECONDS:
            return None
            
        return email
    except Exception:
        return None


def create_session_token(user_id: str) -> str:
    """Creates a secure session token for session cookies."""
    now = int(time.time())
    payload = f"{user_id}:{now}"
    sig = hmac.new(settings.SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    b64_payload = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    b64_sig = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{b64_payload}.{b64_sig}"


def verify_session_token(token: str) -> Optional[str]:
    """Verifies a session cookie token and returns user_id if valid."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        b64_payload, b64_sig = parts
        
        pad_payload = b64_payload + "=" * (-len(b64_payload) % 4)
        pad_sig = b64_sig + "=" * (-len(b64_sig) % 4)
        
        payload = base64.urlsafe_b64decode(pad_payload).decode()
        sig = base64.urlsafe_b64decode(pad_sig)
        
        expected_sig = hmac.new(settings.SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
            
        user_id, ts_str = payload.rsplit(":", 1)
        created_at = int(ts_str)
        # Max session duration: 7 days (604,800s). Reject ancient or future timestamps.
        if (time.time() - created_at > 604800) or (created_at > time.time() + 60):
            return None
        return user_id
    except Exception:
        return None
