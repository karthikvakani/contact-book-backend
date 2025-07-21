from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users
from database import sessionlocal
from pydantic import BaseModel, Field
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
    email:str=Field(min_length=5)
    username:str=Field(min_length=1)
    first_name:str=Field(min_length=1)
    last_name:str=Field(min_length=1)
    password:str=Field()
    mobile_number:str=Field()
    is_active:str=True

class userLogin(BaseModel):
    email: str=Field(min_length=5)
    password: str=Field(min_length=5)

class TokenModel(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db=sessionlocal()
    try:
        yield db 
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(get_db)]

def authenticate_user(email: str, password: str, db: db_dependency):
    user=db.query(Users).filter(email==Users.email).first()

    if user is None:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

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


def createAccessToken(email:str, user_id:int, expireddelta:timedelta):
    encode={'sub':email, 'id': user_id}
    expires=datetime.now(timezone.utc)+expireddelta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECREAT,algorithm=ALGORITHM)

@router.get("/read_all")
def readAll(db: db_dependency):

    return db.query(Users).all()


@router.post("/createuser")
def createUser(userdetails:UserSignin, db:db_dependency):
    
    email_exist=db.query(Users).filter(Users.email==userdetails.email).first()
    mobile_number_exist=db.query(Users).filter(Users.mobile_number==userdetails.mobile_number).first()

    if(not(email_exist and mobile_number_exist)):
            usermodel=Users(email=userdetails.email, 
                    first_name=userdetails.first_name, 
                    last_name=userdetails.last_name, 
                     hashed_password=bcrypt_context.hash(userdetails.password),
                     mobile_number=userdetails.mobile_number,
                       is_active=True)
            db.add(usermodel)
            db.commit()

            return "User Created Successfully"
    else:
        if(email_exist and mobile_number_exist):
            return "Email ID and Mobile Number are already Exists"
        elif(email_exist and not mobile_number_exist):
            return "Email Id is already Exist"
        elif(mobile_number_exist and not email_exist):
            return "Email Id is already Exist"

@router.post('/token')
async def login_for_access_token(form_data:userLogin,
                                 db: db_dependency
                                 ):
    user=authenticate_user(form_data.email, form_data.password, db)
    if not user:
        return 'Check the Email Id and Password'

    token=createAccessToken(user.email, user.id, timedelta(minutes=20))
    
    return {
        'access_token': token,
        'token_type':'bearer'
    }
    