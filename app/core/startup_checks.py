from app.core.security import get_password_hash, verify_password
import structlog

logger = structlog.get_logger()

def check_hashing():
    """Verify that password hashing works correctly on startup."""
    test_pwd = "production_test_123"
    hashed = get_password_hash(test_pwd)

    if not verify_password(test_pwd, hashed):
        logger.error("FATAL: Password hashing verification failed during startup check!")
        raise RuntimeError("Password hashing misconfigured")
    
    logger.info("Security check: Password hashing verified")
