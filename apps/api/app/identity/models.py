import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, JSON, BigInteger
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    """User entity matching blueprints/03-data-model.sql & 03b-data-model-v2.sql."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    is_system_admin = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="active", nullable=False)  # active | disabled | invited
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class InstanceSetting(Base):
    """Global instance configuration matching blueprints/03b-data-model-v2.sql."""
    __tablename__ = "instance_settings"

    key = Column(String(100), primary_key=True)  # access_mode, registration, etc.
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class AuthMagicLink(Base):
    """Auth magic link tokens matching blueprints/03b-data-model-v2.sql."""
    __tablename__ = "auth_magic_links"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)


class AuthSession(Base):
    """Server-side revocable session matching blueprints/03b-data-model-v2.sql."""
    __tablename__ = "auth_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    idle_expires_at = Column(DateTime(timezone=True), nullable=False)
    abs_expires_at = Column(DateTime(timezone=True), nullable=False)
    step_up_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip = Column(String(100), nullable=True)


class WebauthnCredential(Base):
    """FIDO2 / Passkey credentials matching blueprints/03b-data-model-v2.sql."""
    __tablename__ = "webauthn_credentials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    credential_id = Column(String(255), unique=True, nullable=False, index=True)
    public_key = Column(String(500), nullable=False)
    sign_count = Column(BigInteger, default=0, nullable=False)
    transports = Column(JSON, nullable=True)  # ['internal', 'usb', 'ble', 'nfc']
    label = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)


class RecoveryCode(Base):
    """Account recovery codes matching blueprints/03b-data-model-v2.sql."""
    __tablename__ = "recovery_codes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code_hash = Column(String(64), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)

