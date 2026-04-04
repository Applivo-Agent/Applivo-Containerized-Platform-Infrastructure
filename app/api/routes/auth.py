"""
app/api/routes/auth.py
──────────────────────
Multi-user JWT authentication with refresh tokens and session management.
Supports registration, login, token refresh, and session management.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, List

import structlog
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserProfile, UserSession
from app.schemas import UserCreate, UserOut, TokenResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])
log = structlog.get_logger()

security = HTTPBearer(auto_error=False)

REFRESH_TOKEN_EXPIRE_DAYS = 30

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: str, email: str) -> TokenResponse:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return TokenResponse(
        access_token=token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate the current user from the JWT token.
    Raises 401 if token is missing, invalid, or user is inactive.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    user.last_login_at = datetime.now(timezone.utc)
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    profile = UserProfile(user_id=user.id)
    db.add(profile)
    await db.commit()
    await db.refresh(user)

    session = await create_session(db, user, device_id="default", device_name="Registration")
    refresh_tk = create_refresh_token(user.id, str(session.id))
    session.refresh_token_hash = hash_password(refresh_tk)
    session.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token, jti = create_access_token_with_jti(user.id, user.email)
    session.access_token_jti = jti
    await db.commit()

    try:
        from app.services.notification_service import NotificationService
        await NotificationService().notify(
            title="Welcome to Applivo! 🚀",
            body=f"""Hi {user.full_name or 'there'},

We're excited to have you on board! Your account has been successfully created, and you're now ready to begin your smarter, faster job search journey with Applivo.

Here's how to get started:
• Complete your profile with your skills, experience, and preferred job roles
• Upload your resume so our AI can tailor applications for you
• Explore job matches curated specifically for your profile
• Enable automation to let Applivo apply to opportunities on your behalf
• Track your applications, interviews, and progress from one simple dashboard

Our system will continuously search for relevant opportunities, prepare applications, and keep you updated every step of the way.

If you ever need assistance, simply reply to this email or visit your dashboard.

We're here to support your success.

— Team Applivo""",
            event_type="user_signup",
            user_id=user.id,
        )
    except Exception:
        pass

    log.info("User registered", user_id=user.id, email=user.email)
    return TokenResponse(access_token=access_token, expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    session = await create_session(db, user, device_id="default", device_name="Login")
    refresh_tk = create_refresh_token(user.id, str(session.id))
    session.refresh_token_hash = hash_password(refresh_tk)
    session.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token, jti = create_access_token_with_jti(user.id, user.email)
    session.access_token_jti = jti
    await db.commit()

    try:
        from app.services.notification_service import NotificationService
        await NotificationService().notify(
            title="Welcome back, Sudharsan! 👋",
            body=f"""It's great to have you here again. New opportunities are waiting, and Applivo is ready to help you apply smarter, prepare better, and move one step closer to your next career milestone.

Let's get started!""",
            event_type="user_login",
            user_id=user.id,
        )
    except Exception:
        pass

    log.info("User logged in", user_id=user.id, email=user.email)
    return TokenResponse(access_token=access_token, expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.get("/status")
async def auth_status(current_user: User = Depends(get_current_user)):
    """Check authentication status."""
    return {
        "authenticated": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
    }


def create_refresh_token(user_id: str, session_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "session_id": session_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token_with_jti(user_id: str, email: str) -> tuple[str, str]:
    import uuid
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": jti,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti


async def create_session(
    db: AsyncSession,
    user: User,
    device_id: str,
    device_name: Optional[str] = None,
    device_type: Optional[str] = None,
    browser: Optional[str] = None,
    os: Optional[str] = None,
    ip_address: Optional[str] = None,
    location: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UserSession:
    await db.execute(
        update(UserSession).where(
            and_(UserSession.user_id == user.id, UserSession.is_current == True)
        ).values(is_current=False)
    )
    
    session = UserSession(
        user_id=user.id,
        device_id=device_id,
        device_name=device_name,
        device_type=device_type,
        browser=browser,
        os=os,
        ip_address=ip_address,
        location=location,
        user_agent=user_agent,
        is_current=True,
        is_active=True,
    )
    db.add(session)
    await db.flush()
    return session


class SessionOut(BaseModel):
    id: str
    device_name: Optional[str]
    device_type: Optional[str]
    browser: Optional[str]
    os: Optional[str]
    ip_address: Optional[str]
    location: Optional[str]
    is_current: bool
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


class RefreshRequest(BaseModel):
    refresh_token: str


class SessionCreateRequest(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    user_agent: Optional[str] = None


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(
            data.refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        session_id = payload.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    session_result = await db.execute(
        select(UserSession).where(
            and_(
                UserSession.id == session_id,
                UserSession.user_id == user_id,
                UserSession.is_active == True,
            )
        )
    )
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=401, detail="Session no longer active")

    if session.refresh_token_expires_at and session.refresh_token_expires_at < datetime.now(timezone.utc):
        session.is_active = False
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    access_token, jti = create_access_token_with_jti(user.id, user.email)
    session.access_token_jti = jti
    session.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/sessions", response_model=List[SessionOut])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all active sessions for the current user."""
    result = await db.execute(
        select(UserSession)
        .where(
            and_(
                UserSession.user_id == current_user.id,
                UserSession.is_active == True,
            )
        )
        .order_by(UserSession.created_at.desc())
    )
    sessions = result.scalars().all()
    
    return [
        SessionOut(
            id=str(s.id),
            device_name=s.device_name,
            device_type=s.device_type,
            browser=s.browser,
            os=s.os,
            ip_address=s.ip_address,
            location=s.location,
            is_current=s.is_current,
            is_active=s.is_active,
            created_at=s.created_at,
            last_used_at=s.last_used_at,
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke a specific session."""
    result = await db.execute(
        select(UserSession).where(
            and_(
                UserSession.id == session_id,
                UserSession.user_id == current_user.id,
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.is_current:
        raise HTTPException(status_code=400, detail="Cannot revoke current session")
    
    session.is_active = False
    await db.commit()
    
    return {"success": True, "message": "Session revoked"}


@router.delete("/sessions")
async def revoke_all_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke all sessions except the current one."""
    await db.execute(
        update(UserSession).where(
            and_(
                UserSession.user_id == current_user.id,
                UserSession.is_current == False,
                UserSession.is_active == True,
            )
        ).values(is_active=False)
    )
    await db.commit()
    
    return {"success": True, "message": "All other sessions revoked"}


from sqlalchemy import update
