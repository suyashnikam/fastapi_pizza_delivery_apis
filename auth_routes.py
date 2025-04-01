from fastapi import APIRouter, status, Depends
from sqlalchemy.testing.suite.test_reflection import users
from database import Session, engine
from schemas import SignUpModel, LoginModel
from models import User
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
from fastapi_jwt_auth import AuthJWT

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

session =Session(bind=engine)

@auth_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

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

#login route
@auth_router.post('/login',status_code=200)
async def login(user: LoginModel, Authorize: AuthJWT=Depends()):
    db_user = session.query(User).filter(User.username==user.username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Verify if the entered password matches the stored hashed password
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # If credentials are valid, create and return the JWT token
    access_token = Authorize.create_access_token(subject=db_user.username)

    # Generate the refresh token (with a longer expiry time)
    refresh_token = Authorize.create_refresh_token(subject=db_user.username)

    response = {
        "access":access_token,
        "refresh":refresh_token
    }
    return  response

#refreshing tokens
@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="PLease provide a valid refresh token")

    current_user = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=current_user)
    response = {
        "access": access_token,
    }
    return response