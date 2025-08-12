from fastapi import FastAPI
import models
from database import engine
from Routers import auth
from Routers import contacts
from fastapi.middleware.cors import CORSMiddleware



app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(contacts.router)
