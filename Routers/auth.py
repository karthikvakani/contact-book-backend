from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users
from database import sessionlocal
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router=APIRouter(
    prefix='/users',
    tags=['auth']
)

SECREAT="KARTHIK"
ALGORITHM="HS256"

bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='users/token')

class UserSignin(BaseModel):
    email: str=EmailStr
    first_name:str=Field(min_length=1)
    last_name:str=Field(min_length=1)
    password:str=Field()

class userLogin(BaseModel):
    email: str=EmailStr
    password: str=Field()

class TokenModel(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db=sessionlocal()
    try:
        yield db 
    finally:
        db.close()

async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token,SECREAT, algorithms=[ALGORITHM] )
        email: str=payload.get('sub')
        user_id: int=payload.get('id')

        if email is None or user_id is None:
            raise HTTPException(status_code=404, detail='User Not found')
        
        return {'email':email, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="USER Not Found")

db_dependency=Annotated[Session, Depends(get_db)]
user_dependency=Annotated[dict, Depends(get_current_user)]


def authenticate_user(email: str, password: str, db: db_dependency):
    user=db.query(Users).filter(email==Users.email).first()

    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def createAccessToken(email:str, user_id:int, expireddelta:timedelta):
    encode={'sub':email, 'id': user_id}
    # expires=datetime.now(timezone.utc)+expireddelta
    # encode.update({'exp':expires})
    return jwt.encode(encode, SECREAT,algorithm=ALGORITHM)

@router.post('/token')
async def login_for_access_token(form_data:userLogin,
                                 db: db_dependency
                                 ):
    user=authenticate_user(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Check the Email Id and Password")

    token=createAccessToken(user.email, user.id, timedelta(minutes=20))
    
    return {
        'access_token': token,
        'token_type':'bearer'
    }

@router.get("/read_all")
def readAll(db: db_dependency):
    return db.query(Users).all()

@router.get("/getuser")
async def getUserDetails(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=404, detail="token is not valid")
    id=user.get('id')
    user_details=db.query(Users).filter(Users.id==id).first()
    return {
        'email':user_details.email,
        'first_name': user_details.first_name,
        'last_name': user_details.last_name,
        'is_active': user_details.is_active,
        'id': user_details.id,
        'profile_image': user_details.profile_image
    }

@router.post("/createuser")
def createUser(userdetails:UserSignin, db:db_dependency):
    
    email_exist=db.query(Users).filter(Users.email==userdetails.email).first()

    if(not(email_exist)):
            usermodel=Users(email=userdetails.email, 
                    first_name=userdetails.first_name, 
                    last_name=userdetails.last_name, 
                     hashed_password=bcrypt_context.hash(userdetails.password),
                       is_active=True)
            db.add(usermodel)
            db.commit()

            return "User Created Successfully"
    else:
            raise HTTPException(status_code=401, detail="Email already exist")
    