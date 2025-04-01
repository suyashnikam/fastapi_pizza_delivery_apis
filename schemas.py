from pydantic import BaseModel, validator
from typing import Optional,List

class SignUpModel(BaseModel):
    username:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example':{
                "username":"suyashnikam",
                "email":"suyashnikam1998@gmail.com",
                "password":"password",
                "is_staff": False,
                "is_active":True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key:str = 'authjwt_secret_key'

class LoginModel(BaseModel):
    username:str
    password: str

class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str]="PENDING"
    pizza_size: Optional[str]="SMALL"
    user_id: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example":{
                "quantity":2,
                "pizza_size": "LARGE"
            }
        }