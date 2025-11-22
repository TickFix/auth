from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from app.db import AsyncSession
from sqlalchemy import select
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession as ASyncSessionType
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession as SessionClass
from sqlalchemy.orm import sessionmaker

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 60*24

class RegisterIn(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone: str | None
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(payload: RegisterIn):
    async with AsyncSession() as session:
        q = await session.execute(select(User).where(User.email == payload.email))
        if q.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="email already registered.")
        user = User(
            firstname=payload.firstname,
            lastname=payload.lastname,
            email=payload.email,
            phone=payload.phone,
            password_hash=pwd_context.hash(payload.password),
        )
        session.add(user)
        await session.commit()
        return {"msg": "user registered"}

@router.post("/login")
async def login(payload: LoginIn):
    async with AsyncSession() as session:
        q = await session.execute(select(User).where(User.email == payload.email))
        user = q.scalar_one_or_none()
        if not user or not pwd_context.verify(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="invalid credentials")
        token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
