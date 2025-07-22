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

class Contacts(base):
    __tablename__='contacts'

    id=Column(Integer, primary_key=True, index=True)
    first_name: str=Column(String)
    last_name: str=Column(String)
    email: str=Column(String)
    mobile_number: int=Column(Integer)
    profile_image: int=Column(Integer)
    group: str=Column(String)
    is_favourite:bool=Column(Boolean)
    is_active:bool=Column(Boolean)
    user_id: int=Column(Integer, ForeignKey("users.id"))

