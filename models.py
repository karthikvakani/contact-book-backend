from database import base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Users(base):
    __tablename__='users'

    id=Column(Integer, primary_key=True, index=True)
    first_name: str= Column(String)
    last_name: str=Column(String)
    email: str=Column(String)
    hashed_password=Column(String)
    mobile_number: int=Column(Integer, unique=True)
    profile_image=Column(String)
    is_active=Column(Boolean)

