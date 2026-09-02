"""
DisputeSentinel AI — Tests for Core Security
"""

import hmac
import hashlib
from backend.app.core.security import verify_webhook_signature

def test_verify_webhook_signature_success():
    """Test valid HMAC-SHA256 signature verification."""
    secret = "whsec_test_secret_for_development"
    payload = b'{"event":"dispute.created"}'
    
    # Generate valid signature
    valid_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()
    
    assert verify_webhook_signature(payload, valid_signature, secret) is True

def test_verify_webhook_signature_invalid():
    """Test invalid HMAC-SHA256 signature rejection."""
    secret = "whsec_test_secret_for_development"
    payload = b'{"event":"dispute.created"}'
    
    invalid_signature = "a" * 64
    
    assert verify_webhook_signature(payload, invalid_signature, secret) is False

def test_verify_webhook_signature_wrong_secret():
    """Test signature verification with incorrect secret."""
    secret = "whsec_test_secret_for_development"
    wrong_secret = "wrong_secret"
    payload = b'{"event":"dispute.created"}'
    
    signature_with_wrong_secret = hmac.new(
        key=wrong_secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()
    
    assert verify_webhook_signature(payload, signature_with_wrong_secret, secret) is False
