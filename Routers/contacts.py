from fastapi import Depends, HTTPException, APIRouter
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from models import Contacts
from database import sessionlocal
from pydantic import BaseModel, Field
from .auth import get_current_user

router=APIRouter(
    prefix='/contact',
    tags=['contacts']
)

class CreateContactRequest(BaseModel):
    first_name: str=Field(min_length=4)
    last_name: Optional[str]=Field(min_length=4)
    email: Optional[str]=Field(min_length=4)
    mobile_number: int=Field()
    profile_image: Optional[str]=Field(min_length=4)
    group: Optional[str]=Field()
    is_favourite:Optional[bool]=Field(default=False)

class EditContactRequest(BaseModel):
    first_name: Optional[str]=Field(min_length=4)
    last_name: Optional[str]=Field(min_length=4)
    email: Optional[str]=Field(min_length=4)
    mobile_number: Optional[int]=Field()
    profile_image: Optional[str]=Field(min_length=4)
    group: Optional[str]=Field()
    is_favourite:Optional[bool]=Field(default=False)

def get_db():
    db=sessionlocal()
    try:
        yield db 
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(get_db)]
user_dependency=Annotated[dict, Depends(get_current_user)]

@router.get("/getallcontacts")
async def getAllContacts(db:db_dependency, user:user_dependency):
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    return db.query(Contacts).filter(Contacts.user_id==user.get('id')).all()

@router.post("/createcontact")
async def createContact(db:db_dependency, user:user_dependency, contactrequest:CreateContactRequest):
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    model=Contacts(**contactrequest.model_dump(), user_id= user.get('id'), is_active=True)

    db.add(model)
    db.commit()

@router.put("/editcontact")
async def editContact(db:db_dependency, user:user_dependency, id:int, contactrequest:EditContactRequest):
        if user is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        is_contact_exist=db.query(Contacts).filter(user.get('id')==Contacts.user_id).filter(id==Contacts.id).first()

        if is_contact_exist is not None:
            model=Contacts(**contactrequest.model_dump())
            db.add(model)
            db.commit()
        else:
            raise HTTPException(status_code=404, detail='ID Not Found')

@router.delete("/deletecontact")   
async def deleteContact(db:db_dependency, user:user_dependency, id:int):
        if user is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        
        db.query(Contacts).filter(user.get('id')==Contacts.user_id).filter(id==Contacts.id).delete()

        return "Deleted Successfully"
