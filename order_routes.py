from http.client import responses

from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException
from sqlalchemy.sql.functions import current_user
from database import sessionmaker, Session, engine
from models import User, Order
from schemas import OrderModel

order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

session = Session(bind=engine)

@order_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid Token"
        )

    return {"message": "Hellow World"}

@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user).first()
    new_order = Order(
        pizza_size =  order.pizza_size,
        quantity= order.quantity
    )
    new_order.user=user
    session.add(new_order)
    session.commit()

    response = {
        "pizza_size":new_order.pizza_size,
        "quantity": new_order.quantity,
        "id":new_order.id,
        "order_status":new_order.order_status
    }
    return response