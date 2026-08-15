from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
import bcrypt

def get_user(db: Session, user_id: int):
    return db.execute(select(User).filter(User.user_id == user_id)).scalars().first()

def get_user_by_email(db: Session, email: str):
    return db.execute(select(User).filter(User.email == email)).scalars().first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.execute(select(User).offset(skip).limit(limit)).scalars().all()

def create_user(db: Session, user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        is_active=user.is_active,
        physical_info=user.physical_info
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
