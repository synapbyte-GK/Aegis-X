from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import bcrypt

from database import SessionLocal
from auth.models import UserDB


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# JWT configuration
SECRET_KEY = "aegis-x-development-secret-change-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    user = (
        db.query(UserDB)
        .filter(UserDB.id == user_id)
        .first()
    )

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    return user


@router.post("/register")
def register_user(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(UserDB)
        .filter(UserDB.email == data.email.lower())
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User already registered",
        )

    user = UserDB(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        },
    }


@router.post("/login")
def login_user(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(UserDB)
        .filter(UserDB.email == data.email.lower())
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        },
    }


@router.get("/me")
def get_my_profile(
    current_user: UserDB = Depends(get_current_user),
):
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
        }
    }