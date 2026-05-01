from passlib.context import CryptContext

# Use bcrypt consistently everywhere
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt - truncated to 72 bytes."""
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify plain password against hash - truncated to 72 bytes."""
    if not hashed_password:
        return False
    return pwd_context.verify(
        plain_password[:72],
        hashed_password
    )
