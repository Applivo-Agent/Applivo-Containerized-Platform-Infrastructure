"""
app/api/routes/auth.py
──────────────────────
Multi-user JWT authentication with refresh tokens and session management.
Supports registration, login, token refresh, and session management.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Literal

import structlog
from app.core.security import (
    get_password_hash,
    verify_password
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.models.subscription import PlanTier, PLAN_PRICES
from app.models.user import User, UserProfile, UserSession
from app.schemas import (
    UserCreate, UserOut, TokenResponse, LoginRequest, 
    GoogleLoginRequest, ForgotPasswordRequest, ResetPasswordRequest,
    MessageResponse, OTPVerifyRequest, AuthResponse, RegisterVerifyRequest
)
from app.services.otp_service import otp_service
from app.services.notification_service import NotificationService
from app.services.cache_service import CacheService

cache = CacheService()


router = APIRouter(prefix="/auth", tags=["Authentication"])
log = structlog.get_logger()

security = HTTPBearer(auto_error=False)

REFRESH_TOKEN_EXPIRE_DAYS = 30


def _format_plan_prices() -> str:
    starter = PLAN_PRICES.get(PlanTier.STARTER, 0) // 100  # Convert paise to rupees
    pro = PLAN_PRICES.get(PlanTier.PRO, 0) // 100
    premium = PLAN_PRICES.get(PlanTier.PREMIUM, 0) // 100
    return (
        f"Starter: INR {starter}/month\n"
        f"Pro: INR {pro}/month\n"
        f"Premium: INR {premium}/month"
    )


def _build_new_user_greeting(full_name: Optional[str]) -> tuple[str, str]:
    subject = "Welcome to Applivo 🎉"
    starter = PLAN_PRICES.get(PlanTier.STARTER, 19900) // 100  # Convert paise to rupees
    pro = PLAN_PRICES.get(PlanTier.PRO, 39900) // 100
    premium = PLAN_PRICES.get(PlanTier.PREMIUM, 59900) // 100
    body = (
        f"Hi {full_name or 'there'},\n\n"
        "Welcome to **Applivo** - we're excited to have you on board! 🎉\n\n"
        "Applivo is your **AI-powered career co-pilot**, designed to help you discover opportunities, "
        "manage applications, and land your next role faster - without the repetitive manual work.\n\n"
        "Instead of spending hours searching and applying, Applivo automates the heavy lifting so you can "
        "focus on preparing, improving, and succeeding.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🚀 What You Can Do with Applivo\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "• Discover personalized job opportunities tailored to your skills\n"
        "• Automatically match your resume with relevant roles\n"
        "• Track every application in one smart dashboard\n"
        "• Get AI-powered insights to improve your chances\n"
        "• Save time with automated job applications\n"
        "• Stay organized throughout your job search journey\n\n"
        "Whether you're applying for internships, entry-level roles, or advanced positions, "
        "Applivo helps you move faster and smarter.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💼 Choose the Plan That Fits Your Goal\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Starter - INR {starter} / month\n"
        "Perfect for getting started with essential job automation features.\n\n"
        f"Pro - INR {pro} / month\n"
        "Best for active job seekers who want faster applications and smarter matching.\n\n"
        f"Premium - INR {premium} / month\n"
        "Built for serious candidates who want full automation, priority processing, and advanced insights.\n\n"
        "You can compare all features and upgrade anytime directly from your dashboard.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🎯 Your Next Step\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "1. Complete your profile\n"
        "2. Upload or update your resume\n"
        "3. Set your job preferences\n"
        "4. Let Applivo start working for you\n\n"
        "The sooner you begin, the sooner opportunities start coming to you.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "We're here to support your journey every step of the way.\n\n"
        "Let's land your next opportunity together. 🚀\n\n"
        "Warm regards,\n"
        "Team Applivo\n\n"
        "Support: sudharsan97511@gmail.com\n"
        "Website: https://www.applivo.in"
    )
    return subject, body


def _build_welcome_back_message(full_name: Optional[str]) -> tuple[str, str]:
    subject = "Welcome back to Applivo 👋"
    body = (
        f"Hi {full_name or 'there'},\n\n"
        "Welcome back. You have successfully logged in to your Applivo account.\n"
        "If this wasn\'t you, please reset your password immediately."
    )
    return subject, body


async def _send_auth_notification(
    *,
    user: User,
    event_type: str,
    title: str,
    body: str,
    flow: str,
    send_email: bool = True,
    send_telegram: bool = True,
) -> None:
    try:
        await NotificationService().notify(
            title=title,
            body=body,
            event_type=event_type,
            user_id=user.id,
            send_email=send_email,
            send_telegram=send_telegram,
        )
        log.info(
            "Auth notification sent",
            user_id=user.id,
            email=user.email,
            event_type=event_type,
            flow=flow,
        )
    except Exception as e:
        log.warning(
            "Auth notification failed",
            user_id=user.id,
            email=user.email,
            event_type=event_type,
            flow=flow,
            error=str(e),
        )




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
        jti: str = payload.get("jti")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        if jti:
            try:
                if await cache.get(f"blacklist:{jti}"):
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
            except HTTPException:
                raise
            except Exception as e:
                log.warning("Token blacklist check failed", error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                    detail="Security verification unavailable. Please try again later."
                )
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

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Email verification required",
            headers={"X-Verification-Required": "true"}
        )


    user.last_login_at = datetime.now(timezone.utc)
    return user


@router.post("/register/initiate", response_model=AuthResponse)
async def register_initiate(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Initiate registration by sending OTP."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Generate and store OTP
    otp = otp_service.generate_otp()
    if not await otp_service.store_otp(data.email, "register", otp):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to send verification code. Please try again later."
        )

    # Send OTP email
    try:
        send_result = await NotificationService().send_email_to_user(
            subject="Verify your Applivo account 🚀",
            body=f"Your verification code is: {otp}\n\nThis code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.",
            to_email=data.email
        )
        if send_result.get("error"):
            raise RuntimeError(send_result["error"])
    except Exception as e:
        log.error("Failed to send registration OTP", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to send verification email. Please try again.")

    return AuthResponse(message="Verification code sent to your email", email=data.email)


@router.post("/register/verify", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_verify(
    data: RegisterVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify signup OTP and create user account."""
    is_valid = await otp_service.verify_otp(data.email, "register", data.otp)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired verification code")

    # Double check email uniqueness again before creation
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        is_active=True,
        is_verified=True,
        verified_at=datetime.now(timezone.utc)
    )
    db.add(user)
    await db.flush()

    profile = UserProfile(user_id=user.id)
    db.add(profile)
    await db.commit()
    await db.refresh(user)

    session = await create_session(db, user, device_id="default", device_name="Registration")
    refresh_tk = create_refresh_token(user.id, str(session.id))
    session.refresh_token_hash = get_password_hash(refresh_tk)
    session.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token, jti = create_access_token_with_jti(user.id, user.email)
    session.access_token_jti = jti
    await db.commit()

    greeting_subject, greeting_body = _build_new_user_greeting(user.full_name)
    try:
        send_result = await NotificationService().send_email_to_user(
            subject=greeting_subject,
            body=greeting_body,
            to_email=user.email,
        )
        if send_result.get("error"):
            log.warning("Welcome email direct send failed", user_id=user.id, email=user.email, error=send_result.get("error"))
    except Exception as e:
        log.warning("Welcome email direct send failed", user_id=user.id, email=user.email, error=str(e))

    await _send_auth_notification(
        user=user,
        event_type="user_registered_welcome",
        title=greeting_subject,
        body=greeting_body,
        flow="register_verify",
        send_email=False,
        send_telegram=True,
    )

    log.info("User verified and registered", user_id=user.id, email=user.email)
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_tk,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login/initiate", response_model=AuthResponse)
async def login_initiate(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Initiate login by validating password and sending OTP."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        log.warning("Login attempt failed", email=data.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    # Generate and store OTP
    otp = otp_service.generate_otp()
    if not await otp_service.store_otp(data.email, "login", otp):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to send verification code. Please try again later."
        )

    # Send OTP email
    try:
        send_result = await NotificationService().send_email_to_user(
            subject="Your Applivo Login Code 🔑",
            body=f"Your login verification code is: {otp}\n\nThis code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.",
            to_email=data.email
        )
        if send_result.get("error"):
            raise RuntimeError(send_result["error"])
    except Exception as e:
        log.error("Failed to send login OTP", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to send verification email. Please try again.")

    return AuthResponse(message="Verification code sent to your email", email=data.email)


@router.post("/login/verify", response_model=TokenResponse)
async def login_verify(data: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    """Verify login OTP and return tokens."""
    if data.purpose != "login":
        raise HTTPException(status_code=400, detail="Invalid purpose")

    is_valid = await otp_service.verify_otp(data.email, "login", data.otp)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired verification code")

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    previous_last_login_at = user.last_login_at
    user.last_login_at = datetime.now(timezone.utc)
    if not user.is_verified:
        user.is_verified = True
        user.verified_at = datetime.now(timezone.utc)
    
    await db.commit()

    session = await create_session(db, user, device_id="default", device_name="Login")
    refresh_tk = create_refresh_token(user.id, str(session.id))
    session.refresh_token_hash = get_password_hash(refresh_tk)
    session.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token, jti = create_access_token_with_jti(user.id, user.email)
    session.access_token_jti = jti
    await db.commit()

    if previous_last_login_at:
        welcome_subject, welcome_body = _build_welcome_back_message(user.full_name)
        await _send_auth_notification(
            user=user,
            event_type="user_login_welcome_back",
            title=welcome_subject,
            body=welcome_body,
            flow="login_verify",
        )

    log.info("User logged in after OTP", user_id=user.id, email=user.email)
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_tk,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/otp/resend", response_model=AuthResponse)
async def resend_otp(email: str, purpose: Literal["login", "register"], db: AsyncSession = Depends(get_db)):
    """Resend OTP code."""
    # Logic to resend OTP
    otp = otp_service.generate_otp()
    await otp_service.store_otp(email, purpose, otp)
    
    try:
        send_result = await NotificationService().send_email_to_user(
            subject=f"Your Applivo {'Registration' if purpose == 'register' else 'Login'} Code",
            body=f"Your verification code is: {otp}\n\nThis code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.",
            to_email=email
        )
        if send_result.get("error"):
            raise RuntimeError(send_result["error"])
    except Exception as e:
        log.error("Failed to resend OTP", email=email, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to send verification email.")

    return AuthResponse(message="A new verification code has been sent", email=email)



@router.post("/google", response_model=TokenResponse)
async def google_login(data: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    """Login or register using Google ID Token."""
    from google.oauth2 import id_token
    from google.auth.transport import requests

    try:
        # Verify the ID Token
        idinfo = id_token.verify_oauth2_token(
            data.id_token, requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        
        google_id = idinfo["sub"]
        email = idinfo["email"]
        full_name = idinfo.get("name", "Google User")
    except Exception as e:
        log.error("Google token verification failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    is_new_user = False

    # 1. Try to find user by google_id
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    # 2. If not found by google_id, try by email
    if not user:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            # Link existing account to google_id
            user.google_id = google_id
            await db.commit()

    # 3. If still not found, create new user
    if not user:
        user = User(
            email=email,
            hashed_password="oauth_managed",  # Dummy password for social-only accounts
            full_name=full_name,
            google_id=google_id,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(user)
        is_new_user = True
        log.info("New user created via Google", user_id=user.id, email=email)

    previous_last_login_at = user.last_login_at
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    # Standard session creation
    session = await create_session(db, user, device_id="google_oauth", device_name="Google Auth")
    refresh_tk = create_refresh_token(user.id, str(session.id))
    session.refresh_token_hash = get_password_hash(refresh_tk)
    session.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token, jti = create_access_token_with_jti(user.id, user.email)
    session.access_token_jti = jti
    await db.commit()

    if is_new_user:
        greeting_subject, greeting_body = _build_new_user_greeting(user.full_name)
        await _send_auth_notification(
            user=user,
            event_type="user_registered_welcome",
            title=greeting_subject,
            body=greeting_body,
            flow="google_login",
        )
    elif previous_last_login_at:
        welcome_subject, welcome_body = _build_welcome_back_message(user.full_name)
        await _send_auth_notification(
            user=user,
            event_type="user_login_welcome_back",
            title=welcome_subject,
            body=welcome_body,
            flow="google_login",
        )

    log.info("User logged in via Google", user_id=user.id, email=user.email)
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_tk,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Send a password reset link to the user's email."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        # For security, don't confirm if the email exists, but we'll return a success message regardless
        return MessageResponse(message="If your email is registered, you will receive a reset link shortly.")

    # Generate a secure token
    import secrets
    token = secrets.token_urlsafe(32)
    user.password_reset_token = token
    user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    await db.commit()

    # Send email
    try:
        from app.services.notification_service import NotificationService
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        await NotificationService().notify(
            title="Reset Your Password 🔒",
            body=f"""Hi {user.full_name or 'there'},

You recently requested to reset your password for your Applivo account. Click the link below to set a new password:

{reset_link}

This link will expire in 1 hour. If you didn't request this, you can safely ignore this email.

— Team Applivo""",
            event_type="password_reset",
            user_id=user.id,
        )
    except Exception as e:
        log.error("Failed to send reset email", error=str(e))

    return MessageResponse(message="If your email is registered, you will receive a reset link shortly.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using a valid token."""
    result = await db.execute(
        select(User).where(
            and_(
                User.password_reset_token == data.token,
                User.password_reset_expires_at > datetime.now(timezone.utc)
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Update password
    user.hashed_password = get_password_hash(data.new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    await db.commit()

    log.info("Password reset successful", user_id=user.id)
    return MessageResponse(message="Your password has been reset successfully. You can now log in with your new password.")


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
    
    # Check if session with this device_id already exists and update instead of create
    existing = await db.execute(
        select(UserSession).where(
            and_(UserSession.user_id == user.id, UserSession.device_id == device_id)
        )
    )
    existing_session = existing.scalar_one_or_none()
    
    if existing_session:
        existing_session.is_current = True
        existing_session.is_active = True
        existing_session.last_used_at = datetime.now(timezone.utc)
        await db.flush()
        return existing_session
    
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
        last_used_at=datetime.now(timezone.utc),
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


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


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

    # ── Refresh Token Rotation ──────────────────────────
    new_refresh_tk = create_refresh_token(user.id, str(session.id))
    session.refresh_token_hash = get_password_hash(new_refresh_tk)
    session.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    # ───────────────────────────────────────────────────

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_tk,
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


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change password for authenticated user."""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    if data.current_password == data.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    if len(data.new_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be at least 8 characters")

    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()

    log.info("Password changed", user_id=current_user.id)
    return MessageResponse(message="Password updated successfully")


@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """Logout current user and invalidate JWT token."""
    if credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            jti: str = payload.get("jti")
            exp: int = payload.get("exp", 0)
            
            if jti:
                try:
                    # Blacklist current token using TTL
                    ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
                    if ttl > 0:
                        await cache.set(f"blacklist:{jti}", "1", expire=ttl)
                except Exception as e:
                    log.error("Failed to add token to blacklist", error=str(e))
                    # Still allow logout but log critical error
        except JWTError:
            pass
    
    return {"success": True, "message": "Logged out successfully"}
