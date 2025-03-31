from fastapi import APIRouter, status
from sqlalchemy.testing.suite.test_reflection import users
from database import Session, engine
from schemas import SignUpModel
from models import User
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

session =Session(bind=engine)

@auth_router.get('/')
async def hello():
    return {"message": "Hellow World"}

@auth_router.post('/signup', response_model=SignUpModel, status_code=status.HTTP_201_CREATED)
async def signup(user:SignUpModel):
    db_email=session.query(User).filter(User.email ==user.email).first()

    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="User with the email already exists"
                             )

    db_username = session.query(User).filter(User.username == user.username).first()

    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="User with the username already exists"
                             )
    hashed_password = pwd_context.hash(user.password)
    new_user= User(
        username=user.username,
        email=user.email,
        password= hashed_password,
        is_active=user.is_active,
        is_staff=user.is_staff,
    )

    session.add(new_user)
    session.commit()
    return new_user