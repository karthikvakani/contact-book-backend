from fastapi import Depends, HTTPException, APIRouter, Body, Query
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from models import Contacts
from database import sessionlocal
from pydantic import BaseModel, Field
from datetime import date
from .auth import get_current_user
from sqlalchemy import asc, desc



router=APIRouter(
    prefix='/contact',
    tags=['contacts']
)

class CreateContactRequest(BaseModel):
    first_name: str=Field()
    last_name: Optional[str]=Field()
    email: str=Field(min_length=4)
    mobile_number: int=Field()
    profile_image: Optional[str]=Field(default=None)
    group: Optional[str]=Field(default=None)
    is_favourite:Optional[bool]=Field(default=False)
    birthday:Optional[date]= Field(default=None)
    address:Optional[str]=Field(default=None)

class EditContactRequest(BaseModel):
    first_name: Optional[str]=Field(default=None)
    last_name: Optional[str]=Field(default=None)
    email: Optional[str]=Field(default=None,min_length=4)
    mobile_number: Optional[int]=Field(default=None)
    profile_image: Optional[str]=Field(default=None,min_length=4)
    group: Optional[str]=Field(default=None)
    is_favourite:Optional[bool]=Field(default=False)
    address:Optional[str]=Field(default=None)
    birthday:Optional[date]= Field(default=None)
    id:int=Field()

def get_db():
    db=sessionlocal()
    try:
        yield db 
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(get_db)]
user_dependency=Annotated[dict, Depends(get_current_user)]

# @router.get("/getallcontacts")
# async def getAllContacts(db:db_dependency, user:user_dependency, search: str="", page: int=1):
#     if user is None:
#         raise HTTPException(status_code=404, detail="User Not Found")
#     query = db.query(Contacts).filter(Contacts.user_id==user.get('id'))
#     if search:
#         query = query.filter(Contacts.first_name.ilike(f"%{search}%"))
#     contacts = query.offset((page - 1) * 10).limit(10).all()
#     return contacts



@router.get("/getallcontacts")
async def getAllContacts(
    db: db_dependency,
    user: user_dependency,
    search: str = "",
    page: int = 1,
    sort_by: str = Query("first_name", enum=["first_name", "last_name", "email", "mobile_number"]),
    order: str = Query("asc", enum=["asc", "desc"]),
    type: str = Query(None, enum=["favourites", "grouped", None])
):
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    base_query = db.query(Contacts).filter(Contacts.user_id == user.get("id"))

    # Count all contacts for the user (without filters)
    total_all = base_query.count()
    total_favourites = base_query.filter(Contacts.is_favourite == True).count()
    total_grouped = base_query.filter(Contacts.group.isnot(None)).filter(Contacts.group != "").count()

    # Apply filters based on `type` param
    query = db.query(Contacts).filter(Contacts.user_id == user.get("id"))

    if type == "favourites":
        query = query.filter(Contacts.is_favourite == True)
    elif type == "grouped":
        query = query.filter(Contacts.group.isnot(None)).filter(Contacts.group != "")

    # Search filter
    if search:
        query = query.filter(Contacts.first_name.ilike(f"%{search}%"))

    # Sorting
    sort_column = getattr(Contacts, sort_by)
    query = query.order_by(asc(sort_column) if order == "asc" else desc(sort_column))

    # Final paginated data
    total_filtered = query.count()
    contacts = query.offset((page - 1) * 9).limit(9).all()

    return {
        "contacts": contacts,
        "all_counts": {
            "total_contacts": total_all,
            "favourite_contacts": total_favourites,
            "grouped_contacts": total_grouped
        }
    }





@router.post("/createcontact")
async def createContact(db:db_dependency, user:user_dependency, contactrequest:CreateContactRequest):
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    model=Contacts(**contactrequest.model_dump(), user_id= user.get('id'), is_active=True)

    db.add(model)
    db.commit()
    return "User Created Successfully"

@router.put("/editcontact")
async def editContact(db:db_dependency, user:user_dependency, contactrequest:EditContactRequest):
        if user is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        is_contact_exist=db.query(Contacts).filter(user.get('id')==Contacts.user_id).filter(contactrequest.id==Contacts.id).first()

        if is_contact_exist is not None:
            update_data = contactrequest.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(is_contact_exist, key, value)

            db.commit()
            return "edited Successfully"
        else:
            raise HTTPException(status_code=404, detail='ID Not Found')

@router.delete("/deletecontact")   
async def deleteContact(id:int, db:db_dependency, user:user_dependency):
        if user is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        
        db.query(Contacts).filter(user.get('id')==Contacts.user_id).filter(id==Contacts.id).delete()
        db.commit()

        return "Deleted Successfully"
